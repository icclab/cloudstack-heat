__author__ = 'cima'

import uuid

from cs import CloudStack

from heat.engine import properties
from heat.engine import resource

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
        cs = self._get_cloustack()

        serviceofferingid = self.properties.get(self.SERVICE_OFFERING_ID)
        templateid = self.properties.get(self.TEMPLATE_ID)
        zoneid = self.properties.get(self.ZONE_ID)

        vm = cs.deployVirtualMachine(serviceofferingid=serviceofferingid,
                                     templateid=templateid,
                                     zoneid=zoneid)

        self.resource_id_set(vm.id)
        return vm.uuid

    def handle_delete(self): 
        cs = self._get_cloustack()

        if self.resource_id in None:
            return

        cs.destroyVirtualMachine(self.resource_id)

def resource_mapping():
    mappings = {}

    mappings['Cloudstack::Compute::VirtualMachine'] = CloudstackVirtualMachine

