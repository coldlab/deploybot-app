from .client_factory import GCPClientFactory
from google.cloud import service_usage_v1
from .enums.services import GoogleCloudService

class GCPServiceUsage:
    def __init__(self) -> None:
        self.client = GCPClientFactory().get_service_usage_client()
        
    def enable_api(self, project_id: str, api_name: GoogleCloudService) -> service_usage_v1.EnableServiceResponse:
        name = f"projects/{project_id}/services/{api_name.value}"
        try:
            request = service_usage_v1.EnableServiceRequest(
                name=name
            )
            operation = self.client.enable_service(request)
            return operation.result()
        except Exception as e:
            print(f"Error enabling API {api_name}: {e}")
        
    def disable_api(self, project_id: str, api_name: GoogleCloudService) -> service_usage_v1.DisableServiceResponse:
        name = f"projects/{project_id}/services/{api_name.value}"
        try:
            request = service_usage_v1.DisableServiceRequest(
                name=name
            )
            operation = self.client.disable_service(request)
            return operation.result()
        except Exception as e:
            print(f"Error disabling API {api_name}: {e}")

    def get_api(self, project_id: str, api_name: GoogleCloudService) -> service_usage_v1.Service:
        name = f"projects/{project_id}/services/{api_name.value}"
        try:
            request = service_usage_v1.GetServiceRequest(
                name=name
            )
            return self.client.get_service(request)
        except Exception as e:
            print(f"Error getting API {api_name}: {e}")