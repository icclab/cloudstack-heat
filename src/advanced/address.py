from cs import CloudStack

from heat.engine import properties
from heat.engine import resource
from gettext import gettext as _

from time import sleep

__author__ = 'cima'


class CloudstackAddress(resource.Resource):
    PROPERTIES = (
        API_ENDPOINT,
        API_KEY,
        API_SECRET,
        VPC_ID,
        VIRTUAL_MACHINE_ID,
        NETWORK_ID) = (
        'api_endpoint',
        'api_key',
        'api_secret',
        'vpc_id',
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
        VPC_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('VPC ID'),
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
            required=True
        )
    }

    def _get_cloudstack(self):
        cs = CloudStack(endpoint=self.properties.get(self.API_ENDPOINT),
                        key=self.properties.get(self.API_KEY),
                        secret=self.properties.get(self.API_SECRET))
        return cs

    def handle_create(self):
        cs = self._get_cloudstack()

        vpcid = self.properties.get(self.VPC_ID)
        virtualmachineid = self.properties.get(self.VIRTUAL_MACHINE_ID)
        networkid = self.properties.get(self.NETWORK_ID)

        address = cs.associateIpAddress(vpcid=vpcid)

        ipaddressid = address['id']

        # Wait for network ro be created
        # FIXME: More elegant wait of waiting
        # for IP to be properly associated
        sleep(1)

        cs.enableStaticNat(
            ipaddressid=ipaddressid,
            virtualmachineid=virtualmachineid,
            networkid=networkid)

        self.resource_id_set(ipaddressid)
        return ipaddressid

    def check_create_complete(self, _compute_id):
        # TODO: Add more sofisticated condition
        return True

    def handle_delete(self):
        cs = self._get_cloudstack()

        if self.resource_id is None:
            return

        cs.disassociateIpAddress(id=self.resource_id)

    def check_delete_complete(self, _compute_id):
        # TODO: Add more sofisticated condition
        return True

    def _resolve_attribute(self, name):
        cs = self._get_cloudstack()

        address = cs.listPublicIpAddresses(id=self.resource_id)
        if address:
            if name == 'id':
                return address['publicipaddress'][0]['id']
            if name == 'ipaddress':
                return address['publicipaddress'][0]['ipaddress']
            return getattr(address, name)

    attributes_schema = {
        'id': _('id'),
        'ipaddress': _('ipaddress')
    }


def resource_mapping():
    mappings = {}
    mappings['Cloudstack::Network::Address'] = CloudstackAddress
    return mappings
