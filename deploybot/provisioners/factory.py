from typing import Dict, Any

from deploybot.core.enums import Target
from deploybot.core.stack import Stack
from deploybot.core.enums import Provisioner
from deploybot.provisioners.base import BaseProvisioner
from .terraform import TerraformProvisioner
from .pulumi import PulumiProvisioner

class ProvisionerFactory:   
    @classmethod
    def create(cls, provisioner: Provisioner, stack_obj: Stack, target: Target, target_config: Dict[str, Any]) -> BaseProvisioner:
        provisioner_dir = stack_obj.get_provisioner_dir(provisioner, target.value)

        provisioner_config = {
            'provider': target.value,
            'variables': {
                **target_config
            }
        }
        
        if provisioner == Provisioner.TERRAFORM:
            
            # Create Terraform configuration
            # tf_config = {
            #     'provider': target.value,
            #     'variables': {
            #         **target_config
            #     }
            # }
            
            return TerraformProvisioner(
                tf_dir=provisioner_dir,
                config=provisioner_config
            )
        elif provisioner == Provisioner.PULUMI:
            provisioner_config['project_name'] = stack_obj.name
            if target == Target.GCP:
                provisioner_config['provider_variables'] = {'gcp:project': target_config['project_id']}
                target_config.pop('project_id')
            elif target == Target.AWS:
                provisioner_config['provider_variables'] = {'aws:region': target_config['region']}
                target_config.pop('region')
            else:
                raise ValueError(f"Invalid target: {target}")
            
            return PulumiProvisioner(
                work_dir=provisioner_dir,
                config=provisioner_config
            )
        else:
            raise ValueError(f"Invalid provisioner: {provisioner}")