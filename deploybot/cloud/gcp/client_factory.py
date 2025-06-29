from .credentials import get_credentials
from google.cloud import service_usage_v1
from googleapiclient import discovery
from google.cloud import storage
from google.cloud.devtools import cloudbuild_v1
from google.cloud import run_v2

class GCPClientFactory:
    def __init__(self):
        self.credentials = get_credentials()
        
    def get_service_usage_client(self) -> service_usage_v1.ServiceUsageClient:
        return service_usage_v1.ServiceUsageClient(credentials=self.credentials)
        
    def get_sql_admin_client(self) -> discovery.Resource:
        return discovery.build('sqladmin', 'v1beta4', credentials=self.credentials)

    def get_storage_client(self) -> storage.Client:
        return storage.Client(credentials=self.credentials)

    def get_cloud_build_client(self) -> cloudbuild_v1.CloudBuildClient:
        return cloudbuild_v1.CloudBuildClient(credentials=self.credentials)

    def get_cloud_run_client(self) -> run_v2.ServicesClient:
        return run_v2.ServicesClient(credentials=self.credentials)
