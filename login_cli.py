# login_cli.py
from garmin_auth import init_api

if __name__ == "__main__":
    print("🚀 Garmin Connect CLI Login")
    api = init_api()
    if api:
        print("🎉 Authentication complete! Tokens saved.")
    else:
        print("💥 Login failed.")
        exit(1)