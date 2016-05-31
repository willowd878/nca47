from oslo_config import cfg
from oslo_log import log as logging
from nca47.common.i18n import _
from nca47.common.i18n import _LI
from nca47.common.exception_zdns import ZdnsErrMessage
from nca47.common.exception import NonExistDevices
from nca47.api.controllers.v1 import tools
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
opt_group = cfg.OptGroup(name='zdns',
                         title='Options for the nca47-zdns_driver service')
CONF.register_group(opt_group)
CONF.register_opts(ZONES_AGENT_OPTS, opt_group)


class dns_zone_driver():
    def __init__(self):
        self.host = 'https://' + CONF.zdns.host_ip
        self.port = CONF.zdns.port
        self.view_id = CONF.zdns.view_id
        self.auth_name = CONF.zdns.auth_name
        self.auth_pw = CONF.zdns.auth_pw
        self.zdns_error = ZdnsErrMessage()

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
        zone["current_user"] = self.auth_name
        data = json.dumps(zone)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create zones:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_zone_owners(self, context, zone, zone_id):
        """   update zones  owners    """
        url = (self.host + ":" + str(self.port) + '/views/' +
               self.view_id + '/zones/' + zone_id + '/owners')
        headers = {'Content-type': 'application/json'}
        zone["current_user"] = self.auth_name
        data = json.dumps(zone)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("update zones owners:" + url))
        response = requests.put(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_zone(self, context, zone, zone_id):
        """   update zones    """
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones/' + zone_id)
        headers = {'Content-type': 'application/json'}
        zone["current_user"] = self.auth_name
        data = json.dumps(zone)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("update zones :" + url))
        response = requests.put(url=url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_zone(self, context, zone_id):
        """   delete zones    """
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id)
        headers = {'Content-type': 'application/json'}
        data = {"current_user": "admin"}
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete zones :" + url))
        response = requests.delete(url, data=data, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def create_rrs(self, context, rrs, zone_id):
        """   create zones    """
        url = (str(self.host) + ":" + str(self.port) + '/views/' +
               self.view_id + '/zones/' + str(zone_id) + '/rrs')
        headers = {'Content-type': 'application/json'}
        rrs["current_user"] = self.auth_name
        data = json.dumps(rrs)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create rrs:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_rrs(self, context, rrs, zone_id, rrs_id):
        """   update rrs    """
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs/' + rrs_id)
        headers = {'Content-type': 'application/json'}
        rrs["current_user"] = self.auth_name
        data = json.dumps(rrs)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("update rrs:" + url))
        response = requests.put(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_rrs(self, context, zone_id, rrs_id):
        """   delete rrs    """
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs/' + rrs_id)
        headers = {'Content-type': 'application/json'}
        rrs = {}
        rrs["current_user"] = self.auth_name
        data = json.dumps(rrs)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete rrs :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def del_cache(self, context, cache_dic):
        """   delete cache    """
        url = (self.host + ":" + str(self.port) + '/cache/clean')
        LOG.info(_LI("delete cache :" + url))
        headers = {'Content-type': 'application/json'}
        cache_dic["current_user"] = self.auth_name
        auth = (self.auth_name, self.auth_pw)
        response = requests.post(url, data=cache_dic,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_zone_one(self, context, zone_id):
        """   view one zone     """
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones/' + zone_id)
        headers = {'Content-type': 'application/json'}
        LOG.info(_LI("view one zone :" + url))
        auth = (self.auth_name, self.auth_pw)
        response = requests.get(url, data={"current_user": "admin"},
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
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
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_rrs(self, context, zone_id):
        """   view rrs    """
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs')
        params = {'current_user': 'admin'}
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get_rrs :" + url))
        response = requests.get(url, data=params,
                                auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    # this is a hm_template operation
    def create_hm_template(self, context, obj_dic):
        gslb_obj = ["name", "types", "check_interval", "timeout",
                    "max_retries", "max_retries", "sendstring",
                    "recvstring", "username", "password"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("create the hm_template values with dic format"
                     "is %(json)s of dervice"), {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/hm_template')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create hm_template url:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_hm_template(self, context, obj_dic):
        name = obj_dic["hm_template_id"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/hm_template/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete hm_template url :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_hm_template(self, context, obj_dic):

        name = obj_dic["hm_template_id"]
        gslb_obj = ["check_interval", "timeout",
                    "max_retries", "max_retries", "sendstring",
                    "recvstring", "username", "password"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("update the hm_template values with dic format"
                     "is %(json)s of dervice"), {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/hm_template/' + name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("update hm_template url:" + url))
        response = requests.put(url=url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_hm_templates(self, context, obj_dic):
        gslb_obj = ["search_attrs"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/hm_template')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all hm_template url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_hm_template(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/hm_template/' + name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all hm_template url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    # this is a gslb_zone operation
    def create_gslb_zone(self, context, obj_dic):
        gslb_obj = ["name", "devices", "syn_server"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name

        LOG.info(_LI("create the gslb_zone values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/dc')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create gslb_zone url:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_gslb_zone(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/dc/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete gslb_zone url :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_gslb_zone(self, context, obj_dic):
        name = obj_dic["name"]
        gslb_obj = ["devices", "server", "enable"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
#         driver_dic["username"] = self.auth_name
#         driver_dic["password"] = self.auth_pw
        LOG.info(_LI("update the gslb_zone values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/dc/' + name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create gslb_zone url:" + url))
        response = requests.put(url=url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_gslb_zones(self, context, obj_dic):
        gslb_obj = ["search_attrs"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/dc')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all gslb_zone url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_gslb_zone(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/dc/' + name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all gslb_zone url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    # this is a gmember operation
    def create_gmember(self, context, obj_dic):
        values = ["ip", "port", "enable", "name"]
        driver_dic = tools.input_dic(values, obj_dic)
        gslb_obj = {}
        gslb_obj["gmember_name"] = obj_dic['name']
        gslb_obj["current_user"] = self.auth_name
        dic = tools.dict_merge(driver_dic, gslb_obj)
        dic.pop('name')
        LOG.info(_LI("create the gmember values with dic format"
                     "is %(json)s of dervice"), {"json": dic})
        url = (self.host + ":" + str(self.port) +
               '/dc/' + obj_dic["gslb_zone_name"] + "/gmember")
        LOG.info(_LI("create gmember url:" + url))
        headers = {'Content-type': 'application/json'}
        data = json.dumps(dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create gmember url:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_gmember(self, context, obj_dic):
        gmember_id = obj_dic["gmember_id"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/dc/' +
               obj_dic["gslb_zone_name"] + "/gmember/" + gmember_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete gmember url :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_gmember(self, context, obj_dic):
        name = obj_dic["gmember_name"]
        gslb_obj = ["enable"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("update the gmember values with dic format"
                     "is %(json)s of dervice"), {"json": driver_dic})
        url = (self.host + ":" + str(self.port) + '/dc/' +
               obj_dic["gslb_zone_name"] + "/gmember/" + name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create gmember url:" + url))
        response = requests.put(url=url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_gmembers(self, context, obj_dic):
        gslb_obj = ["search_attrs"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/dc' + obj_dic["gslb_zone_name"] + "/gmember")
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all gmember url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_gmember(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/dc/' +
               obj_dic["gslb_name"] + "/gmember/" + name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all gmember url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    # this is a syngroup operation
    def create_syngroup(self, context, obj_dic):
        gslb_obj = ["name", "dcs", "probe_range", "pass"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("create the syngroup values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/syngroup')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create syngroup url:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_syngroup(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/syngroup/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete syngroup url :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_syngroup(self, context, obj_dic):
        name = obj_dic["name"]
        gslb_obj = ["dcs", "probe_range", "pass"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("update the syngroup values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) + '/syngroup/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create syngroup url:" + url))
        response = requests.put(url=url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_syngroups(self, context, obj_dic):
        gslb_obj = ["search_attrs", "current_user"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/syngroup')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all syngroup url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_syngroup(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/syngroup/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all syngroup url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    # this is a gpool operation
    def create_gpool(self, context, obj_dic):
        gslb_obj = ["name", "enable", "ttl", "max_addr_ret", "cname",
                    "first_algorithm", "second_algorithm", "fallback_ip",
                    "hms", "pass", "gmember_list", "warning"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("create the gpool values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/gpool')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create gpool url:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_gpool(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/gpool/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete gpool url :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_gpool(self, context, obj_dic):
        name = obj_dic["name"]
        gslb_obj = ["enable", "ttl", "max_addr_ret", "cname",
                    "first_algorithm", "second_algorithm", "fallback_ip",
                    "hms", "pass", "gmember_list", "warning"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("update the gpool values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) + '/gpool/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create gpool url:" + url))

        response = requests.put(url=url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_gpools(self, context, obj_dic):
        gslb_obj = ["search_attrs", "current_user"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/gpool')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all gpool url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_gpool(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/gpool/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all gpool url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    # this is a gmap operation
    def create_gmap(self, context, obj_dic):
        gslb_obj = ["name", "enable", "algorithm", "last_resort_pool",
                    "gpool_list"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("create the gmap values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/gmap')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create gmap url:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_gmap(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/gmap/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete gmap url :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_gmap(self, context, obj_dic):
        name = obj_dic["name"]
        gslb_obj = ["enable", "algorithm", "last_resort_pool",
                    "gpool_list"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("update the gmap values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) + '/gmap/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create gmap url:" + url))
        response = requests.put(url=url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_gmaps(self, context, obj_dic):
        gslb_obj = ["search_attrs", "current_user"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/gmap')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all gmap url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_gmap(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/gmap/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all gmap url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    # this is a region operation
    def create_region(self, context, obj_dic):
        gslb_obj = ["name"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("create the region values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/region')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create region url:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_region(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/region/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete region url :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def create_member(self, context, obj_dic):
        name = obj_dic["name"]
        gslb_obj = ["type", "data1", "data2", "data3", "data4"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("create the region_create_member values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/region/' + name + "/member")
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create region_create_member url:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_member(self, context, obj_dic):
        region_id = obj_dic["name"]
        member_id = obj_dic["member_name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/region/' +
               region_id + '/member/' + member_id)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete region_delete_member url :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_regions(self, context, obj_dic):
        gslb_obj = ["search_attrs", "current_user"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/region')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all region url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_region(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/region/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all region url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    # this is a sp_policy operation
    def create_sp_policy(self, context, obj_dic):
        gslb_obj = ["priority", "src_type", "src_logic", "src_data1",
                    "src_data2", "src_data3", "src_data4", "dst_type",
                    "dst_logic", "dst_data1", "dst_data2"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("create the sp_policy values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/sp_policy')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create sp_policy url:" + url))
        response = requests.post(url, data=data,
                                 headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def delete_sp_policy(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/sp_policy/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("delete sp_policy url :" + url))
        response = requests.delete(url, data=data,
                                   headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def update_sp_policy(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        driver_dic["priority"] = obj_dic["new_priority"]
        url = (self.host + ":" + str(self.port) + '/sp_policy/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("create sp_policy url:" + url))
        response = requests.put(url=url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_sp_policys(self, context, obj_dic):
        gslb_obj = ["search_attrs", "current_user"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) +
               '/sp_policy')
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all sp_policy url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()

    def get_sp_policy(self, context, obj_dic):
        name = obj_dic["name"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/sp_policy/' +
               name)
        headers = {'Content-type': 'application/json'}
        data = json.dumps(driver_dic)
        auth = (self.auth_name, self.auth_pw)
        LOG.info(_LI("get all sp_policy url :" + url))
        response = requests.get(url, data=data,
                                headers=headers, auth=auth, verify=False)
        if response.status_code is None:
            raise NonExistDevices
        if response.status_code is not 200:
            raise ZdnsErrMessage(self.zdns_error.getMessage(response.
                                                            status_code))
        return response.json()
