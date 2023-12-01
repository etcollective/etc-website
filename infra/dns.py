import pulumi
import pulumi_gcp as gcp
from cloud_run import region, service
from project import project, pulumi_stack

# Setup Vars
config = pulumi.Config()
zone = config.get('zone')

wp_domain_mapping = gcp.cloudrun.DomainMapping(
    f'{pulumi_stack}-wp-domain-mapping',
    name=f'{pulumi_stack}.{zone}',
    location=region,
    project=project.project_id,
    metadata=gcp.cloudrun.DomainMappingMetadataArgs(
        namespace=project.project_id,
    ),
    spec=gcp.cloudrun.DomainMappingSpecArgs(
        route_name=service.name,
    ),
    opts=pulumi.ResourceOptions(parent=service, depends_on=[service]),
)

# Setup Outputs
url = wp_domain_mapping.name.apply(lambda url: f'https://{url}')
pulumi.export('Cloud Run Domain Mapping', url)
