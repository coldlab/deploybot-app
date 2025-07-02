from typing import Dict, Any
import boto3

from deploybot.core.enums import Target
from deploybot.core.enums import Provisioner
from deploybot.core.stack import Stack
from deploybot.provisioners.base import BaseProvisioner
from .base import BaseTarget
from ..provisioners.factory import ProvisionerFactory

class AWSTarget(BaseTarget):   
    def __init__(self, config: Dict[str, Any], provisioner: Provisioner):
        region = config.get('region', 'us-east-1')
        super().__init__(name=Target.AWS.value, region=region, config=config, provisioner=provisioner)
        
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
    
    def get_provisioner(self, stack_obj: Stack) -> BaseProvisioner:
        return ProvisionerFactory.create(self.provisioner, stack_obj, Target.AWS, self.config) 