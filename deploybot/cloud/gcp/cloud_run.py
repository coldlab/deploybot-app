from .client_factory import GCPClientFactory
from google.cloud import run_v2
import time
from google.iam.v1.iam_policy_pb2 import GetIamPolicyRequest, SetIamPolicyRequest
from google.iam.v1.policy_pb2 import Policy

class GCPCloudRun:
    def __init__(self):
        self.client = GCPClientFactory().get_cloud_run_client()

    def get_service(self, project_id: str, region: str, service_name: str) -> run_v2.Service:
        name=f"projects/{project_id}/locations/{region}/services/{service_name}"
        return self.client.get_service(name=name)

    def create_service_async(self, project_id: str, region: str, service_name: str, service_body: run_v2.Service) -> run_v2.Service:
        parent=f"projects/{project_id}/locations/{region}"
        return self.client.create_service(parent=parent, service_id=service_name, service=service_body)
    
    def create_service(self, project_id: str, region: str, service_name: str, service_body: run_v2.Service) -> run_v2.Service:
        self.create_service_async(project_id, region, service_name, service_body)
        print(f"Cloud Run deployment started: {service_name}")
        return self.wait_for_service(project_id, region, service_name)

    def update_service_async(self, project_id: str, region: str, service_name: str, service_body: run_v2.Service) -> run_v2.Service:
        name=f"projects/{project_id}/locations/{region}/services/{service_name}"
        service_body.name = name
        return self.client.update_service(service=service_body)
    
    def update_service(self, project_id: str, region: str, service_name: str, service_body: run_v2.Service) -> run_v2.Service:
        self.update_service_async(project_id, region, service_name, service_body)
        return self.wait_for_service(project_id, region, service_name)

    def delete_service(self, project_id: str, region: str, service_name: str) -> None:
        name=f"projects/{project_id}/locations/{region}/services/{service_name}"
        operation = self.client.delete_service(name=name)
        operation.result()

    def wait_for_service(self, project_id: str, region: str, service_name: str, wait_time: int = 10) -> run_v2.Service:
        while True:
            service = self.get_service(project_id, region, service_name)
            terminal_condition = service.terminal_condition
            print(f"Waiting for service {service_name} to finish...")
            if terminal_condition is not None:
                status = terminal_condition.state
                if status == run_v2.types.Condition.State.CONDITION_SUCCEEDED:
                    print(f"Service {service_name} finished successfully")
                    return service
                elif status == run_v2.types.Condition.State.CONDITION_FAILED:
                    raise Exception(f"Service {service_name} failed")
            time.sleep(wait_time)

    def get_iam_policy(self, project_id: str, region: str, service_name: str) -> Policy:
        name=f"projects/{project_id}/locations/{region}/services/{service_name}"
        request = GetIamPolicyRequest(resource=name)
        return self.client.get_iam_policy(request)
    
    def set_iam_policy(self, project_id: str, region: str, service_name: str, policy: Policy) -> Policy:
        name=f"projects/{project_id}/locations/{region}/services/{service_name}"
        request = SetIamPolicyRequest(resource=name, policy=policy)
        return self.client.set_iam_policy(request)