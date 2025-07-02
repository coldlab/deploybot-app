from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .enums import Target, Provisioner

class StackConfig(BaseModel):
    """Stack configuration model."""
    name: str = Field(
        description="Name of the stack"
    )
    target: Target = Field(
        description="Deployment target (gcp or onprem)"
    )
    default_provisioner: Provisioner = Field(
        description="Default provisioner to use"
    )
    provisioners: List[Provisioner] = Field(
        description="List of provisioners to use. If not specified, the default provisioner will be used."
    )
    config: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Cloud provider specific configuration"
    )
