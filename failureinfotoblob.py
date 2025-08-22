import csv
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta, datetime



# Config
log_analytics_workspace_id = "<Log analytics ID>"
account_name = "<Storage account name>"
account_key = "<Storage account key>"
container_name = "<Storage container name>"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"filename-failure_{timestamp}.csv"

# Authenticate
credential = DefaultAzureCredential()
client = LogsQueryClient(credential)
# KQL query to get detailed failures
query = """
AppRequests
| extend trimmedRoleName = trim(" ", AppRoleName)
| where (ResultCode startswith "4" or ResultCode startswith "5")
  and trimmedRoleName == "<App Service name>"
  and TimeGenerated >= ago(24h)
| project TimeGenerated, ResultCode, AppRoleName, Url, ClientIP
| order by TimeGenerated desc
"""
# Run query for last 1 hour
response = client.query_workspace(
    workspace_id=log_analytics_workspace_id,
    query=query,
    timespan=timedelta(hours=1)
)
# Save to CSV
if response.tables:
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([col for col in response.tables[0].columns])
        for row in response.tables[0].rows:
            writer.writerow(row)
    print(f"Saved query results to '{filename}'.")
else:
    print("No data returned from query.")

# Upload to Blob
blob_server_client = BlobServiceClient(
    f"https://<endpoint>.blob.core.windows.net/",
    credential=account_key
)
container_client = blob_server_client.get_container_client(container_name)

try: 
    container_client.create.container()
except Exception:
    pass

with open(filename, "rb") as data:
    container_client.upload_blob(name=filename, data=data, overwrite=True)

print(f"Uploaded '{filename}' to blob container '{container_name}'.")