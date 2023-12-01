import pulumi
import pulumi_gcp as gcp

# Setup Vars
config = pulumi.Config()
zone = config.require('zone')
folder_id = config.require('folderId')
billing_account = config.require_secret('billing-account')
pulumi_stack = pulumi.get_stack()

# APIs to Enable
apis = [
    'secretmanager.googleapis.com',
    'compute.googleapis.com',
    'servicenetworking.googleapis.com',
    'run.googleapis.com',
    'sqladmin.googleapis.com',
    'artifactregistry.googleapis.com',
    'iamcredentials.googleapis.com',
    'cloudresourcemanager.googleapis.com',
]

# Setup Project
folder = gcp.organizations.get_folder(folder=f'{folder_id}')

project = gcp.organizations.Project(
    f'wordpress-{pulumi_stack}',
    project_id=f'etc-wordpress-site-{pulumi_stack}',
    folder_id=folder.name,
    billing_account=billing_account,
)

# Enable APIs
for api in apis:
    service = gcp.projects.Service(
        api,
        service=api,
        project=project.project_id,
        opts=pulumi.ResourceOptions(parent=project),
    )

restricted_sharing_policy = gcp.projects.OrganizationPolicy(
    'org-policy-restricted-domains',
    list_policy=gcp.projects.OrganizationPolicyListPolicyArgs(
        inherit_from_parent=False,
        allow=gcp.projects.OrganizationPolicyListPolicyAllowArgs(
            all=True,
        ),
    ),
    constraint='sql.restrictPublicIp',
    project=project.project_id,
    opts=pulumi.ResourceOptions(parent=project, delete_before_replace=True),
)
# Setup Outputs
pulumi.export('project-name', project.name)
pulumi.export('project-id', project.project_id)
