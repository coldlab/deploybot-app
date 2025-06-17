# deploybot/targets/factory.py
from typing import Dict, Any

from deploybot.core.parameters import DeployParameters
from .base import BaseTarget
from .gcp import GCPTarget
from .aws import AWSTarget
from ..core.enums import Target

class TargetFactory:
    """Factory for creating deployment targets."""
    
    _targets = {
        Target.GCP: GCPTarget,
        Target.AWS: AWSTarget,
    }
    
    @classmethod
    def create(cls, target_type: Target, config: Dict[str, Any], parameters: DeployParameters) -> BaseTarget:
        target_class = cls._targets.get(target_type)
        if not target_class:
            raise ValueError(f"Unsupported target type: {target_type}")

        target_config = config.get(target_type.value, {}).copy()
        
        if target_type == Target.GCP:
            target_config['project_id'] = parameters.project_id
            if parameters.region:
                target_config['region'] = parameters.region
                target_config['zone'] = f"{parameters.region}-a"
        
        elif target_type == Target.AWS:
            if parameters.region:
                target_config['region'] = parameters.region              
            
        return target_class(target_config)