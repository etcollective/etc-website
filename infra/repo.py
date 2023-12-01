import pulumi
import pulumi_gcp as gcp
import pulumi_google_native as gcp_native

from project import project, pulumi_stack

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
)

docker_tag = gcp_native.artifactregistry.v1beta2.get_tag(
    location=region,
    tag_id='latest',
    repository_id=docker_repo.repository_id,
    package_id='website',
)

# Setup Outputs
pulumi.export('Artifact Registry Repo', docker_repo.id)
pulumi.export('Docker Tag', docker_tag.name)
