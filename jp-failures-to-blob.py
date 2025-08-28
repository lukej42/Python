import csv
import io
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta, datetime

# ----------------------------
# Config
# ----------------------------
log_analytics_workspace_id = "<Log Analytics workspace ID>"
account_name = "<storage account name>"
account_key = "<access key>"
container_name = "<container name>"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"<file name>-failure_{timestamp}.csv"

# ----------------------------
# Authenticate
# ----------------------------
credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

# ----------------------------
# KQL query to get detailed failures
# ----------------------------
query = """
AppRequests
| extend trimmedRoleName = trim(" ", AppRoleName)
| where (ResultCode startswith "4" or ResultCode startswith "5")
  and trimmedRoleName == "<role name>"
  and TimeGenerated >= ago(24h)
| project TimeGenerated, ResultCode, AppRoleName, Url, ClientIP
| order by TimeGenerated desc
"""

# Run query for last 1 hour
response = client.query_workspace(
    workspace_id=log_analytics_workspace_id,
    query=query,
    timespan=timedelta(hours=24)
)

# ----------------------------
# Write CSV to in-memory buffer
# ----------------------------
if response.tables:
    output = io.StringIO()
    writer = csv.writer(output)
    # Write headers (columns are strings in this SDK version)
    writer.writerow(response.tables[0].columns)
    # Write rows
    for row in response.tables[0].rows:
        writer.writerow(row)
    csv_data = output.getvalue().encode("utf-8")  # convert to bytes for blob
    output.close()
else:
    print("No data returned from query.")
    csv_data = None

# ----------------------------
# Upload to Azure Blob
# ----------------------------
if csv_data:
    blob_service_client = BlobServiceClient(
        f"https://<storage account name>.blob.core.windows.net",
        credential=account_key
    )
    container_client = blob_service_client.get_container_client(container_name)
    
    # Create container if it doesn’t exist
    try:
        container_client.create_container()
    except Exception:
        pass

    # Upload CSV directly from memory
    container_client.upload_blob(name=filename, data=csv_data, overwrite=True)
    print(f"Uploaded '{filename}' to blob container '{container_name}'.")