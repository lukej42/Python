from azure.identity import DefaultAzureCredential
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from datetime import datetime, timedelta
import statistics

# ===== CONFIGURATION =====
subscription_id = "<Azure Subscription ID>"
resource_group_name = "<Resource group name>"
app_service_plan_name = "<App Service Plan name"

# App Service Plan size options (ordered from smallest to largest)
sku_scale_sequence = ["B1", "B2", "B3"]  # Change this to match your needs

cpu_scale_up_threshold = 70  # %
cpu_scale_down_threshold = 30  # %

# Authenticate
credential = DefaultAzureCredential()
web_client = WebSiteManagementClient(credential, subscription_id)
monitor_client = MonitorManagementClient(credential, subscription_id)

def get_average_cpu(resource_id):
    """Fetch average CPU usage from Azure Monitor for last 5 minutes"""
    metrics_data = monitor_client.metrics.list(
        resource_id,
        timespan=f"{(datetime.utcnow() - timedelta(minutes=5)).isoformat()}/{datetime.utcnow().isoformat()}",
        interval="PT1M",
        metricnames="CpuPercentage",
        aggregation="Average"
    )

    cpu_values = []
    for item in metrics_data.value:
        for timeseries in item.timeseries:
            for data in timeseries.data:
                if data.average is not None:
                    cpu_values.append(data.average)

    return statistics.mean(cpu_values) if cpu_values else 0

def scale_app_service_plan(new_sku):
    """Scale the App Service Plan to a new size"""
    plan = web_client.app_service_plans.get(resource_group_name, app_service_plan_name)
    plan.sku.name = new_sku
    web_client.app_service_plans.begin_create_or_update(resource_group_name, app_service_plan_name, plan)
    print(f"Scaled plan to {new_sku}")

def main():
    plan = web_client.app_service_plans.get(resource_group_name, app_service_plan_name)
    resource_id = plan.id
    current_sku = plan.sku.name

    avg_cpu = get_average_cpu(resource_id)
    print(f"Average CPU: {avg_cpu:.2f}% | Current SKU: {current_sku}")

    index = sku_scale_sequence.index(current_sku)

    if avg_cpu > cpu_scale_up_threshold and index < len(sku_scale_sequence) - 1:
        scale_app_service_plan(sku_scale_sequence[index + 1])

    elif avg_cpu < cpu_scale_down_threshold and index > 0:
        scale_app_service_plan(sku_scale_sequence[index - 1])

    else:
        print("No scaling action needed.")

if __name__ == "__main__":
    main()