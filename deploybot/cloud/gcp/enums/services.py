from enum import Enum

class GoogleCloudService(Enum):
    CLOUD_RUN = "run.googleapis.com"
    CLOUD_SQL = "sqladmin.googleapis.com"
    CLOUD_BUILD = "cloudbuild.googleapis.com"
    CLOUD_STORAGE = "storage.googleapis.com"
    CONTAINER_REGISTRY = "containerregistry.googleapis.com"
    ARTIFACT_REGISTRY = "artifactregistry.googleapis.com"
    DNS = "dns.googleapis.com"
    SERVICE_USAGE = "serviceusage.googleapis.com"
