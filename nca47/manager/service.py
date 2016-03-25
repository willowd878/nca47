from oslo_config import cfg
from oslo_log import log as logging
from nca47.common import service
# from nca47.common import coordination
from nca47.common.i18n import _LI
from nca47 import agent
from nca47.agent.dns_driver import zdns_driver

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

RPC_API_VERSION = '1.0'


class DNSService(service.RPCService, service.Service):
    """ Use for handling DNS requests and validation request parameters"""

    RPC_API_VERSION = '1.0'

    # Since the RPC Service class will be use for handle/reply all message
    # for every RPC client, so will initialize some keys
    def __init__(self, topic='dns_manager', threads=None):
        self.rpc_topic = topic
        super(DNSService, self).__init__(threads=threads)
        self.agent = agent.get_dns_backend()

    @property
    def service_name(self):
        return self.rpc_topic

    def start(self):
        super(DNSService, self).start()

    def stop(self):
        super(DNSService, self).stop()

    # Zone Methods
    def create_zone(self, context, zone):
        LOG.info(_LI("create_zone: Replying rpc client's create_zone."))
        zone = self.agent.create_zone(context, zone)
        return zone

    def update_zone(self, context, zone, zone_id):
        LOG.info(_LI("update_zone: Replying rpc client's update_zone."))
        zone = self.agent.update_zone(context, zone, zone_id)
        return zone

    def update_zone_owners(self, context, zone, zone_id):
        LOG.info(_LI("update_zone_owners: Replying rpcclient's update_zone."))
        zone = self.agent.update_zone_owners(context, zone, zone_id)
        return zone

    def delete_zone(self, context, zone, zone_id):
        LOG.info(_LI("delete_zone: Replying rpc client's delete_zone."))
        response = self.agent.delete_zone(context, zone, zone_id)
        return response

    def get_zone_one(self, context, zone_id):
        LOG.info(_LI("get_zone_one: Replying rpc client's "
                     "get_zone_one."))
        response = self.agent.get_zone_one(context, zone_id)
        return response

    def get_zones(self, context):
        LOG.info(_LI("get_zones: Replying rpc client's get_zones."))
        response = self.agent.get_zones(context)
        return response

    # Zone_records Methods
    def create_record(self, context, records_dic, zone_id):
        LOG.info(_LI("create_record: Calling central's create_zone_record."))
        response = self.agent.create_rrs(context, records_dic, zone_id)
        return response

    def get_records(self, context, records_dic, zone_id):
        LOG.info(_LI("get_records: Calling central's get_zone_record."))
        response = self.agent.get_rrs(context, records_dic, zone_id)
        return response

    def update_record(self, context, records_dic, zone_id, record_id):
        LOG.info(_LI("update_record: Calling central's update_zone_record."))
        response = self.agent.update_rrs(context, records_dic, zone_id,
                                         record_id)
        return response

    def delete_record(self, context, records_dic, zone_id, record_id):
        LOG.info(_LI("delete_record: Calling central's delete_zone_record."))
        response = self.agent.delete_rrs(context, records_dic, zone_id,
                                         record_id)
        return response

    def del_cache(self, context, cache_dic):
        LOG.info(_LI("del_cache: Calling central's del_cache."))
        response = self.agent.del_cache(context, cache_dic)
        return response


class FWService(service.RPCService, service.Service):
    """
    Use for handling FireWall's requests and validation
    request parametes
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='firewall_manager', threads=None):
        self.rpc_topic = topic
        super(FWService, self).__init__(threads=threads)
