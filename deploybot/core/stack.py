import os
import yaml
from typing import Dict, Any, List
from pathlib import Path

from deploybot.core.config import StackConfig
from deploybot.core.enums import Provisioner, Target

class Stack:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.config = self._load_config()
    
    def _load_config(self) -> StackConfig:
        config_path = os.path.join(self.path, 'stack.yaml')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Stack configuration file '{config_path}' not found for stack '{self.name}'.")
        
        with open(config_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
        
        try:
            return StackConfig(**yaml_content)
        except Exception as e:
            raise ValueError(f"Invalid configuration for stack '{self.name}' in '{config_path}': {e}")
    
    @property
    def provisioners(self) -> List[Provisioner]:
        return self.config.provisioners
    
    @property
    def default_target(self) -> Target:
        return self.config.target
    
    def get_provisioner_dir(self, provisioner: Provisioner, target_name: str) -> str:
        """Returns the target-specific provisioner directory."""
        provisioner_base_dir = os.path.join(self.path, provisioner.value)
        provisioner_target_dir = os.path.join(provisioner_base_dir, target_name)
        if not os.path.isdir(provisioner_target_dir):
            raise FileNotFoundError(f"{provisioner.value.title()} directory for target '{target_name}' not found at {provisioner_target_dir}")
        return provisioner_target_dir

def get_stack(stack_name: str) -> Stack:
    """Get a stack instance by name."""
    stacks_dir = Path(__file__).parent.parent.parent / 'stacks'
    stack_path = stacks_dir / stack_name
    
    if not stack_path.is_dir():
        raise ValueError(f"Stack '{stack_name}' not found.")
    
    return Stack(stack_name, str(stack_path.absolute())) 