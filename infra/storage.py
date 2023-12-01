import pulumi
import pulumi_gcp as gcp
from project import project

# Setup Vars
gcp_config = pulumi.Config('gcp')
region = gcp_config.get('region')
stack = pulumi.get_stack()

# Setup Bucket
assets_bucket = gcp.storage.Bucket(
    'assets-bucket',
    location=region,
    name=f'{stack}-website-assets',
    project=project.project_id,
    opts=pulumi.ResourceOptions(protect=False),
)

allow_public_access = gcp.storage.BucketIAMBinding(
    'assets-bucket-public-access',
    bucket=assets_bucket.name,
    role='roles/storage.objectViewer',
    members=[
        'allUsers',
        'allAuthenticatedUsers'
    ],
    opts=pulumi.ResourceOptions(parent=assets_bucket)
)

# Setup IAM Permissions
service_account = gcp.serviceaccount.Account(
    'assets-bucket-service-account',
    account_id=f'{stack}-wp-stateless',
    display_name=f'{stack} WP-Stateless',
    project=project.project_id,
    opts=pulumi.ResourceOptions(parent=assets_bucket, depends_on=[assets_bucket])
)

sa_binding = gcp.storage.BucketIAMBinding(
    'assets-bucket-iam-binding',
    bucket=assets_bucket.name,
    role='roles/storage.admin',
    members=[
        service_account.email.apply(lambda email: f'serviceAccount:{email}')
    ],
    opts=pulumi.ResourceOptions(parent=service_account)
)

# Setup Outputs
pulumi.export('web-assets-bucket', assets_bucket.name)
pulumi.export('wp-stateless-serviceaccount', service_account.email)
