from cs import CloudStack
from cs import CloudStackException

from heat.engine import properties
from heat.engine import resource
from gettext import gettext as _
from base64 import b64encode

__author__ = 'cima'


class CloudstackVirtualMachine(resource.Resource):
    PROPERTIES = (
        API_ENDPOINT,
        API_KEY,
        API_SECRET,
        SERVICE_OFFERING_ID,
        TEMPLATE_ID,
        ZONE_ID,
        USER_DATA,
        KEY_PAIR,
        SECURITY_GROUP_IDS,
        NETWORK_IDS) = (
        'api_endpoint',
        'api_key',
        'api_secret',
        'service_offering_id',
        'template_id',
        'zone_id',
        'user_data',
        'key_pair',
        'security_group_ids',
        'network_ids')

    properties_schema = {
        API_ENDPOINT: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Cloudstack API endpoint'),
            required=True
        ),
        API_KEY: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('API key'),
            required=True
        ),
        API_SECRET: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('API secret key'),
            required=True
        ),
        SERVICE_OFFERING_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Service offering ID'),
            required=True
        ),
        TEMPLATE_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Template ID'),
            required=True
        ),
        ZONE_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Zone ID'),
            required=True
        ),
        USER_DATA: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('User data script'),
            required=False
        ),
        KEY_PAIR: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Name of the ssh keypair to login to the VM'),
            required=False
        ),
        SECURITY_GROUP_IDS: properties.Schema(
            data_type=properties.Schema.LIST,
            description=_('List of security group ids'),
            required=False
        ),
        NETWORK_IDS: properties.Schema(
            data_type=properties.Schema.LIST,
            description=_('List of network ids'),
            required=False
        )
    }

    def _get_cloudstack(self):
        cs = CloudStack(endpoint=self.properties.get(self.API_ENDPOINT),
                        key=self.properties.get(self.API_KEY),
                        secret=self.properties.get(self.API_SECRET))
        return cs

    def handle_create(self):
        cs = self._get_cloudstack()

        serviceofferingid = self.properties.get(self.SERVICE_OFFERING_ID)
        templateid = self.properties.get(self.TEMPLATE_ID)
        zoneid = self.properties.get(self.ZONE_ID)
        userdata = self.properties.get(self.USER_DATA)
        keypair = self.properties.get(self.KEY_PAIR)
        securitygroupids = self.properties.get(self.SECURITY_GROUP_IDS)
        networkids = self.properties.get(self.NETWORK_IDS)

        if securitygroupids:
            # base zone setup
            vm = cs.deployVirtualMachine(
                serviceofferingid=serviceofferingid,
                templateid=templateid,
                zoneid=zoneid,
                userdata=b64encode(userdata),
                keypair=keypair,
                securitygroupids=securitygroupids)
        elif networkids:
            # advanced zone setup
            vm = cs.deployVirtualMachine(
                serviceofferingid=serviceofferingid,
                templateid=templateid,
                zoneid=zoneid,
                userdata=b64encode(userdata),
                keypair=keypair,
                networkids=networkids)
        else:
            # try default fallback
            vm = cs.deployVirtualMachine(
                serviceofferingid=serviceofferingid,
                templateid=templateid,
                zoneid=zoneid,
                userdata=b64encode(userdata),
                keypair=keypair)

        self.resource_id_set(vm['id'])
        return vm['id']

    def check_create_complete(self, _compute_id):
        cs = self._get_cloudstack()

        vm = cs.listVirtualMachines(id=self.resource_id)
        if vm:
            if vm['virtualmachine'][0]['state'].lower() == 'running':
                return True

        return False

    def handle_delete(self):
        cs = self._get_cloudstack()

        if self.resource_id is None:
            return
        try:
            cs.destroyVirtualMachine(id=self.resource_id,
                                     expunge=True)
        except CloudStackException as e:
            print e

    def check_delete_complete(self, _compute_id):
        cs = self._get_cloudstack()
        vm = None
        try:
            vm = cs.listVirtualMachines(id=self.resource_id)
        except CloudStackException as e:
            if e.args[2]['errorcode'] == 431:
                # Resource cannot be found
                # One thing less...
                return True
            print e
        if vm:
            return False
        else:
            return True

    def handle_suspend(self):
        cs = self._get_cloudstack()

        if self.resource_id is None:
            return

        cs.stopVirtualMachine(id=self.resource_id)

    def check_suspend_complete(self, _compute_id):
        cs = self._get_cloudstack()

        vm = cs.listVirtualMachines(id=self.resource_id)
        if vm:
            if vm['virtualmachine'][0]['state'].lower() == 'stopped':
                return True

        return False

    def handle_resume(self):
        cs = self._get_cloudstack()

        if self.resource_id is None:
            return

        cs.startVirtualMachine(id=self.resource_id)

    def check_resume_complete(self, _compute_id):
        cs = self._get_cloudstack()

        vm = cs.listVirtualMachines(id=self.resource_id)
        if vm:
            if vm['virtualmachine'][0]['state'].lower() == 'running':
                return True

        return False

    def _resolve_attribute(self, name):
        cs = self._get_cloudstack()

        vm = cs.listVirtualMachines(id=self.resource_id)
        if vm:
            if name == 'network_ip':
                return vm['virtualmachine'][0]['nic'][0]['ipaddress']
            if name == 'id':
                return vm['virtualmachine'][0]['id']
            return getattr(vm, name)

    attributes_schema = {
        'id': _('id'),
        'network_ip': _('ip address')
    }


def resource_mapping():
    mappings = {}
    mappings['Cloudstack::Compute::VirtualMachine'] = CloudstackVirtualMachine
    return mappings
