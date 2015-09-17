# OpenStack HEAT for Cloudstack
Uses Exoscale's simple, yet powerful CloudStack API client for python and the command-line. (https://github.com/exoscale/cs)

## Install cs library & Heat plugin
Install cs package:

```
pip install cs
```
 
Copy the heat plugin to /usr/lib/heat:

```
mkdir -p /usr/lib/heat
cp cloustack_plugin.py /usr/lib/heat/cloudstack_plugin.py
```

Uncomment ```plugin_dirs``` line in ```/etc/heat/heat.conf```

Restart the heat engine service:

```
service openstack-heat-engine restart
```

Run ```heat resource-type-list```, verify that ```Cloudstack::Compute::CloudstackVirtualMachine``` shows up.

