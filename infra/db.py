import pulumi
import pulumi_gcp as gcp
from pulumi_random import RandomPassword

from network import network
from project import project, service

# Setup Config / Vars
stack = pulumi.get_stack()
config = pulumi.Config('db')
gcp_config = pulumi.Config('gcp')
region = gcp_config.get('region')
database_name = config.get('name') or 'wordpress'
username = config.get('username') or 'wordpress'
db_tier = config.get('tier') or 'db-f1-micro'

# Setup Private Services Connection
priv_ip = gcp.compute.GlobalAddress(
    'priving-services-connection-ip',
    name='private-ip-address',
    purpose='VPC_PEERING',
    address_type='INTERNAL',
    prefix_length=16,
    network=network.id,
    project=project.project_id,
    opts=pulumi.ResourceOptions(parent=network, depends_on=[service]),
)

service_connection = gcp.servicenetworking.Connection(
    'gcp-service-networking-connection',
    network=network.id,
    service='servicenetworking.googleapis.com',
    reserved_peering_ranges=[priv_ip.name],
    opts=pulumi.ResourceOptions(parent=network, depends_on=[service]),
)

# Setup DB Password
password = RandomPassword(
    'database-password-generation',
    length=16,
    special=True,
)

# Setup Labels
labels = {
    'app': 'wordpress',
    'env': stack,
    'component': 'database',
}

public_ip_org_policy = gcp.projects.OrganizationPolicy(
    'org-policy-allow-public-ip-sql',
    boolean_policy=gcp.projects.OrganizationPolicyBooleanPolicyArgs(
        enforced=False,
    ),
    constraint='constraints/sql.restrictPublicIp',
    project=project.project_id,
    opts=pulumi.ResourceOptions(parent=project, delete_before_replace=True),
)
# Setup SQL Instance
instance = gcp.sql.DatabaseInstance(
    'instance',
    database_version='MYSQL_8_0',
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier=db_tier,
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            enable_private_path_for_google_cloud_services=True,
            ipv4_enabled=True,
            private_network=network.id,
        ),
        insights_config=gcp.sql.DatabaseInstanceSettingsInsightsConfigArgs(
            query_insights_enabled=True,
            query_plans_per_minute=5,
            query_string_length=1024,
            record_application_tags=True,
            record_client_address=True,
        ),
    ),
    deletion_protection=False if stack == 'staging' else True,
    project=project.project_id,
    opts=pulumi.ResourceOptions(
        depends_on=[service_connection, public_ip_org_policy]
    ),
)

# Setup Database
database = gcp.sql.Database(
    database_name,
    instance=instance.name,
    name=database_name,
    project=instance.project,
    opts=pulumi.ResourceOptions(parent=instance),
)

# Create a user on that instance
user = gcp.sql.User(
    'db-user',
    instance=instance.name,
    name=username,
    password=password.result,
    project=instance.project,
    opts=pulumi.ResourceOptions(parent=instance),
)

# Save Credentials to Secret Manager
secret = gcp.secretmanager.Secret(
    'database-password',
    labels=labels,
    secret_id='pretix-db-pw',
    project=instance.project,
    replication=gcp.secretmanager.SecretReplicationArgs(
        user_managed=gcp.secretmanager.SecretReplicationUserManagedArgs(
            replicas=[
                gcp.secretmanager.SecretReplicationUserManagedReplicaArgs(
                    location=region,
                ),
            ],
        ),
    ),
    opts=(
        pulumi.ResourceOptions(
            parent=password, delete_before_replace=True, depends_on=[service]
        )
    ),
)

version = gcp.secretmanager.SecretVersion(
    'database-password-version',
    secret=secret.id,
    secret_data=password.result,
    opts=pulumi.ResourceOptions(parent=secret),
)

db_bucket = gcp.storage.Bucket(
    'db-bucket',
    name=f'etc-wordpress-db-{stack}',
    location=region,
    uniform_bucket_level_access=True,
    project=instance.project,
    opts=pulumi.ResourceOptions(parent=instance),
)

# Setup Outputs
pulumi.export('Database Instance Name', instance.name)
pulumi.export('Database Instance IP', instance.private_ip_address)
pulumi.export('Database User', user.name)
pulumi.export('Database Name', database.name)
pulumi.export('Database Secret', secret.name)
pulumi.export('Database Bucket', db_bucket.name)
