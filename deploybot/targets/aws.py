from typing import Dict, Any
import boto3

from deploybot.core.enums import Target
from deploybot.core.stack import Stack
from deploybot.provisioners.terraform import TerraformProvisioner
from .base import BaseTarget
from ..provisioners.terraform_factory import TerraformFactory

class AWSTarget(BaseTarget):   
    def __init__(self, config: Dict[str, Any]):
        super().__init__(name=Target.AWS.value, config=config)
        self.region = config.get('region', 'us-east-1')
        
        # Initialize AWS credentials
        self._init_credentials()
    
    def _init_credentials(self) -> None:
        """Initialize AWS credentials."""
        try:
            self.session = boto3.Session(region_name=self.region)
            self.sts = self.session.client('sts')
        except Exception as e:
            raise Exception(f"Failed to initialize AWS credentials: {str(e)}")
    
    def validate_credentials(self) -> None:
        """Validate AWS credentials and permissions."""
        try:
            # Make a simple API call to verify credentials
            self.sts.get_caller_identity()
        except Exception as e:
            raise Exception(f"Failed to validate AWS credentials: {str(e)}")
    
    def get_provisioner(self, stack_obj: Stack) -> TerraformProvisioner:
        """Get the appropriate provisioner for this target."""
        return TerraformFactory.create(stack_obj, Target.AWS, self.config) 