from datetime import datetime, timedelta
from azure.storage.blob import (
    BlobServiceClient,
    generate_container_sas,
    ContainerSasPermissions,
)
# Azure Storage account info
account_name = "<storage account name>"
account_key = "<access key>"
container_name = "<container name>"
# Define SAS token expiry and permissions
sas_token_expiry = datetime.utcnow() + timedelta(hours=1)  # < token valid for number of hours set here
permissions = ContainerSasPermissions(read=True, write=True, list=True)  # customize permissions
# Generate SAS token for the container
sas_token = generate_container_sas(
    account_name=account_name,
    container_name=container_name,
    account_key=account_key,
    permission=permissions,
    expiry=sas_token_expiry,
)
print("SAS token for container:")
print(sas_token)
# You can construct a full URL with SAS token to access the container
container_url_with_sas = f"https://{account_name}.blob.core.windows.net/{container_name}?{sas_token}"
print("\nFull URL with SAS token:")
print(container_url_with_sas)