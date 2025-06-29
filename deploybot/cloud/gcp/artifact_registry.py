from .client_factory import GCPClientFactory

class GCPArtifactRegistry:
    def __init__(self):
        self.client = GCPClientFactory().get_artifact_registry_client()

    def delete_package(self, project_id: str, region: str, repository_name: str, package_name: str) -> None:
        name = f"projects/{project_id}/locations/{region}/repositories/{repository_name}/packages/{package_name}"
        operation = self.client.delete_package(name=name)
        operation.result()
