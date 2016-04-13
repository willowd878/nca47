from oslo_config import cfg
from oslo_log import log as logging
from nca47.common.i18n import _
from nca47.common.i18n import _LI

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
        LOG.info(_LI("create zones:"+url))
        return {" fake create zone": "success"}

    def update_zone_owners(self, context, zone, zone_id):
        url = (self.host + ":" + str(self.port) + '/views/' +
               self.view_id + '/zones/' + zone_id + '/owners')
        LOG.info(_LI("update_zone_owners:"+url))
        return {"fake update zone owners zone": "success"}

    def update_zone(self, context, zone, zone_id):
        url = (self.host + ":" + str(self.port) +
               '/views/' + self.view_id + '/zones/' + zone_id)
        LOG.info(_LI("update zones :"+url))
        return {"fake update_zone zone": "success"}

    def delete_zone(self, context, zone, zone_id):
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
        return {"fake id": "update_rrs"}

    def delete_rrs(self, context, rrs, zone_id, rrs_id):
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
