from deploybot.cloud.gcp.artifact_registry import GCPArtifactRegistry

class GCPArtifactRegistryService:
    def __init__(self):
        self.client = GCPArtifactRegistry()

    def delete_package(self, project_id: str, region: str, repository_name: str, package_name: str) -> None:
        try:
            self.client.get_package(project_id, region, repository_name, package_name)
        except Exception:
            print(f"Package {package_name} not found, skipping deletion...")
            return
        self.client.delete_package(project_id, region, repository_name, package_name)
        print(f"Deleted package: {package_name}")