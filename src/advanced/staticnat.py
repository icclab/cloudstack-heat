from cs import CloudStack

from heat.engine import properties
from heat.engine import resource
from gettext import gettext as _

__author__ = 'cima'


class CloudstackStaticNAT(resource.Resource):
    PROPERTIES = (
        API_ENDPOINT,
        API_KEY,
        API_SECRET,
        IP_ADDRESS_ID,
        VIRTUAL_MACHINE_ID,
        NETWORK_ID) = (
        'api_endpoint',
        'api_key',
        'api_secret',
        'ip_address_id',
        'virtual_machine_id',
        'network_id')

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
        IP_ADDRESS_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('IP address ID'),
            required=True
        ),
        VIRTUAL_MACHINE_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('VM ID'),
            required=True
        ),
        NETWORK_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Network ID'),
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

        virtualmachineid = self.properties.get(self.VIRTUAL_MACHINE_ID)
        ipaddressid = self.properties.get(self.IP_ADDRESS_ID)
        networkid = self.properties.get(self.NETWORK_ID)

        cs.enableStaticNat(
            ipaddressid=ipaddressid,
            virtualmachineid=virtualmachineid,
            networkid=networkid)

        return ipaddressid

    def check_create_complete(self, _compute_id):
        # TODO: Add more sofisticated condition
        return True

    def handle_delete(self):
        # Nothing to do here as NAT resource does not have id
        pass

    def check_delete_complete(self, _compute_id):
        # TODO: Add more sofisticated condition
        return True

    def _resolve_attribute(self, name):
        pass


def resource_mapping():
    mappings = {}
    mappings['Cloudstack::Network::StaticNAT'] = CloudstackStaticNAT
    return mappings
