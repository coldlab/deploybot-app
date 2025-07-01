from deploybot.cloud.gcp.service_usage import GCPServiceUsage
from deploybot.cloud.gcp.enums.services import GoogleCloudService
from google.cloud import service_usage_v1

class GCPServiceUsageService:
    def __init__(self):
        self.service_usage = GCPServiceUsage()

    def enable_api(self, project_id: str, api_name: GoogleCloudService):
        api = self.service_usage.get_api(project_id, api_name)
        if api.state == service_usage_v1.State.ENABLED:
            return
        print(f"Enabling API {api_name} for project {project_id}")
        self.service_usage.enable_api(project_id, api_name)
