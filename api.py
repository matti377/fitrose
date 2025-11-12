# app.py
import hmac
from flask import Flask, jsonify, request
import os
from pathlib import Path
from datetime import datetime, timedelta
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
)
from garth.exc import GarthHTTPError
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_garmin_client():
    tokenstore = os.getenv("GARMINTOKENS", "~/.garminconnect")
    tokenstore_path = Path(tokenstore).expanduser()

    if not tokenstore_path.exists() or not any(tokenstore_path.glob("*.json")):
        raise GarminConnectAuthenticationError("No saved tokens found. Run `python login_cli.py` first.")

    try:
        garmin = Garmin()
        garmin.login(str(tokenstore_path))
        return garmin
    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError, GarminConnectConnectionError) as e:
        raise GarminConnectAuthenticationError(f"Token login failed: {e}. Re-run CLI login.")

@app.route('/health-metrics', methods=['GET'])
def get_health_metrics():
    try:
        client = get_garmin_client()
        
        # Get date from query param or default to yesterday
        date_str = request.args.get('date')
        if date_str:
            target_date = date_str
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        else:
            target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            
        # Test if apikey matches
        apiKey_str = request.args.get('key')
        expected_key = "YOURAPIKEYHERE"  # Replace with your actual API key
        if(apiKey_str != expected_key):
            return jsonify({"error": "The API KEY is incorrect"}), 401
        


        # Fetch comprehensive daily summary
        user_summary = client.get_user_summary(target_date)
        if not isinstance(user_summary, dict):
            return jsonify({"error": f"No data found for {target_date}"}), 404

        # --- Core metrics from user_summary ---
        steps = user_summary.get("totalSteps") or 0
        active_seconds = (user_summary.get("activeSeconds") or 0) + (user_summary.get("highlyActiveSeconds") or 0)
        active_minutes = active_seconds // 60
        resting_heart_rate = user_summary.get("restingHeartRate") or 0
        stress_level = user_summary.get("averageStressLevel") or 0

        # --- Body Battery (most recent value) ---
        body_battery = user_summary.get("bodyBatteryMostRecentValue") or 0

        # --- Recovery Time (from latest activity) ---
        recovery_time = 0
        try:
            activities = client.get_activities(0, 1)
            if activities:
                recovery_time = activities[0].get("recoveryTime") or 0
        except Exception as e:
            app.logger.warning(f"Recovery time fetch failed: {e}")

        # --- HRV Sleep Score & Sleep Coach (only for recent dates ≤7 days) ---
        hrv_sleep_score = 0
        sleep_coach_feedback = "N/A"
        
        try:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
            if (datetime.now().date() - date_obj).days <= 7:
                sleep_data = client.get_sleep_data(target_date)
                if sleep_:
                    # HRV Sleep Score (if available)
                    hrv_status = sleep_data.get("sleepScores", {}).get("hrvStatus", {})
                    hrv_sleep_score = hrv_status.get("score", 0)
                    
                    # Sleep Coach Feedback (from Body Battery event)
                    feedback_event = user_summary.get("endOfDayBodyBatteryDynamicFeedbackEvent")
                    if feedback_event:
                        # Map Garmin's internal codes to readable text
                        feedback_map = {
                            "SLEEP_TIME_PASSED_RECOVERING_AND_INACTIVE": "Great recovery during sleep",
                            "SLEEP_PREPARATION_RECOVERING_AND_INACTIVE": "Optimal conditions for recovery",
                            "POOR_SLEEP_RECOVERY": "Poor sleep recovery",
                            "LOW_BODY_BATTERY_AT_WAKE_TIME": "Low energy upon waking",
                        }
                        event_type = feedback_event.get("feedbackLongType")
                        sleep_coach_feedback = feedback_map.get(event_type, event_type or "N/A")
        except Exception as e:
            app.logger.warning(f"Sleep/HRV fetch failed: {e}")

        return jsonify({
            "date": target_date,
            "steps": int(steps),
            "active_minutes": int(active_minutes),
            "resting_heart_rate": int(resting_heart_rate),
            "stress_level": int(stress_level),
            #"recovery_time_minutes": int(recovery_time),
            "body_battery_end_of_day": int(body_battery),
            #"hrv_sleep_score": int(hrv_sleep_score),
            "sleep_coach_feedback": str(sleep_coach_feedback)
        })

    except GarminConnectAuthenticationError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)