# OpenStack HEAT for Cloudstack

This OpenStack HEAT plugin adds support for CloudStack cloud resources - CloudStack orchestration using OpenStack HEAT!

Uses Exoscale's simple, yet powerful CloudStack API client for python and the command-line. (https://github.com/exoscale/cs)

## Install cs library & Heat plugin
Install cs package:

```
pip install cs
```
 
Copy the heat plugin to /usr/lib/heat:

```
mkdir -p /usr/lib/heat
cp -r src/* /usr/lib/heat/
```

Uncomment ```plugin_dirs``` line in ```/etc/heat/heat.conf```

Restart the heat engine service:

```
service openstack-heat-engine restart
```

Run ```heat resource-type-list``` and verify that Cloudstack resources show up.

## Supported Cloudstack resources:

Basic zone:

```
Cloudstack::Compute::VirtualMachine
Cloudstack::Network::SecurityGroup
```

Advanced zone:

```
Cloudstack::Compute::VirtualMachine
Cloudstack::Network::Network
Cloudstack::Network::VPC
Cloudstack::Network::Address
Cloudstack::Network::StaticNAT
```

Stay tuned! More Cloudstack resources will follow soon!
