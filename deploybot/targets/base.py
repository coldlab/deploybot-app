from abc import ABC, abstractmethod
from typing import Dict, Any

from deploybot.core.stack import Stack
from deploybot.core.enums import Provisioner

class BaseTarget(ABC):
    """Base class for all deployment targets."""
    
    def __init__(self, name: str, config: Dict[str, Any], provisioner: Provisioner):
        self.name = name
        self.config = config
        self.provisioner = provisioner
    
    @abstractmethod
    def validate_credentials(self) -> None:
        """Validate target credentials and permissions."""
        pass
    
    @abstractmethod
    def get_provisioner(self, stack_obj: Stack) -> Any:
        """Get the appropriate provisioner for this target."""
        pass 