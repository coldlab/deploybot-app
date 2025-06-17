from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProvisioner(ABC):
    """Base class for all provisioners."""
    
    def __init__(self, stack_path: str, config: Dict[str, Any]):
        self.stack_path = stack_path
        self.config = config
    
    @abstractmethod
    def validate(self) -> None:
        """Validate the provisioner configuration."""
        pass
    
    @abstractmethod
    def init(self) -> None:
        """Initialize the provisioner."""
        pass
    
    @abstractmethod
    def apply(self) -> Dict[str, Any]:
        """Apply the configuration and return deployment info."""
        pass
    
    @abstractmethod
    def destroy(self) -> None:
        """Destroy the provisioned resources."""
        pass 