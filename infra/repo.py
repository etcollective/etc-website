import pulumi
import pulumi_gcp as gcp

from project import project, pulumi_stack, service

# Setup Vars
gcp_config = pulumi.Config('gcp')
region = gcp_config.get('region')

# Setup Repo
docker_repo = gcp.artifactregistry.Repository(
    'docker_repo',
    format='DOCKER',
    location=region,
    project=project.project_id,
    repository_id=f'website-{pulumi_stack}',
    opts=pulumi.ResourceOptions(depends_on=[service]),
)

# Setup Outputs
pulumi.export('Artifact Registry Repo', docker_repo.id)
