from oslo_config import cfg
from oslo_log import log as logging
from nca47.common.i18n import _
from nca47.common.i18n import _LI
from nca47.common.exception_zdns import ZdnsErrMessage
from nca47.common.exception import NonExistDevices
import requests
import json
CONF = cfg.CONF
LOG = logging.getLogger(__name__)

DNS_DRIVER = None

ZONES_AGENT_OPTS = [
    cfg.StrOpt('host_ip',
               default='0.0.0.0',
               help=_('The IP address on which nca47-zdns_driver listens.')),
    cfg.PortOpt('port',
                default=20120,
                help=_('The TCP port on which nca47-zdns_driver listens.')),
    cfg.StrOpt('view_id',
               default='telecom',
               help=_('The TCP view_id on which nca47-zdns_driver listens.')),
    cfg.StrOpt('auth_name',
               default='admin',
               help=_('The TCP auth_name on which nca47-zdns_driver'
                      'listens.')),
    cfg.StrOpt('auth_pw',
               default='zdns',
               help=_('The TCP auth_pw on which nca47-zdns_driver listens.')),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='zdns_agent',
                         title='Options for the nca47-zdns_driver service')
CONF.register_group(opt_group)
CONF.register_opts(ZONES_AGENT_OPTS, opt_group)


class dns_zone_driver():
    def __init__(self):
        self.host = 'https://' + CONF.zdns_agent.host_ip
        self.port = CONF.zdns_agent.port
        self.view_id = CONF.zdns_agent.view_id
        self.auth_name = CONF.zdns_agent.auth_name
        self.auth_pw = CONF.zdns_agent.auth_pw

    @classmethod
    def get_instance(cls):
        global DNS_DRIVER
        if not DNS_DRIVER:
            DNS_DRIVER = cls()
        return DNS_DRIVER

    def create_zone(self, context, zone):
        """   create zones    """
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(zone)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create zones:"+url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def update_zone_owners(self, context, zone, zone_id):
        """   update zones  owners    """
        url = (self.host + ":" + str(self.port) + '/views/' +
               self.view_id + '/zones/' + zone_id + '/owners')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(zone)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("update zones owners:"+url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def update_zone(self, context, zone, zone_id):
        """   update zones    """
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones/' + zone_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(zone)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("update zones :"+url))
        response = requests.put(url=url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def delete_zone(self, context, zone, zone_id):
        """   delete zones    """
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(zone)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete zones :"+url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def create_rrs(self, context, rrs, zone_id):
        """   create zones    """
        url = (str(self.host) + ":" + str(self.port) + '/views/' +
               self.view_id + '/zones/' + str(zone_id) + '/rrs')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(rrs)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create rrs:"+url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def update_rrs(self, context, rrs, zone_id, rrs_id):
        """   update rrs    """
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs/' + rrs_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(rrs)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create rrs:"+url))
        response = requests.put(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def delete_rrs(self, context, rrs, zone_id, rrs_id):
        """   delete rrs    """
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs/' + rrs_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(rrs)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete rrs :"+url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def del_cache(self, context, cache_dic):
        """   delete cache    """
        url = (self.host + ":" + str(self.port) + '/cache/clean')
        LOG.info(_LI("delete cache :"+url))
        headers = {'Content-type': 'application/json'}
        auth = (self.auth_name, self.auth_pw)
        response = requests.post(url, data=cache_dic,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def get_zone_one(self, context, zone_id):
        """   view one zone     """
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones/' + zone_id)
        headers = {'Content-type': 'application/json'}
        LOG.info(_LI("view one zone :"+url))
        auth = (self.auth_name, self.auth_pw)
        response = requests.get(url, data={"current_user": "admin"},
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def get_zones(self, context):
        """   view all zone     """
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones')
        LOG.info(_LI("view all zone :" + url))
        params = {'current_user': 'admin'}
        auth = (self.auth_name, self.auth_pw)
        response = requests.get(url, data=params,
                                auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()

    def get_rrs(self, context, rrs, zone_id):
        """   view rrs    """
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs')
        params = {'current_user': 'admin'}
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("view rrs :"+url))
        response = requests.get(url, data=params,
                                auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(response.status_code)
        return response.json()
