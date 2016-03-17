from oslo_config import cfg
from oslo_log import log as logging
from nca47.common.i18n import _
from nca47.common.i18n import _LI
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
    cfg.StrOpt('user_id',
               default='admin',
               help=_('The TCP view_id on which nca47-zdns_driver listens.')),
    cfg.StrOpt('password',
               default='zdns',
               help=_('The TCP view_id on which nca47-zdns_driver listens.')),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='zdns_agent',
                         title='Options for the nca47-zdns_driver service')
CONF.register_group(opt_group)
CONF.register_opts(ZONES_AGENT_OPTS, opt_group)


class dns_zone_driver():
    def __init__(self):
        self.host = 'http://' + CONF.zdns_agent.host_ip
        self.port = CONF.zdns_agent.port
        self.view_id = CONF.zdns_agent.view_id

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
        zone = self.make_zone_object(zone.as_dict())
        data = json.dumps(zone)
        LOG.info(_LI("create zones:"+url))
        request = requests.post(url, data=data,
                                headers=headers, verify=False)
        return request.json()

    def update_zone_owners(self, context, zone, zone_id):
        """   update zones  owners    """
        url = (self.host + ":" + str(self.port) + '/views/' +
               self.view_id + '/zones/' + zone_id + '/owners')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(zone)
        LOG.info(_LI("update zones owners:"+url))
        request = requests.get(url, data=data,
                               headers=headers, verify=False)
        return request.json()

    def update_zone(self, context, zone, zone_id):
        """   update zones    """
        url = (self.host + '/zones/' + str(self.port) +
               '/views/' + self.view_id + '/zones/' + zone_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(zone)
        LOG.info(_LI("update zones :"+url))
        request = requests.put(url=url, data=data,
                               headers=headers, verify=False)
        return request.json()

    def delete_zone(self, context, zone, zone_id):
        """   delete zones    """
        url = (self.host + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(zone)
        LOG.info(_LI("delete zones :"+url))
        request = requests.delete(url, data=data,
                                  headers=headers, verify=False)
        return request.json()

    def create_rrs(self, context, rrs, zone_id):
        """   create zones    """
        url = (str(self.host) + str(self.port) + '/views/' + self.view_id +
               '/zones/' + str(zone_id) + '/rrs')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(rrs)
        LOG.info(_LI("create rrs:"+url))
        request = requests.post(url, data=data,
                                headers=headers, verify=False)
        return request.json()

    def update_rrs(self, context, rrs, zone_id, rrs_id):
        """   update rrs    """
        url = (self.host + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs' + rrs_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(rrs)
        LOG.info(_LI("create rrs:"+url))
        request = requests.put(url, data=data,
                               headers=headers, verify=False)
        return request

    def delete_rrs(self, context, rrs, zone_id, rrs_id):
        """   delete rrs    """
        url = (self.host + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs' + rrs_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(rrs)
        LOG.info(_LI("delete rrs :"+url))
        request = requests.delete(url, data=data,
                                  headers=headers, verify=False)
        return request.json()

    def del_cache(self, context, cache_dic):
        """   delete cache    """
        url = (self.host + str(self.port) + '/cache/clean')
        LOG.info(_LI("delete cache :"+url))
        headers = {'Content-type': 'application/json'}
        request = requests.post(url, data=cache_dic,
                                headers=headers, verify=False)
        return request.json()

    def get_zone_one(self, context, zone, zone_id):
        """   view one zone     """
        url = (self.host + '/zones/' + str(self.port) +
               '/views/' + self.view_id + '/zones/' + zone_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(zone)
        LOG.info(_LI("view one zone :"+url))
        request = requests.get(url, data=data,
                               headers=headers, verify=False)
        return request.json()

    def get_zone(self, context, zone):
        """   view all zone     """
        url = (self.host + '/zones/' + str(self.port) +
               '/views/' + self.view_id + '/zones/')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(zone)
        LOG.info(_LI("view all zone :"+url))
        request = requests.get(url, data=data,
                               headers=headers, verify=False)
        return request.json()

    def get_rrs(self, context, rrs, zone_id):
        """   view rrs    """
        url = (self.host + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(rrs)
        LOG.info(_LI("view rrs :"+url))
        request = requests.get(url, data=data,
                               headers=headers, verify=False)
        return request.json()

    def make_zone_object(self, zone_dict):
        target_values = {}
        for k in zone_dict:
            if k == "zone_name":
                target_values['name'] = zone_dict[k]
            else:
                target_values[k] = zone_dict[k]
        return target_values
