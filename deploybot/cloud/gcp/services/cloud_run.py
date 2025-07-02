from deploybot.cloud.gcp.cloud_run import GCPCloudRun
from google.cloud.run_v2 import Service
from google.iam.v1.policy_pb2 import Binding    

class GCPCloudRunService:
    def __init__(self):
        self.client = GCPCloudRun()

    def deploy(self, project_id: str, region: str, service_name: str, service_body: Service) -> Service:
        print(f"Deploying to Cloud Run: {service_name}")
        try:
            service = self.client.get_service(project_id, region, service_name)
            service = self.client.update_service(project_id, region, service_name, service_body)
        except Exception:
            service = self.client.create_service(project_id, region, service_name, service_body)
        return service

    def delete_service(self, project_id: str, region: str, service_name: str) -> None:
        try:
            self.client.get_service(project_id, region, service_name)
        except Exception:
            print(f"Service {service_name} not found in {region}, project: {project_id}")
            print("Skipping deletion...")
            return
        print(f"Deleting service: {service_name} in {region}, project: {project_id}")
        self.client.delete_service(project_id, region, service_name)
        print(f"Deleted service: {service_name} in {region}, project: {project_id}")


    def set_iam_policy(self, project_id: str, region: str, service_name: str, binding: Binding) -> None:
        import json
        print(f"Fetching current IAM policy for service: {service_name} in {region}, project: {project_id}")
        policy = self.client.get_iam_policy(project_id, region, service_name)
        
        print("Adding new binding:")
        print(json.dumps({
            'role': binding.role,
            'members': list(binding.members)
        }, indent=2))

        # Validation: check if binding already exists
        binding_exists = False
        for b in policy.bindings:
            if b.role == binding.role and set(b.members) == set(binding.members):
                binding_exists = True
                break
        
        if binding_exists:
            print("Binding already exists in the policy. Skipping append.")
            return

        policy.bindings.append(binding)
        print("Setting updated IAM policy...")
        self.client.set_iam_policy(project_id, region, service_name, policy)
        print("IAM policy updated successfully.")
