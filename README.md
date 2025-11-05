# 🏃‍♂️ Garmin Health Metrics API

A lightweight Flask API to fetch your personal Garmin Connect health and wellness data — including **steps, active minutes, resting heart rate, stress level, recovery time, Body Battery, HRV sleep score, and sleep coach feedback**.

> 🔐 **Secure by design**: Uses token-based authentication (no credentials stored in code).  
> 📅 **Historical support**: Retrieve data up to 1 year back (core metrics only).  
> 🚀 **Personal use only**: Built for self-hosting on your own VPS or local machine.

---

## 📦 Features

- ✅ **Steps** (`totalSteps`)
- ✅ **Active Minutes** (moderate + vigorous activity)
- ✅ **Resting Heart Rate**
- ✅ **Average Stress Level**
- ✅ **Recovery Time** (from latest activity)
- ✅ **Body Battery** (end-of-day value)
- ✅ **HRV Sleep Score** (recent days only)
- ✅ **Sleep Coach Feedback** (human-readable insights)
- 📅 Supports historical dates via `?date=YYYY-MM-DD`
- 🔐 Secure token-based auth (with MFA support)

---

## 🛠️ Requirements

- Python 3.8+
- A **Garmin Connect account** (with 2FA enabled recommended)
- A VPS or local machine for self-hosting
- `git`, `python3`, `pip`

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/your-username/garmin-health-api.git
cd garmin-health-api
```

### 2. Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Authenticate with Garmin (one-time setup)
```bash
python login_cli.py
```
- Enter your **Garmin email and password**
- Complete **MFA** if prompted
- Tokens are saved securely to `~/.garminconnect/` (never in the repo!)

> 💡 Tokens persist across sessions — you only need to run this once (or when expired).

### 4. Start the API
```bash
python app.py
```
By default, the server runs at `http://localhost:5000`.

### 5. Fetch your data
```bash
# Get yesterday's metrics (recommended for sleep/HRV)
curl http://localhost:5000/health-metrics

# Get historical data (core metrics only)
curl "http://localhost:5000/health-metrics?date=2025-10-10"
```

**Example response:**
```json
{
  "date": "2025-10-10",
  "steps": 7979,
  "active_minutes": 110,
  "resting_heart_rate": 59,
  "stress_level": 27,
  "recovery_time_minutes": 42,
  "body_battery": 40,
  "hrv_sleep_score": 85,
  "sleep_coach_feedback": "Great recovery during sleep"
}
```

---

## 🖥️ Deploy to VPS (Production)

For personal production use on a VPS (e.g., DigitalOcean, Hetzner):

### 1. Clone and set up (as above)
### 2. Create a systemd service
```bash
sudo nano /etc/systemd/system/garmin-api.service
```
Paste the [service config from the deployment guide](#-deployment-guide) (included in full below).

### 3. Use Nginx as reverse proxy (optional but recommended)
- Install Nginx
- Configure proxy to `http://127.0.0.1:5000`
- Add basic auth or IP whitelisting for security

### 4. Enable auto-start
```bash
sudo systemctl enable --now garmin-api
```

> 🔒 **Security note**: Always run behind a firewall or Nginx. Never expose Flask directly to the internet.

---

## 🔒 Security

- **No credentials in code**: Authentication uses saved tokens only.
- **Tokens stored locally**: In `~/.garminconnect/` (outside the project directory).
- **GitHub-safe**: `.gitignore` blocks all sensitive files.
- **VPS-hardened**: Use firewall rules or basic auth to restrict access.

> ⚠️ **This is for personal use only**. Do not expose this API publicly.

---

## 📁 Project Structure

```
.
├── app.py                # Main Flask API
├── garmin_auth.py        # Authentication logic (token + MFA)
├── login_cli.py          # One-time CLI login script
├── requirements.txt      # Python dependencies
├── .gitignore            # Excludes tokens and secrets
└── README.md             # You are here!
```

---

## ⚠️ Limitations

- **HRV Sleep Score & Sleep Coach** only available for the **last 7 days** (Garmin API limitation).
- **Recovery Time** comes from your most recent activity (not date-specific).
- **Endurance Score** and **Hill Score** are not exposed by Garmin’s API.
- Historical data beyond 1 year may not be available.

---

## 🤝 Disclaimer

This project uses the **unofficial [`garminconnect`](https://github.com/cyberjunky/python-garminconnect) Python library**.  
Garmin does not provide a public health API — use at your own risk.  
This tool is **not affiliated with Garmin International**.

> 📜 **Respect Garmin’s ToS**: Avoid excessive requests. Cache data when possible.

---

## 🙌 Credits

- [cyberjunky/python-garminconnect](https://github.com/cyberjunky/python-garminconnect) — Unofficial Garmin API client
- [Garth](https://github.com/matin/garth) — Authentication layer used by `garminconnect`

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

> 💡 **Tip**: Pair this API with [Home Assistant](https://www.home-assistant.io/), [Grafana](https://grafana.com/), or a custom dashboard to visualize your health trends!
