from typing import Dict, Any

from deploybot.core.enums import Target
from deploybot.core.stack import Stack
from deploybot.core.enums import Provisioner
from .terraform import TerraformProvisioner

class TerraformFactory:   
    @classmethod
    def create(cls, stack_obj: Stack, target: Target, target_config: Dict[str, Any]) -> TerraformProvisioner:
        # Get Terraform directory from stack
        tf_dir = stack_obj.get_provisioner_dir(Provisioner.TERRAFORM, target.value)
        
        # Create Terraform configuration
        tf_config = {
            'provider': target.value,
            'variables': {
                **target_config
            }
        }
        
        return TerraformProvisioner(
            tf_dir=tf_dir,
            config=tf_config
        ) 