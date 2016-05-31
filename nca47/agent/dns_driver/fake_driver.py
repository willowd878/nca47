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


class fake_dns_driver():

    def __init__(self):
        self.host = 'https://fake_ip'
        self.port = CONF.zdns.port
        self.view_id = CONF.zdns.view_id
        self.auth_name = CONF.zdns.auth_name
        self.auth_pw = CONF.zdns.auth_pw

    @classmethod
    def get_instance(cls):
        global DNS_DRIVER
        if not DNS_DRIVER:
            DNS_DRIVER = cls()
        return DNS_DRIVER

    def create_zone(self, context, zone):
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones')
        LOG.info(_LI("create zones:" + url))
        return {" fake create zone": "success"}

    def update_zone_owners(self, context, zone, zone_id):
        url = (self.host + ":" + str(self.port) + '/views/' +
               self.view_id + '/zones/' + zone_id + '/owners')
        LOG.info(_LI("update_zone_owners:" + url))
        return {"fake update zone owners zone": "success"}

    def update_zone(self, context, zone, zone_id):
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones/' + zone_id)
        LOG.info(_LI("update zones :" + url))
        return {"fake update_zone zone": "success"}

    def delete_zone(self, context, zone_id):
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id)
        LOG.info(_LI("delete zones :" + url))
        return {"fake delete_zone zone": "success"}

    def create_rrs(self, context, rrs, zone_id):
        url = (str(self.host) + ":" + str(self.port) + '/views/' +
               self.view_id + '/zones/' + str(zone_id) + '/rrs')
        LOG.info(_LI("create rrs:" + url))
        res = {
            "fake comment": "", "name": "www.baidu.", "type": "A",
            "ttl": 1200, "state": "",
            "href": "/views/default/zones/www.baidu/rrs/"
            "www.baidu.$1200$A$MTk4LjIwMi4zOC40OA==",
            "klass": "IN", "rdata": "198.202.38.48",
            "reverse_name": "baidu.www",
            "id": "www.baidu.$1200$A$MTk4LjIwMi4zOC40OA==",
            "is_shared": ""
        }
        return res

    def update_rrs(self, context, rrs, zone_id, rrs_id):
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs/' + rrs_id)
        LOG.info(_LI("update rrs:" + url))
        return {"id": "update_rrs", "ttl": "100",
                "name": "www.baidu.com", "type": "A"}

    def delete_rrs(self, context, zone_id, rrs_id):
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs/' + rrs_id)
        LOG.info(_LI("delete rrs :" + url))
        return {"fake delete_rss": "success"}

    def del_cache(self, context, cache_dic):
        url = (self.host + ":" + str(self.port) + '/cache/clean')
        LOG.info(_LI("delete cache :" + url))
        return {"fake clean cache": "success"}

    def get_zone_one(self, context, zone_id):
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones/' + zone_id)
        LOG.info(_LI("view one zone :" + url))
        return {"fake get_zone_one": "success"}

    def get_zones(self, context):
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones')
        LOG.info(_LI("view all zone :" + url))
        return {"fake get_zones": "success"}

    def get_rrs(self, context, zone_id):
        url = (self.host + ":" + str(self.port) + '/views/' + self.view_id +
               '/zones/' + zone_id + '/rrs')
        LOG.info(_LI("get_rrs :" + url))
        res = {
            "total_size": 2, "page_num": 1,
            "resources":
                [
                    {
                        "comment": "", "name": "www.baidu.",
                        "type": "NS", "ttl": 3600, "state": "",
                        "href": "/views/default/zones/www.baidu/rrs/"
                        "www.baidu.$3600$NS$bnMud3d3LmJhaWR1Lg==",
                        "klass": "IN", "rdata": "ns.www.baidu.",
                        "reverse_name": "baidu.www",
                        "id": "www.baidu.$3600$NS$bnMud3d3LmJhaWR1Lg==",
                        "is_shared": ""
                    },
                    {
                        "comment": "", "name": "ns.www.baidu.",
                        "type": "A", "ttl": 3600, "state": "",
                        "href": "/views/default/zones/www.baidu/rrs/"
                        "ns.www.baidu.$3600$A$MTI3LjAuMC4x",
                        "klass": "IN", "rdata": "127.0.0.1",
                        "reverse_name": "baidu.www.ns",
                        "id": "ns.www.baidu.$3600$A$MTI3LjAuMC4x",
                        "is_shared": ""
                    }
                ],
            "page_size": 2
        }
        return res

    def create_region(self, context, region):
        LOG.info(_LI("create regions..."))
        return {"region_id": "123456", "refcnt": "123456"}

    def delete_region(self, context, region):
        LOG.info(_LI("delete regions :"))
        return {"fake delete_region region": "success"}

    def create_member(self, context, member):
        LOG.info(_LI("create members..."))
        return {"id": "member123456"}

    def delete_member(self, context, member):
        LOG.info(_LI("delete members :"))
        return {"fake delete_member member": "success"}

    def create_sp_policy(self, context, policy):
        LOG.info(_LI("create policys..."))
        return {"sp_policy_id": "policy123456"}

    def delete_sp_policy(self, context, policy):
        LOG.info(_LI("delete policys :"))
        return {"fake delete_sp_policy policy": "success"}

    def update_sp_policy(self, context, policy):
        LOG.info(_LI("update policys :"))
        return {"fake update_sp_policy policy": "success"}

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
        return {"refcnt": "10", "id": "test_gmember_id"}

    def delete_gmember(self, context, obj_dic):

        gmember_id = obj_dic["gmember_id"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/dc/' +
               obj_dic["gslb_zone_name"] + "/gmember/" + gmember_id)

        return {"result": "successed"}

    def update_gmember(self, context, obj_dic):

        name = obj_dic["gmember_name"]
        gslb_obj = ["enable"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        LOG.info(_LI("update the gmember values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) + '/dc/' +
               obj_dic["gslb_zone_name"] + "/gmember/" + name)

        return {"update": "successed"}

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

        return {"refcnt": "10", "id": "test_hm_template_id"}

    def delete_hm_template(self, context, obj_dic):
        name = obj_dic["hm_template_id"]
        driver_dic = {}
        driver_dic["current_user"] = self.auth_name
        url = (self.host + ":" + str(self.port) + '/hm_template/' +
               name)
        return {"result": "successed"}

    def update_hm_template(self, context, obj_dic):
        name = obj_dic["hm_template_id"]
        gslb_obj = ["check_interval", "timeout",
                    "max_retries", "max_retries", "sendstring",
                    "recvstring", "username", "password"]
        driver_dic = tools.input_dic(gslb_obj, obj_dic)
        driver_dic["current_user"] = self.auth_name
        driver_dic["username"] = self.auth_name
        driver_dic["password"] = self.auth_pw
        LOG.info(_LI("update the hm_template values with dic format\
                         is %(json)s of dervice"),
                 {"json": driver_dic})
        url = (self.host + ":" + str(self.port) +
               '/hm_template/' + name)
        return {"update": "successed"}

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
        obj_dic['id'] = obj_dic['name']
        return obj_dic

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
        obj_dic['id'] = obj_dic['name']
        return obj_dic

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
        obj_dic['id'] = obj_dic['name']
        return obj_dic

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
        obj_dic['refcnt'] = 12
        obj_dic['id'] = obj_dic['name']
        return obj_dic

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
        obj_dic['refcnt'] = 12
        obj_dic['id'] = obj_dic['name']
        return obj_dic

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
        return obj_dic

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
        obj_dic['id'] = obj_dic['name']
        return obj_dic

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
        return obj_dic

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
        return obj_dic
