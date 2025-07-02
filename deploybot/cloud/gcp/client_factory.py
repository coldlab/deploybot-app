from .credentials import get_credentials
from google.cloud import service_usage_v1
from googleapiclient import discovery
from google.cloud import storage
from google.cloud.devtools import cloudbuild_v1
from google.cloud import run_v2
from google.cloud import artifactregistry_v1
from deploybot.core.global_state import global_state_manager

class GCPClientFactory:
    """Factory for GCP clients using global state credentials."""
    
    _instance = None
    _clients = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GCPClientFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # No initialization needed - credentials come from global state
        pass
    
    def _get_credentials(self):
        """Get credentials from global state or fallback to direct loading."""
        credentials = global_state_manager.gcp_credentials
        if credentials is None:
            # Fallback to direct credential loading (for backward compatibility)
            credentials = get_credentials()
        return credentials
        
    def get_service_usage_client(self) -> service_usage_v1.ServiceUsageClient:
        if 'service_usage' not in self._clients:
            self._clients['service_usage'] = service_usage_v1.ServiceUsageClient(
                credentials=self._get_credentials()
            )
        return self._clients['service_usage']
        
    def get_sql_admin_client(self) -> discovery.Resource:
        if 'sql_admin' not in self._clients:
            self._clients['sql_admin'] = discovery.build(
                'sqladmin', 'v1beta4', 
                credentials=self._get_credentials()
            )
        return self._clients['sql_admin']

    def get_storage_client(self) -> storage.Client:
        if 'storage' not in self._clients:
            self._clients['storage'] = storage.Client(
                credentials=self._get_credentials()
            )
        return self._clients['storage']

    def get_cloud_build_client(self) -> cloudbuild_v1.CloudBuildClient:
        if 'cloud_build' not in self._clients:
            self._clients['cloud_build'] = cloudbuild_v1.CloudBuildClient(
                credentials=self._get_credentials()
            )
        return self._clients['cloud_build']

    def get_cloud_run_client(self) -> run_v2.ServicesClient:
        if 'cloud_run' not in self._clients:
            self._clients['cloud_run'] = run_v2.ServicesClient(
                credentials=self._get_credentials()
            )
        return self._clients['cloud_run']

    def get_artifact_registry_client(self) -> artifactregistry_v1.ArtifactRegistryClient:
        if 'artifact_registry' not in self._clients:
            self._clients['artifact_registry'] = artifactregistry_v1.ArtifactRegistryClient(
                credentials=self._get_credentials()
            )
        return self._clients['artifact_registry']
    
    def reset(self):
        """Reset all cached clients (useful for testing or credential rotation)."""
        self._clients.clear()
