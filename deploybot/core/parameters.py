from pydantic import BaseModel, Field
from typing import Optional
from .enums import Target, Provisioner

class DeployParameters(BaseModel):
    stack: str = Field(
        description="Name of the stack to deploy"
    )
    target: Optional[Target] = Field(
        default=None,
        description="Deployment target (gcp, onprem). Defaults to stack's default target if not provided."
    )
    project_id: Optional[str] = Field(
        default=None,
        description="GCP Project ID (required for GCP target)"
    ) 
    region: Optional[str] = Field(
        default=None,
        description="Region to deploy to (overrides stack config)"
    )
    provisioner: Optional[Provisioner] = Field(
        default=None,
        description="Provisioner to use (native, terraform, pulumi). Defaults to stack's default provisioner if not provided."
    )