from cs import CloudStack
from cs import CloudStackException

from heat.engine import properties
from heat.engine import resource
from gettext import gettext as _
from time import sleep

__author__ = 'cima'


class CloudstackSecurityGroup(resource.Resource):
    PROPERTIES = (
        API_ENDPOINT,
        API_KEY,
        API_SECRET,
        NAME,
        RULES) = (
        'api_endpoint',
        'api_key',
        'api_secret',
        'name',
        'rules')

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
            description=_('The name of the security group'),
            required=True
        ),
        RULES: properties.Schema(
            data_type=properties.Schema.LIST,
            description=_('List of ingress / egress rules'),
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

        name = self.properties.get(self.NAME)
        rules = self.properties.get(self.RULES)

        sg = cs.createSecurityGroup(name=name)

        sg_id = sg['securitygroup']['id']

        for rule in rules:
            if rule.get('direction', 'ingress') == 'ingress':
                cs.authorizeSecurityGroupIngress(
                    securitygroupid=sg_id,
                    startport=rule.get('startport', None),
                    endport=rule.get('endport', None),
                    cidrlist=rule.get('cidr', '0.0.0.0/0'),
                    protocol=rule.get('protocol', 'tcp'))
            elif rule.get('direction', 'ingress') == 'egress':
                cs.authorizeSecurityGroupEgress(
                    securitygroupid=sg_id,
                    startport=rule.get('startport', None),
                    endport=rule.get('endport', None),
                    cidrlist=rule.get('cidr', '0.0.0.0/0'),
                    protocol=rule.get('protocol', 'tcp'))

        self.resource_id_set(sg_id)
        return sg_id

    def check_create_complete(self, _compute_id):
        cs = self._get_cloudstack()

        sg = cs.listSecurityGroups(id=self.resource_id)
        if sg:
            return True

        return False

    def handle_delete(self):
        cs = self._get_cloudstack()

        if self.resource_id is None:
            return
        try:
            cs.deleteSecurityGroup(id=self.resource_id)
        except CloudStackException as e:
            if e.args[2]['errorcode'] == 536:
                # Delete failed - cannot delete group when
                # it's in use by virtual machines
                # just wait for a while and try again
                sleep(10)
                self.handle_delete()
            print e

    def check_delete_complete(self, _compute_id):
        cs = self._get_cloudstack()
        sg = None
        try:
            sg = cs.listSecurityGroups(id=self.resource_id)
        except CloudStackException as e:
            if e.args[2]['errorcode'] == 431:
                # Resource cannot be found
                # One thing less...
                return True
            print e
        if sg:
            return False
        else:
            return True

    def _resolve_attribute(self, name):
        cs = self._get_cloudstack()

        sg = cs.listSecurityGroups(id=self.resource_id)
        if sg:
            if name == 'id':
                return sg['securitygroup'][0]['id']
            return getattr(sg, name)

    attributes_schema = {
        'id': _('id')
    }


def resource_mapping():
    mappings = {}
    mappings['Cloudstack::Network::SecurityGroup'] = CloudstackSecurityGroup
    return mappings
