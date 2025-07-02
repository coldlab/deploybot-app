from deploybot.core.recipie import BaseRecipe
from deploybot.cloud.gcp.services.sql_admin import GCPCloudSQLAdminService
from deploybot.cloud.gcp.services.storage import GCPStorageService
from deploybot.cloud.gcp.services.cloud_run import GCPCloudRunService
from deploybot.cloud.gcp.cloud_build import GCPCloudBuild
from deploybot.cloud.gcp.services.sql_templates import POSTGRES_SQL_TEMPLATE
from pathlib import Path
from google.iam.v1.policy_pb2 import Binding
from google.cloud.run_v2 import Service, RevisionTemplate, Container, VolumeMount, Volume, CloudSqlInstance, EnvVar
from concurrent.futures import ThreadPoolExecutor
from deploybot.cloud.gcp.services.service_usage import GCPServiceUsageService
from deploybot.cloud.gcp.enums.services import GoogleCloudService
from deploybot.cloud.gcp.services.artifact_registry import GCPArtifactRegistryService
# from deploybot.core.recipie_registry import RecipeRegistry

class FastAPIPostgresRecipe(BaseRecipe):
    def __init__(self):
        super().__init__()
        self.stack_name = 'fastapi-postgres'
        self.service_usage_service = GCPServiceUsageService()
        self.sql_admin_service = GCPCloudSQLAdminService()
        self.storage_service = GCPStorageService()
        self.cloud_build = GCPCloudBuild()
        self.cloud_run_service = GCPCloudRunService()
        self.artifact_registry_service = GCPArtifactRegistryService()
    
    def _db_flow(self):
        instance_body = POSTGRES_SQL_TEMPLATE
        instance = self.sql_admin_service.create_psql_instance(
            self.variables['project_id'],
            self.variables['db_instance'],
            self.variables['region'],
            instance_body
        )
        self.sql_admin_service.create_database_and_user(
            self.variables['project_id'],
            self.variables['db_instance'],
            self.variables['database_name'],
            self.variables['db_user'],
            self.variables['db_password']
        )

        return {
            # 'sql_instance': instance,
            # 'sql_url': instance['selfLink'],
            # 'sql_ip': instance['ipAddresses'][0]['ipAddress'],
            'sql_connection_name': instance['connectionName']
        }

    def _app_flow(self):
        source_dir = str(Path(__file__).parent.parent.parent / 'app')
        object_name = self.storage_service.upload_directory_as_tar(
            self.variables['bucket_name'],
            source_dir,
            self.variables['app_name']
        )

        image_path = f"gcr.io/{self.variables['project_id']}/{self.variables['app_name']}:{self.variables['image_tag']}"
        build_body = {
        'source': {
            'storage_source': {
                'bucket': self.variables['bucket_name'],
                'object': object_name
            }
        },
        'steps': [
            {
                'name': 'gcr.io/cloud-builders/docker',
                'args': [
                    'build', '-t', image_path, '.'
                ]
            }
        ],
        'images': [image_path]
    }
        build = self.cloud_build.create_build(
            self.variables['project_id'],
            build_body
        )

        image_url = f"{build.results.images[0].name}@{build.results.images[0].digest}"

        return image_url
     

    def deploy(self):
        self.service_usage_service.enable_api(self.variables['project_id'], GoogleCloudService.CLOUD_SQL)
        self.service_usage_service.enable_api(self.variables['project_id'], GoogleCloudService.CLOUD_RUN)
        self.service_usage_service.enable_api(self.variables['project_id'], GoogleCloudService.CLOUD_BUILD)
        self.service_usage_service.enable_api(self.variables['project_id'], GoogleCloudService.CLOUD_STORAGE)
        self.service_usage_service.enable_api(self.variables['project_id'], GoogleCloudService.CONTAINER_REGISTRY)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_db = executor.submit(self._db_flow)
            future_app = executor.submit(self._app_flow)

            db_result = future_db.result()
            image_url = future_app.result()

        # print(db_result)
        service_body = Service(
        template=RevisionTemplate(
            containers=[Container(
                image=image_url,
                volume_mounts=[VolumeMount(name='cloudsql', mount_path='/cloudsql')],
                env=[EnvVar(name='DB_USER', value=self.variables['db_user']),
                     EnvVar(name='DB_PASSWORD', value=self.variables['db_password']),
                     EnvVar(name='DB_NAME', value=self.variables['database_name']),
                     EnvVar(name='DB_CONNECTION_NAME', value=db_result['sql_connection_name'])
                     ]
                )],
            volumes=[Volume(name='cloudsql', cloud_sql_instance=CloudSqlInstance(instances=[db_result['sql_connection_name']]))]
        )
    )
        service = self.cloud_run_service.deploy(
            self.variables['project_id'],
            self.variables['region'],
            self.variables['app_name'],
            service_body
        )

        binding = Binding(
            role='roles/run.invoker',
            members=['allUsers']
        )
        self.cloud_run_service.set_iam_policy(
            self.variables['project_id'],
            self.variables['region'],
            self.variables['app_name'],
            binding
        )

        print(f"FastAPI PostgreSQL stack deployment completed!")

        # TODO: Create a state file to track the deployment (e.g. something simple just to know if the deployment is done, failed, etc.)
        

    def destroy(self):
        print("Starting parallel destruction of FastAPI PostgreSQL stack...")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all deletion tasks in parallel
            future_cloud_run = executor.submit(
                self.cloud_run_service.delete_service,
                self.variables['project_id'],
                self.variables['region'],
                self.variables['app_name']
            )
            
            future_sql = executor.submit(
                self.sql_admin_service.delete_sql_instance,
                self.variables['project_id'],
                self.variables['db_instance']
            )
            
            future_storage = executor.submit(
                self.storage_service.delete_file,
                self.variables['bucket_name'],
                f"{self.variables['app_name']}.tar.gz"
            )
            
            repository_name = 'gcr.io'
            location = 'us'
            future_artifact = executor.submit(
                self.artifact_registry_service.delete_package,
                self.variables['project_id'],
                location,
                repository_name,
                self.variables['app_name']
            )
            
            # Wait for all operations to complete
            future_cloud_run.result()
            future_sql.result()
            future_storage.result()
            future_artifact.result()
        
        print("FastAPI PostgreSQL stack destruction completed!")


    def plan(self):
        pass

# RecipeRegistry.register('fastapi-postgres', FastAPIPostgresRecipe)


if __name__ == "__main__":
    recipe = FastAPIPostgresRecipe()
    recipe.deploy()