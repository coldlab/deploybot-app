from deploybot.cloud.gcp.sql_admin import GCPCloudSQLAdmin
import copy

class GCPCloudSQLAdminService:
    def __init__(self) -> None:
        self.client = GCPCloudSQLAdmin()

    def create_psql_instance(self, project_id: str, instance_name: str, region: str, instance_body: dict) -> dict:
        try:
            instance = self.client.get_instance(project_id, instance_name)
            print(f"Instance {instance_name} already exists")
            return instance
        except Exception as e:
            print(f"Instance {instance_name} not found, creating new instance...")

        instance_body = copy.deepcopy(instance_body)
        instance_body['name'] = instance_name
        instance_body['region'] = region
        print(f"Creating Cloud SQL instance: {instance_name}...")
        instance = self.client.create_instance(project_id, instance_name, instance_body)
        print(f"Cloud SQL instance created: {instance_name}")
        return instance

    def create_database_and_user(self, project_id: str, instance_name: str, database_name: str, user_name: str, user_password: str = "testpassword123") -> None:
        try:
            database = self.client.get_database(project_id, instance_name, database_name)
            print(f"Database {database_name} already exists")
        except Exception as e:
            print(f"Database {database_name} not found, creating new database...")
            
            database_body = {
                'name': database_name
            }
            database = self.client.create_database_async(project_id, instance_name, database_body)
            print(f"Cloud SQL database created: {database}")
        
        try:
            user = self.client.get_user(project_id, instance_name, user_name)
            print(f"User {user_name} already exists")
        except Exception as e:
            print(f"User {user_name} not found, creating new user...")

            user_body = {
                'name': user_name,
                'password': user_password  # In production, use a secure password
            }
            user = self.client.create_user_async(project_id, instance_name, user_body)
            print(f"Cloud SQL user created: {user}")
    
    def delete_sql_instance(self, project_id: str, instance_name: str) -> None:
        try:
            self.client.get_instance(project_id, instance_name)
        except Exception:
            print(f"Instance {instance_name} not found, skipping deletion...")
            return
        print(f"Deleting instance: {instance_name}...")
        self.client.delete_instance(project_id, instance_name)
        print(f"Deleted instance: {instance_name}")
