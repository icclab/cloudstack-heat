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
        NAME,
        SERVICE_OFFERING_ID,
        TEMPLATE_ID,
        ZONE_ID,
        USER_DATA,
        KEY_PAIR,
        SECURITY_GROUP_IDS,
        NETWORK_IDS,
        IPADDRESS) = (
        'api_endpoint',
        'api_key',
        'api_secret',
        'name',
        'service_offering_id',
        'template_id',
        'zone_id',
        'user_data',
        'key_pair',
        'security_group_ids',
        'network_ids',
        'ipaddress')

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
        NAME: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Virtual machine hostname'),
            required=False
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
        ),
        IPADDRESS: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('VM IP address'),
            required=False
        )
    }

    def _get_cloudstack(self, method='get'):
        cs = CloudStack(endpoint=self.properties.get(self.API_ENDPOINT),
                        key=self.properties.get(self.API_KEY),
                        secret=self.properties.get(self.API_SECRET),
                        method=method)
        return cs

    def handle_create(self):
        # use post to be able to inject up to 64k user data
        cs = self._get_cloudstack(method='post')

        params = {}

        params['serviceofferingid'] = self.properties.get(
            self.SERVICE_OFFERING_ID)
        params['templateid'] = self.properties.get(self.TEMPLATE_ID)
        params['zoneid'] = self.properties.get(self.ZONE_ID)

        if self.properties.get(self.USER_DATA):
            params['userdata'] = b64encode(self.properties.get(self.USER_DATA))
        if self.properties.get(self.KEY_PAIR):
            params['keypair'] = self.properties.get(self.KEY_PAIR)
        if self.properties.get(self.SECURITY_GROUP_IDS):
            params['securitygroupids'] = self.properties.get(
                self.SECURITY_GROUP_IDS)
        if self.properties.get(self.NETWORK_IDS):
            params['networkids'] = self.properties.get(self.NETWORK_IDS)
        if self.properties.get(self.NAME):
            params['name'] = self.properties.get(self.NAME)
        if self.properties.get(self.IPADDRESS):
            params['ipaddress'] = self.properties.get(self.IPADDRESS)

        vm = cs.deployVirtualMachine(**params)

        self.resource_id_set(vm['id'])
        return vm['id']

    def check_create_complete(self, _compute_id):
        cs = self._get_cloudstack()

        vm = cs.listVirtualMachines(id=self.resource_id)
        if vm:
            if vm['virtualmachine'][0]['state'].lower() == 'running':
                return True

        return False

    def handle_update(self, json_snippet=None, tmpl_diff=None, prop_diff=None):
        # TODO
        pass

    def check_update_complete(self):
        # TODO
        pass

    def handle_delete(self, expunge=True):
        cs = self._get_cloudstack()

        if self.resource_id is None:
            return
        try:
            res = cs.destroyVirtualMachine(id=self.resource_id,
                                           expunge=expunge)
            jobid = res['jobid']
            res = cs.queryAsyncJobResult(jobid=jobid)
            if int(res['jobresultcode']) == 530:
                # try to delete with expunge = False
                self.handle_delete(expunge=False)
        except CloudStackException as e:
            raise e

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
            raise e
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
        'network_ip': _('network_ip')
    }


def resource_mapping():
    mappings = {}
    mappings['Cloudstack::Compute::VirtualMachine'] = CloudstackVirtualMachine
    return mappings
