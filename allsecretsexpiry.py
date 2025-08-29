from datetime import datetime, timezone, timedelta
from azure.identity import DefaultAzureCredential
import requests

# This script is an extension to the secretsexpiry.py script and takes into account Secrets that are stored in MS Entra App registrations
# Microsoft Graph base URL
GRAPH_API = "https://graph.microsoft.com/v1.0"

# Authenticate with DefaultAzureCredential (needs proper Graph API permissions)
credential = DefaultAzureCredential()
token = credential.get_token("https://graph.microsoft.com/.default")
headers = {"Authorization": f"Bearer {token.token}"}

# Expiry threshold
expiry_threshold_days = 30
now = datetime.now(timezone.utc)

print(f"\nChecking Entra ID App Registration secrets expiring in {expiry_threshold_days} days:\n")

# Get all applications
apps = requests.get(f"{GRAPH_API}/applications", headers=headers).json()

for app in apps.get("value", []):
    app_name = app.get("displayName")
    app_id = app.get("appId")

    # Check passwordCredentials (client secrets)
    for secret in app.get("passwordCredentials", []):
        end_date = datetime.fromisoformat(secret["endDateTime"].replace("Z", "+00:00"))
        days_left = (end_date - now).days

        if 0 <= days_left <= expiry_threshold_days:
            print(f"- App: {app_name} ({app_id}) | Secret ID: {secret['keyId']} expires in {days_left} days on {end_date.date()}")
        elif days_left < 0:
            print(f"- App: {app_name} ({app_id}) | Secret ID: {secret['keyId']} already expired on {end_date.date()}")

    # Check keyCredentials (certificates)
    for cert in app.get("keyCredentials", []):
        end_date = datetime.fromisoformat(cert["endDateTime"].replace("Z", "+00:00"))
        days_left = (end_date - now).days

        if 0 <= days_left <= expiry_threshold_days:
            print(f"- App: {app_name} ({app_id}) | Certificate ID: {cert['keyId']} expires in {days_left} days on {end_date.date()}")
        elif days_left < 0:
            print(f"- App: {app_name} ({app_id}) | Certificate ID: {cert['keyId']} already expired on {end_date.date()}")