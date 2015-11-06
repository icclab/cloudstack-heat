from cs import CloudStack
from cs import CloudStackException

from heat.engine import properties
from heat.engine import resource
from gettext import gettext as _

__author__ = 'cima'


class CloudstackNetwork(resource.Resource):
    PROPERTIES = (
        API_ENDPOINT,
        API_KEY,
        API_SECRET,
        NAME,
        DISPLAY_TEXT,
        ZONE_ID,
        NETWORK_OFFERING_ID,
        VPC_ID,
        ACL_ID,
        GATEWAY,
        NETMASK) = (
        'api_endpoint',
        'api_key',
        'api_secret',
        'name',
        'display_text',
        'zone_id',
        'network_offering_id',
        'vpc_id',
        'acl_id',
        'gateway',
        'netmask')

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
            description=_('The name of the network'),
            required=True
        ),
        DISPLAY_TEXT: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('The displaytext for the network'),
            required=True
        ),
        ZONE_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('The zone id'),
            required=True
        ),
        NETWORK_OFFERING_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('The network offering id'),
            required=True
        ),
        VPC_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('VPC ID'),
            required=True
        ),
        ACL_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('ACL id'),
            required=True
        ),
        GATEWAY: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Network gateway'),
            required=True
        ),
        NETMASK: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Network netmask'),
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

        displaytext = self.properties.get(self.DISPLAY_TEXT)
        zoneid = self.properties.get(self.ZONE_ID)
        networkofferingid = self.properties.get(self.NETWORK_OFFERING_ID)
        vpcid = self.properties.get(self.VPC_ID)
        name = self.properties.get(self.NAME)
        gateway = self.properties.get(self.GATEWAY)
        netmask = self.properties.get(self.NETMASK)
        aclid = self.properties.get(self.ACL_ID)

        network = cs.createNetwork(
            name=name,
            displaytext=displaytext,
            networkofferingid=networkofferingid,
            zoneid=zoneid,
            gateway=gateway,
            netmask=netmask,
            aclid=aclid,
            vpcid=vpcid
        )

        self.resource_id_set(network['network']['id'])
        return network['network']['id']

    def check_create_complete(self, _compute_id):
        cs = self._get_cloudstack()

        sg = cs.listNetworks(id=self.resource_id)
        if sg:
            return True

        return False

    def handle_delete(self):
        cs = self._get_cloudstack()

        if self.resource_id is None:
            return
        try:
            cs.deleteNetwork(id=self.resource_id)
        except CloudStackException as e:
            print e

    def check_delete_complete(self, _compute_id):
        cs = self._get_cloudstack()
        network = None
        try:
            network = cs.listNetworks(id=self.resource_id)
        except CloudStackException as e:
            if e.args[2]['errorcode'] == 431:
                # Resource cannot be found
                # One thing less...
                return True
            print e
        if network:
            return False
        else:
            return True

    def _resolve_attribute(self, name):
        cs = self._get_cloudstack()

        network = cs.listNetworks(id=self.resource_id)
        if network:
            if name == 'id':
                return network['network'][0]['id']
            return getattr(network, name)

    attributes_schema = {
        'id': _('id')
    }


def resource_mapping():
    mappings = {}
    mappings['Cloudstack::Network::Network'] = CloudstackNetwork
    return mappings
