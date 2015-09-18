import uuid

from cs import CloudStack

from heat.engine import properties
from heat.engine import resource
from gettext import gettext as _
from base64 import b64encode

__author__ = 'cima'

API_ENDPOINT = ''
API_KEY = ''
API_SECRET = ''


class CloudstackVirtualMachine(resource.Resource):
    PROPERTIES = (
        SERVICE_OFFERING_ID,
        TEMPLATE_ID,
        ZONE_ID,
        USER_DATA,
        KEY_PAIR) = (
        'service_offering_id',
        'template_id',
        'zone_id',
        'user_data',
        'key_pair')

    properties_schema = {
        SERVICE_OFFERING_ID: properties.Schema(
            properties.Schema.STRING,
            _('Service offering ID'),
            True
        ),
        TEMPLATE_ID: properties.Schema(
            properties.Schema.STRING,
            _('Template ID'),
            True
        ),
        ZONE_ID: properties.Schema(
            properties.Schema.STRING,
            _('Zone ID'),
            True
        ),
        USER_DATA: properties.Schema(
            properties.Schema.STRING,
            _('User data script'),
            False
        ),
        KEY_PAIR: properties.Schema(
            properties.Schema.STRING,
            _('Name of the ssh keypair to login to the VM'),
            False
        )
    }

    def _get_cloudstack(self):
        cs = CloudStack(endpoint=API_ENDPOINT,
                        key=API_KEY,
                        secret=API_SECRET)
        return cs

    def handle_create(self):
        cs = self._get_cloudstack()

        serviceofferingid = self.properties.get(self.SERVICE_OFFERING_ID)
        templateid = self.properties.get(self.TEMPLATE_ID)
        zoneid = self.properties.get(self.ZONE_ID)
        userdata = self.properties.get(self.USER_DATA)
        keypair = self.properties.get(self.KEY_PAIR)

        vm = cs.deployVirtualMachine(serviceofferingid=serviceofferingid,
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

        cs.destroyVirtualMachine(id=self.resource_id)

    def check_delete_complete(self, _compute_id):
        cs = self._get_cloudstack()

        vm = cs.listVirtualMachines(id=self.resource_id)
        if vm:
            return False

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


def resource_mapping():
    mappings = {}

    mappings['Cloudstack::Compute::VirtualMachine'] = CloudstackVirtualMachine

    return mappings
