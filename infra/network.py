import pulumi
import pulumi_gcp as gcp

from project import project, service

# Setup Config
config = pulumi.Config('network')

# Setup VPC
network_name = config.get('vpc_name')
network = gcp.compute.Network(
    network_name,
    name=network_name,
    project=project.project_id,
    auto_create_subnetworks=False,
    opts=pulumi.ResourceOptions(depends_on=[service]),
)

subnet = gcp.compute.Subnetwork(
    'public-subnet',
    name='subnet',
    ip_cidr_range='10.0.1.0/24',
    network=network.id,
    project=project.project_id,
    opts=pulumi.ResourceOptions(parent=network),
)

# Setup Outputs
pulumi.export('vpc', network.name)
pulumi.export(
    'subnet',
    pulumi.Output.all(subnet.name, subnet.ip_cidr_range).apply(
        lambda subnet: f'{subnet[0]}; {subnet[1]}'
    ),
)
