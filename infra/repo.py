import pulumi
import pulumi_docker as docker
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

# Build Repo URL
repo_url = pulumi.Output.all(
    region, project.project_id, docker_repo.name
).apply(lambda url: f'{url[0]}-docker.pkg.dev/{url[1]}/{url[2]}')

# Build and Push Image
docker_image = docker.Image(
    'wordpress-image',
    build=docker.DockerBuildArgs(
        context='../', dockerfile='../Dockerfile', platform='linux/amd64'
    ),
    image_name=repo_url.apply(lambda url: f'{url}/website:latest'),
    opts=pulumi.ResourceOptions(parent=docker_repo),
)

# Setup Outputs
pulumi.export('Artifact Registry Repo', docker_repo.id)
pulumi.export('Docker Image', docker_image.image_name)
