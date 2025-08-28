from datetime import datetime, timezone, timedelta
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
# Replace with your Key Vault URL
key_vault_url = "<key vault URL>"
# Authenticate using DefaultAzureCredential (make sure your environment is set up)
credential = DefaultAzureCredential()
# Create a SecretClient
client = SecretClient(vault_url=key_vault_url, credential=credential)
# Define threshold to report secrets expiring within this many days
expiry_threshold_days = 30
now = datetime.now(timezone.utc)
print(f"Secrets expiring within {expiry_threshold_days} days:")
# List all secrets
for secret_props in client.list_properties_of_secrets():
    # Fetch full secret to access attributes like expiry date
    secret = client.get_secret(secret_props.name)
    expires_on = secret.properties.expires_on
    if expires_on:
        days_to_expiry = (expires_on - now).days
        if 0 <= days_to_expiry <= expiry_threshold_days:
            print(f"- Secret: {secret.name}, Expires on: {expires_on.date()}, Days left: {days_to_expiry}")
        elif days_to_expiry < 0:
            print(f"- Secret: {secret.name} has already expired on {expires_on.date()}")
    else:
        print(f"- Secret: {secret.name} does not have an expiration date set")