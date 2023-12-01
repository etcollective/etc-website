import pulumi
import pulumi_gcp as gcp
import pulumi_google_native as gcp_native
import pulumi_cloudflare as cloudflare

from cloud_run import region, service
from project import project, pulumi_stack

# Setup Vars
config = pulumi.Config()
zone = config.get('zone')
stack_name = pulumi.get_stack()

# Build Desired Domain
domain_name = zone if 'production' in stack_name else f'{stack_name}.{zone}'

# Setup Cloud Run Domain Mapping
wp_domain_mapping = gcp.cloudrun.DomainMapping(
    f'{pulumi_stack}-wp-domain-mapping',
    name=domain_name,
    location=service.location,
    project=service.project,
    metadata=gcp.cloudrun.DomainMappingMetadataArgs(
        namespace=service.project,
    ),
    spec=gcp.cloudrun.DomainMappingSpecArgs(
        route_name=service.name,
    ),
    opts=pulumi.ResourceOptions(parent=service, depends_on=[service]),
)

# Setup Outputs
url = wp_domain_mapping.name.apply(lambda url: f'https://{url}')
pulumi.export('Cloud Run Domain Mapping', url)
