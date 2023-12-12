import pulumi_gcp as gcp
from db import database, instance, secret, user
from project import project, service
from pulumi import Config, Output, ResourceOptions, export, get_stack
from repo import docker_image
from storage import assets_bucket

# Setup Vars
gcp_config = Config('gcp')
region = gcp_config.get('region')
config = Config()
image = config.get('image')
zone = config.require('zone')
stack = get_stack()
cpu_limit = config.get('cpu-limit') or '1000m'
memory_limit = config.get('memory-limit') or '512Mi'
url = config.get('url') or zone
max_instance_count = config.get_int('max-instance-count') or 1
min_instance_count = config.get_int('min-instance-count') or 0

# WordPress Config
wp_config_extra = {
    # General WP Config
    'WP_SITEURL': url,
    'WP_HOME': url,
    'WP_ENVIRONMENT_TYPE': stack,
    'WP_ALLOW_REPAIR': 'true',
    'FORCE_SSL_ADMIN': 'true',
    'AUTOMATIC_UPDATER_DISABLED': 'true',
    'IMAGE_EDIT_OVERWRITE': 'true',
    ## WP Stateless Plugin
    'WP_STATELESS_MEDIA_CACHE_BUSTING': 'true',
    'WP_STATELESS_MEDIA_MODE': 'ephemeral',
    'WP_STATELESS_MEDIA_BUCKET': f'{stack}-website-assets',
    'WP_STATELESS_MEDIA_BODY_REWRITE': 'true',
}


def serialize_wp_config(config):
    return '\n'.join(
        [f"define('{key}', '{value}');" for key, value in config.items()]
    )


serialized_config = serialize_wp_config(wp_config_extra)

# Setup Service Account
cloud_run_sa = gcp.serviceaccount.Account(
    'cloud-run-serviceaccount',
    account_id='wordpress-cloud-run',
    display_name='Wordpress Service Account',
    project=project.project_id,
)

# The format 'serviceAccount:' needs to be prefixed for the member email
formatted_member_email = Output.concat('serviceAccount:', cloud_run_sa.email)

# Setup Service Account Permissions
secret_access = gcp.secretmanager.SecretIamMember(
    'cloud-run-sa-secret-permissions',
    secret_id=secret.id,
    role='roles/secretmanager.secretAccessor',
    member=formatted_member_email,
    project=project.project_id,
    opts=ResourceOptions(
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
volume_name = 'wp-data'

service = gcp.cloudrunv2.Service(
    'wordpress-cloudrun-service',
    location=region,
    name=f'{stack}-wordpress-site',
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
            min_instance_count=min_instance_count,
            max_instance_count=max_instance_count,
        ),
        execution_environment='EXECUTION_ENVIRONMENT_GEN2',
        containers=[
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=docker_image.image_name,
                ports=[
                    gcp.cloudrunv2.ServiceTemplateContainerPortArgs(
                        container_port=80,
                    )
                ],
                resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    startup_cpu_boost=True,
                    limits={'cpu': cpu_limit, 'memory': memory_limit},
                ),
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
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name='WORDPRESS_CONFIG_EXTRA',
                        value=serialized_config,
                    ),
                ],
                volume_mounts=[
                    gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
                        name=volume_name, mount_path='/var/www/html'
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
                        name='cloudsql',
                        mount_path='/cloudsql',
                    ),
                ],
            ),
        ],
        volumes=[
            gcp.cloudrunv2.ServiceTemplateVolumeArgs(name=volume_name),
            gcp.cloudrunv2.ServiceTemplateVolumeArgs(
                name='cloudsql',
                cloud_sql_instance=gcp.cloudrunv2.ServiceTemplateVolumeCloudSqlInstanceArgs(
                    instances=[instance.connection_name],
                ),
            ),
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
    project=project.project_id,
    opts=ResourceOptions(depends_on=[service]),
)

allow_public_ingress = gcp.cloudrun.IamBinding(
    'wordpress-cloud-run-iam-binding',
    location=service.location,
    service=service.name,
    role='roles/run.invoker',
    project=project.project_id,
    members=['allUsers'],
)

# Setup Outputs
export('Wordpress Service Account', cloud_run_sa.email)
export('Wordpress Cloud Run URI', service.uri)
export('Cloud Run Service', service.name)
