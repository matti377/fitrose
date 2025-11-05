# garmin_auth.py
import os
import sys
from pathlib import Path
from getpass import getpass
import requests
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
)
from garth.exc import GarthHTTPError, GarthException


def get_credentials():
    email = input("Enter Garmin email: ").strip()
    password = getpass("Enter Garmin password: ")
    return email, password


def init_api() -> Garmin | None:
    """Initialize Garmin API with authentication and token management."""

    tokenstore = os.getenv("GARMINTOKENS", "~/.garminconnect")
    tokenstore_path = Path(tokenstore).expanduser()

    print(f"🔐 Token storage: {tokenstore_path}")

    # Check if token files exist
    if tokenstore_path.exists():
        print("📄 Found existing token directory")
        token_files = list(tokenstore_path.glob("*.json"))
        if token_files:
            print(f"🔑 Found {len(token_files)} token file(s): {[f.name for f in token_files]}")
        else:
            print("⚠️ Token directory exists but no token files found")
    else:
        print("📭 No existing token directory found")

    # First try to login with stored tokens
    try:
        print("🔄 Attempting to use saved authentication tokens...")
        garmin = Garmin()
        garmin.login(str(tokenstore_path))
        print("✅ Successfully logged in using saved tokens!")
        return garmin

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError, GarminConnectConnectionError):
        print("🔑 No valid tokens found. Requesting fresh login credentials.")

    # Loop for credential entry with retry on auth failure
    while True:
        try:
            email, password = get_credentials()
            print("🔒 Logging in with credentials...")
            garmin = Garmin(email=email, password=password, is_cn=False, return_on_mfa=True)
            result1, result2 = garmin.login()

            if result1 == "needs_mfa":
                print("🔐 Multi-factor authentication required")
                mfa_code = input("Please enter your MFA code: ")
                print("🔄 Submitting MFA code...")

                try:
                    garmin.resume_login(result2, mfa_code)
                    print("✅ MFA authentication successful!")
                except (GarthHTTPError, GarthException) as e:
                    error_str = str(e)
                    if "429" in error_str and "Too Many Requests" in error_str:
                        print("❌ Too many MFA attempts. Wait 30 minutes.")
                        sys.exit(1)
                    elif "401" in error_str or "403" in error_str:
                        print("❌ Invalid MFA code. Try again.")
                        continue
                    else:
                        print(f"❌ MFA failed: {e}")
                        sys.exit(1)

            # Save tokens
            garmin.garth.dump(str(tokenstore_path))
            print(f"💾 Tokens saved to: {tokenstore_path}")
            print("✅ Login successful!")
            return garmin

        except GarminConnectAuthenticationError:
            print("❌ Auth failed. Check email/password.")
            continue
        except (FileNotFoundError, GarthHTTPError, GarminConnectConnectionError, requests.exceptions.HTTPError) as err:
            print(f"❌ Connection error: {err}")
            return None
        except KeyboardInterrupt:
            print("\n👋 Cancelled.")
            return None