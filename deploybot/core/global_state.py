from typing import Optional
from google.auth.credentials import Credentials
import threading

class GlobalStateManager:
    """
    Global state manager for DeployBot.
    Manages shared resources like credentials across the deployment process.
    """
    
    def __init__(self):
        self._gcp_credentials: Optional[Credentials] = None
        self._gcp_project_id: Optional[str] = None
        self._lock = threading.Lock()

    @property
    def gcp_credentials(self) -> Optional[Credentials]:
        """Get GCP credentials if they have been set."""
        with self._lock:
            return self._gcp_credentials

    @gcp_credentials.setter
    def gcp_credentials(self, credentials: Credentials) -> None:
        """Set GCP credentials for the deployment session."""
        with self._lock:
            self._gcp_credentials = credentials

    @property
    def project_id(self) -> Optional[str]:
        """Get project ID if it has been set."""
        with self._lock:
            return self._gcp_project_id

    @project_id.setter 
    def project_id(self, project_id: str) -> None:
        """Set project ID for the deployment session."""
        with self._lock:
            self._gcp_project_id = project_id
        
    def reset(self) -> None:
        """Reset all global state (useful for testing)."""
        with self._lock:
            self._gcp_credentials = None
            self._gcp_project_id = None
    
    def is_initialized(self) -> bool:
        """Check if credentials have been initialized."""
        with self._lock:
            return self._gcp_credentials is not None

# Global instance
global_state_manager = GlobalStateManager() 