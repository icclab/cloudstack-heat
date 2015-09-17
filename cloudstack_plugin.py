import uuid

from cs import CloudStack

from heat.engine import properties
from heat.engine import resource
from gettext import gettext as _

__author__ = 'cima'

API_ENDPOINT = ''
API_KEY = ''
API_SECRET = ''


class CloudstackVirtualMachine(resource.Resource):
    PROPERTIES = (SERVICE_OFFERING_ID, TEMPLATE_ID, ZONE_ID) = \
        ('service_offering_id', 'template_id', 'zone_id')

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

        vm = cs.deployVirtualMachine(serviceofferingid=serviceofferingid,
                                     templateid=templateid,
                                     zoneid=zoneid)

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

        cs.stopVirtualMachine(self.resource_id)

    def check_suspend_complete(self, _compute_id):
        # TODO
        pass

    def handle_resume(self):
        cs = self._get_cloudstack()

        if self.resource_id is None:
            return

        cs.startVirtualMachine(self.resource_id)

    def check_resume_complete(self, _compute_id):
        # TODO
        pass

'''
class CloudstackNetwork(resource.Resource):
    PROPERTIES = (DISPLAY_TEXT, NAME, NETWORK_OFFERING_ID, ZONE_ID) = \
        ('display_text', 'name', 'network_offering_id', 'zone_id')

    properties_schema = {
        DISPLAY_TEXT: properties.Schema(
            properties.Schema.STRING,
            _('The display text of the network'),
            True
        ),
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('The name of the network'),
            True
        ),
        NETWORK_OFFERING_ID: properties.Schema(
            properties.Schema.STRING,
            _('Network offering ID'),
            True
        ),
        ZONE_ID: properties.Schema(
            properties.Schema.STRING,
            _('Zone ID'),
            True
        )
    }

    def _get_cloudstack(self):
        cs = CloudStack(endpoint=API_ENDPOINT,
                        key=API_KEY,
                        secret=API_SECRET)
        return cs

    def handle_create(self):
        cs = self._get_cloudstack()

        displaytext = self.properties.get(self.DISPLAY_TEXT)
        name = self.properties.get(self.NAME)
        networkofferingid = self.properties.get(self.NETWORK_OFFERING_ID)
        zoneid = self.properties.get(self.ZONE_ID)

        network = cs.createNetwork(displaytext=displaytext,
                                   name=name,
                                   networkofferingid=networkofferingid
                                   zoneid=zoneid)

        self.resource_id_set(network.id)
        return network.id

    def check_create_complete(self, _compute_id):
        # TODO
        pass

    def handle_delete(self):
        cs = self._get_cloudstack()

        if self.resource_id in None:
            return

        cs.deleteNetwork(self.resource_id)

    def check_delete_complete(self, _compute_id):
        # TODO
        pass
'''


def resource_mapping():
    mappings = {}

    mappings['Cloudstack::Compute::VirtualMachine'] = CloudstackVirtualMachine
#    mappings['Cloudstack::Network::Network'] = CloudstackNetwork

    return mappings
