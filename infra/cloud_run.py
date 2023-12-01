import pulumi
import pulumi_gcp as gcp
from db import database, instance, secret, user
from project import project, service

# Setup Vars
gcp_config = pulumi.Config('gcp')
region = gcp_config.get('region')
config = pulumi.Config()
image = config.get('image')

# Setup Service Account
cloud_run_sa = gcp.serviceaccount.Account(
    'cloud-run-serviceaccount',
    account_id='wordpress-cloud-run',
    display_name='Wordpress Service Account',
)

# The format 'serviceAccount:' needs to be prefixed for the member email
formatted_member_email = pulumi.Output.concat(
    'serviceAccount:', cloud_run_sa.email
)

# Setup Service Account Permissions
secret_access = gcp.secretmanager.SecretIamMember(
    'cloud-run-sa-secret-permissions',
    secret_id=secret.id,
    role='roles/secretmanager.secretAccessor',
    member=formatted_member_email,
    opts=pulumi.ResourceOptions(
        parent=cloud_run_sa, depends_on=[cloud_run_sa, secret]
    ),
)

db_access = gcp.projects.IAMBinding(
    'wordpress-sa-sql-binding',
    members=[formatted_member_email],
    project=project.project_id,
    role='roles/cloudsql.client',
)

# Setup Cloud Run Service
volume_name = 'wp-files'
service = gcp.cloudrunv2.Service(
    'wordpress-cloudrun-service',
    location=region,
    name='wordpress-site',
    ingress='INGRESS_TRAFFIC_ALL',
    traffics=[
        gcp.cloudrunv2.ServiceTrafficArgs(
            type='TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST',
            percent=100,
        )
    ],
    template=gcp.cloudrunv2.ServiceTemplateArgs(
        service_account=cloud_run_sa.email,
        scaling=gcp.cloudrunv2.ServiceTemplateScalingArgs(
            max_instance_count=1,
        ),
        execution_environment='EXECUTION_ENVIRONMENT_GEN2',
        containers=[
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=image,
                ports=[
                    gcp.cloudrunv2.ServiceTemplateContainerPortArgs(
                        container_port=80,
                    )
                ],
                envs=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name='WORDPRESS_DB_HOST',
                        value=instance.connection_name.apply(
                            lambda conn_name: f':/cloudsql/{conn_name}'
                        ),
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name='WORDPRESS_DB_USER',
                        value=user.name,
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name='WORDPRESS_DB_NAME',
                        value=database.name,
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name='WORDPRESS_DB_PASSWORD',
                        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
                            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                                version='latest',
                                secret=secret.name,
                            ),
                        ),
                    ),
                ],
                volume_mounts=[
                    gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
                        name='cloudsql',
                        mount_path='/cloudsql',
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
                        name=volume_name, mount_path='/var/www/html'
                    ),
                ],
            ),
        ],
        volumes=[
            gcp.cloudrunv2.ServiceTemplateVolumeArgs(
                name='cloudsql',
                cloud_sql_instance=gcp.cloudrunv2.ServiceTemplateVolumeCloudSqlInstanceArgs(
                    instances=[instance.connection_name],
                ),
            ),
            gcp.cloudrunv2.ServiceTemplateVolumeArgs(name=volume_name),
        ],
        # vpc_access=gcp.cloudrunv2.ServiceTemplateVpcAccessArgs(
        #     egress='ALL_TRAFFIC',
        #     network_interfaces=[
        #         gcp.cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
        #             network=network.name, subnetwork=subnet.name
        #         )
        #     ],
        # ),
    ),
    opts=pulumi.ResourceOptions(depends_on=[service]),
)

allow_public_ingress = gcp.cloudrun.IamBinding(
    'wordpress-cloud-run-iam-binding',
    location=service.location,
    service=service.name,
    role='roles/run.invoker',
    members=['allUsers'],
)
# Setup Outputs
pulumi.export('Wordpress Service Account', cloud_run_sa.email)
pulumi.export('Wordpress Cloud Run URI', service.uri)
pulumi.export('Cloud Run Service', service.name)
