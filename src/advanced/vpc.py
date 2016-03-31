from cs import CloudStack
from cs import CloudStackException

from heat.engine import properties
from heat.engine import resource
from gettext import gettext as _

__author__ = 'cima'


class CloudstackVPC(resource.Resource):
    PROPERTIES = (
        API_ENDPOINT,
        API_KEY,
        API_SECRET,
        NAME,
        DISPLAY_TEXT,
        ZONE_ID,
        VPC_OFFERING_ID,
        CIDR) = (
        'api_endpoint',
        'api_key',
        'api_secret',
        'name',
        'display_text',
        'zone_id',
        'vpc_offering_id',
        'cidr')

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
            description=_('VPC name'),
            required=True
        ),
        DISPLAY_TEXT: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('VPC display text'),
            required=True
        ),
        ZONE_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('Zone id'),
            required=True
        ),
        VPC_OFFERING_ID: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('VPC offering id'),
            required=True
        ),
        CIDR: properties.Schema(
            data_type=properties.Schema.STRING,
            description=_('VPC CIDR'),
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

        zoneid = self.properties.get(self.ZONE_ID)
        vpcofferingid = self.properties.get(self.VPC_OFFERING_ID)
        name = self.properties.get(self.NAME)
        displaytext = self.properties.get(self.DISPLAY_TEXT)
        cidr = self.properties.get(self.CIDR)

        vpc = cs.createVPC(
            name=name,
            displaytext=displaytext,
            vpcofferingid=vpcofferingid,
            zoneid=zoneid,
            cidr=cidr
        )

        self.resource_id_set(vpc['id'])
        return vpc['id']

    def check_create_complete(self, _compute_id):
        cs = self._get_cloudstack()

        vpc = cs.listVPCs(id=self.resource_id)
        if vpc:
            return True

        return False

    def handle_update(self, json_snippet=None, tmpl_diff=None, prop_diff=None):
        # TODO
        pass

    def check_update_complete(self):
        # TODO
        pass

    def handle_delete(self):
        cs = self._get_cloudstack()

        if self.resource_id is None:
            return
        try:
            cs.deleteVPC(id=self.resource_id)
        except CloudStackException as e:
            raise e

    def check_delete_complete(self, _compute_id):
        cs = self._get_cloudstack()
        vpc = None
        try:
            vpc = cs.listVPCs(id=self.resource_id)
        except CloudStackException as e:
            if e.args[2]['errorcode'] == 431:
                # Resource cannot be found
                # One thing less...
                return True
            raise e
        if vpc:
            return False
        else:
            return True

    def _resolve_attribute(self, name):
        cs = self._get_cloudstack()

        vpc = cs.listVPCs(id=self.resource_id)
        if vpc:
            if name == 'id':
                return vpc['vpc'][0]['id']
            return getattr(vpc, name)

    attributes_schema = {
        'id': _('id')
    }


def resource_mapping():
    mappings = {}
    mappings['Cloudstack::Network::VPC'] = CloudstackVPC
    return mappings
