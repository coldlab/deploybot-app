from .client_factory import GCPClientFactory
import time

class GCPCloudSQLAdmin:
    _INSTANCE_CREATION_TIMEOUT = 60
    _INSTANCE_OPERATION_MESSAGE_TEMPLATE = "Cloud SQL instance '{instance_name}'"
    _DATABASE_OPERATION_MESSAGE_TEMPLATE = "Cloud SQL database '{database_name}'"
    _USER_OPERATION_MESSAGE_TEMPLATE = "Cloud SQL user '{user_name}'"
    
    def __init__(self) -> None:
        self.client = GCPClientFactory().get_sql_admin_client()
        
    # Instance API
    def create_instance_async(self, project_id: str, instance_body: dict) -> str:
        request = self.client.instances().insert(project=project_id, body=instance_body)
        response = request.execute()
        return response['name']
        
    def create_instance(self, project_id: str, instance_name: str, instance_body: dict) -> dict:
        operation_name = self.create_instance_async(project_id, instance_body)
        message = self._INSTANCE_OPERATION_MESSAGE_TEMPLATE.format(instance_name=instance_name)
        self.wait_for_operation(project_id, operation_name, message, self._INSTANCE_CREATION_TIMEOUT)
        return self.get_instance(project_id, instance_name)

    def get_instance(self, project_id: str, instance_name: str) -> dict:
        request = self.client.instances().get(project=project_id, instance=instance_name)
        response = request.execute()
        return response

    def delete_instance_async(self, project_id: str, instance_name: str) -> str:
        request = self.client.instances().delete(project=project_id, instance=instance_name)
        response = request.execute()
        return response['name']

    def delete_instance(self, project_id: str, instance_name: str) -> None:
        operation_name = self.delete_instance_async(project_id, instance_name)
        message = self._INSTANCE_OPERATION_MESSAGE_TEMPLATE.format(instance_name=instance_name)
        self.wait_for_operation(project_id, operation_name, message)

    # Database API
    def create_database_async(self, project_id: str, instance_name: str, database_body: dict) -> str:
        request = self.client.databases().insert(project=project_id, instance=instance_name, body=database_body)
        response = request.execute()
        return response['name']
    
    def create_database(self, project_id: str, instance_name: str, database_name: str, database_body: dict) -> dict: 
        operation_name = self.create_database_async(project_id, instance_name, database_body)
        message = self._DATABASE_OPERATION_MESSAGE_TEMPLATE.format(database_name=database_name)
        self.wait_for_operation(project_id, operation_name, message)
        return self.get_database(project_id, instance_name, database_name)
    
    def get_database(self, project_id: str, instance_name: str, database_name: str) -> dict:
        request = self.client.databases().get(project=project_id, instance=instance_name, database=database_name)
        response = request.execute()
        return response
    
    # User API
    def create_user_async(self, project_id: str, instance_name: str, user_body: dict) -> str:
        request = self.client.users().insert(project=project_id, instance=instance_name, body=user_body)
        response = request.execute()
        return response['name']
    
    def create_user(self, project_id: str, instance_name: str, user_name: str, user_body: dict) -> dict:
        operation_name = self.create_user_async(project_id, instance_name, user_body)
        message = self._USER_OPERATION_MESSAGE_TEMPLATE.format(user_name=user_name)
        self.wait_for_operation(project_id, operation_name, message)
        return self.get_user(project_id, instance_name, user_name)
    
    def get_user(self, project_id: str, instance_name: str, user_name: str) -> dict:    
        request = self.client.users().get(project=project_id, instance=instance_name, user=user_name)
        response = request.execute()
        return response

    # Operation API
    def get_operation(self, project_id: str, operation_name: str) -> dict:
        request = self.client.operations().get(project=project_id, operation=operation_name)
        response = request.execute()
        return response
    
    def wait_for_operation(self, project_id: str, operation_name: str, resource_message:str, wait_time: int = 10) -> dict:
        total_time = 0
        while True:
            operation = self.get_operation(project_id, operation_name)
            
            operation_type = operation['operationType']
            print(f"Waiting for operation {operation_type} of {resource_message} to complete... [{total_time}s]")
            
            if operation['status'] == 'DONE':
                print(f"Operation {operation_type} of {resource_message} completed successfully in {total_time} seconds")
                return operation
            
            print(f"Waiting for {wait_time} seconds before checking again...")
            total_time += wait_time
            time.sleep(wait_time)
