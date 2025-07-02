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

        # print(f"Application URL: {service.uri}")
        # print(f"FastAPI PostgreSQL stack deployment completed!")

        return {
            'app_url': service.uri
        }


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
        """Show deployment plan with all resources and app details."""
        print("=" * 60)
        print("🚀 FastAPI PostgreSQL Stack Deployment Plan")
        print("=" * 60)
        
        # Project Information
        print(f"\n📋 Project Information:")
        print(f"   Project ID: {self.variables['project_id']}")
        print(f"   Region: {self.variables['region']}")
        print(f"   Stack: {self.stack_name}")
        
        # Application Details
        print(f"\n📱 Application Details:")
        print(f"   App Name: {self.variables['app_name']}")
        print(f"   Image Tag: {self.variables['image_tag']}")
        print(f"   Source: FastAPI application with PostgreSQL")
        print(f"   Container Registry: gcr.io/{self.variables['project_id']}/{self.variables['app_name']}:{self.variables['image_tag']}")
        
        # Infrastructure Resources
        print(f"\n🏗️  Infrastructure Resources to Create:")
        print(f"   ┌─ Google Cloud APIs to Enable:")
        print(f"   │  ├─ Cloud SQL Admin API")
        print(f"   │  ├─ Cloud Run API")
        print(f"   │  ├─ Cloud Build API")
        print(f"   │  ├─ Cloud Storage API")
        print(f"   │  └─ Container Registry API")
        print(f"   │")
        print(f"   ├─ Database Layer:")
        print(f"   │  ├─ Cloud SQL Instance: {self.variables['db_instance']}")
        print(f"   │  │  ├─ Database: {self.variables['database_name']}")
        print(f"   │  │  ├─ User: {self.variables['db_user']}")
        print(f"   │  │  └─ Version: PostgreSQL 14")
        print(f"   │  └─ Connection: Private VPC")
        print(f"   │")
        print(f"   ├─ Application Layer:")
        print(f"   │  ├─ Cloud Run Service: {self.variables['app_name']}")
        print(f"   │  │  ├─ Region: {self.variables['region']}")
        print(f"   │  │  ├─ CPU: {self.variables['cloud_run_cpu']}")
        print(f"   │  │  ├─ Memory: {self.variables['cloud_run_memory']}")
        print(f"   │  │  ├─ Max Instances: {self.variables['cloud_run_max_instances']}")
        print(f"   │  │  └─ Public Access: Enabled")
        print(f"   │  └─ Cloud SQL Connection: Enabled")
        print(f"   │")
        print(f"   ├─ Build & Storage:")
        print(f"   │  ├─ Cloud Storage Bucket: {self.variables['bucket_name']}")
        print(f"   │  ├─ Source Archive: {self.variables['app_name']}.tar.gz")
        print(f"   │  ├─ Cloud Build: Docker container build")
        print(f"   │  └─ Artifact Registry: Container image storage")
        print(f"   │")
        print(f"   └─ Security & IAM:")
        print(f"      ├─ Service Account: Cloud Run service account")
        print(f"      ├─ IAM Binding: roles/run.invoker for allUsers")
        print(f"      └─ Cloud SQL Client: Service account permissions")
        
        # Environment Variables
        print(f"\n🔧 Environment Variables:")
        print(f"   ├─ DB_USER: {self.variables['db_user']}")
        print(f"   ├─ DB_PASSWORD: [HIDDEN]")
        print(f"   ├─ DB_NAME: {self.variables['database_name']}")
        print(f"   └─ DB_CONNECTION_NAME: [Auto-generated]")
        
        # Deployment Strategy
        print(f"\n⚡ Deployment Strategy:")
        print(f"   ├─ Parallel Deployment: Infrastructure + App")
        print(f"   ├─ Database: Cloud SQL instance creation")
        print(f"   ├─ Application: Container build + Cloud Run deployment")
        print(f"   └─ Integration: Cloud SQL connection via Unix socket")
        
        # Estimated Costs (rough estimates)
        print(f"\n💰 Estimated Monthly Costs (rough estimates):")
        print(f"   ├─ Cloud SQL (db-f1-micro): ~$7-15/month")
        print(f"   ├─ Cloud Run (512Mi, 1 CPU): ~$5-20/month (usage-based)")
        print(f"   ├─ Cloud Storage: ~$0.02/GB/month")
        print(f"   ├─ Cloud Build: ~$0.003/minute (build time)")
        print(f"   └─ Total: ~$12-35/month (depending on usage)")
        
        # Post-Deployment Info
        print(f"\n🎯 Post-Deployment Information:")
        print(f"   ├─ Application URL: https://{self.variables['app_name']}-[hash]-{self.variables['region']}.run.app")
        print(f"   ├─ Database Connection: Private VPC only")
        print(f"   ├─ Scaling: Automatic (0 to {self.variables['cloud_run_max_instances']} instances)")
        print(f"   └─ Monitoring: Cloud Run metrics available")
        
        print(f"\n" + "=" * 60)
        print("✅ Plan complete! Run 'deploy' to execute this plan.")
        print("=" * 60)

# RecipeRegistry.register('fastapi-postgres', FastAPIPostgresRecipe)


if __name__ == "__main__":
    recipe = FastAPIPostgresRecipe()
    recipe.deploy()