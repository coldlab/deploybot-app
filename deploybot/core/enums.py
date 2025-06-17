from enum import Enum

class Target(str, Enum):
    """Available deployment targets."""
    GCP = "gcp"
    AWS = "aws"
    ONPREM = "onprem"

class Provisioner(str, Enum):
    """Available provisioners."""
    TERRAFORM = "terraform"
    ANSIBLE = "ansible"
