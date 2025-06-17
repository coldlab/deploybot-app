from typing import Dict, Any
import os
from google.cloud import storage
import google.auth

from deploybot.core.enums import Target
from deploybot.core.stack import Stack
from deploybot.provisioners.terraform import TerraformProvisioner
from .base import BaseTarget
from ..provisioners.terraform_factory import TerraformFactory

class GCPTarget(BaseTarget):
    """GCP deployment target implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(name=Target.GCP.value, config=config)
        self.project_id = config.get('project_id')
        self.region = config.get('region', 'us-central1')
        self.zone = config.get('zone', 'us-central1-a')
        
        # Initialize credentials using Application Default Credentials
        self._init_credentials()
        
        # Validate required configuration
        if not self.project_id:
            raise ValueError("GCP project_id is required")
    
    def _init_credentials(self) -> None:
        """Initialize GCP credentials using Application Default Credentials."""
        try:
            self.credentials, self.default_project = google.auth.default()
            
            if not self.project_id and self.default_project:
                self.project_id = self.default_project

        except Exception as e:
            raise Exception(
                f"Failed to load GCP Application Default Credentials: {str(e)}. "
                "Please ensure you've run 'gcloud auth application-default login' "
                "and set the GCP_PROJECT_ID environment variable or pass it via --project-id."
            )
    
    def validate_credentials(self) -> None:
        """Validate GCP credentials and permissions."""
        try:
            # Try to access GCS as a simple permission check
            storage_client = storage.Client(
                credentials=self.credentials,
                project=self.project_id
            )
            # Make a small API call to verify credentials
            storage_client.list_buckets(max_results=1)
        except Exception as e:
            raise Exception(f"Failed to validate GCP credentials: {str(e)}")
    
    def get_provisioner(self, stack_obj: Stack) -> TerraformProvisioner:
        return TerraformFactory.create(stack_obj, Target.GCP, self.config) 