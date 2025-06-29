from .client_factory import GCPClientFactory
from google.cloud.devtools import cloudbuild_v1
from google.api_core.operation import Operation
import time

class GCPCloudBuild:
    def __init__(self):
        self.client = GCPClientFactory().get_cloud_build_client()
        # self.operations_client = GCPClientFactory().get_operations_client()

    def create_build_async(self, project_id: str, build: cloudbuild_v1.Build) -> Operation:
        return self.client.create_build(project_id=project_id, build=build)


    def get_build(self, project_id: str, build_id: str) -> cloudbuild_v1.Build:
        return self.client.get_build(project_id=project_id, id=build_id)

    def create_build(self, project_id: str, build: cloudbuild_v1.Build) -> cloudbuild_v1.Build:
        operation = self.create_build_async(project_id, build)
        while operation.metadata is None or operation.metadata.build is None:
            print("Waiting for build metadata to be available...")
            time.sleep(2)
        build_id = operation.metadata.build.id
        print(f"Cloud Build started: {build_id}")
        return self.wait_for_build(project_id, build_id)

    def wait_for_build(self, project_id: str, build_id: str, wait_time: int = 10) -> cloudbuild_v1.Build:
        while True:
            build = self.get_build(project_id, build_id)
            status = build.status
            print(f"Waiting for build {build_id} to finish...")
            if status == cloudbuild_v1.Build.Status.SUCCESS:
                print(f"Build {build_id} finished successfully")
                return build
            elif build.status == cloudbuild_v1.Build.Status.FAILURE:
                raise Exception(f"Build {build_id} failed")
            time.sleep(wait_time)


