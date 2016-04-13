from oslo_config import cfg
from oslo_log import log as logging
from nca47.common import service
# from nca47.common import coordination
from nca47.common.i18n import _LI
from nca47 import agent
from nca47.agent.dns_driver import zdns_driver
from nca47.agent.dns_driver import fake_driver
from nca47.manager.central import CentralManager

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

    def get_agent_status(self, context):
        print "get_agent_status from dns service"
        return None

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

    def get_records(self, context, zone_id):
        LOG.info(_LI("get_records: Calling central's get_zone_record."))
        response = self.agent.get_rrs(context, zone_id)
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
        self.agent = agent.get_firewall_backend()

    @property
    def service_name(self):
        return self.rpc_topic

    def start(self):
        super(FWService, self).start()

    def stop(self):
        super(FWService, self).stop()

    # this is a vlan operation
    def creat_vlan(self, context, vlan_infos):
        LOG.info(_LI("creat_vlan: Calling central's creat_vlan."))
        response = self.agent.creat_vlan(context, vlan_infos)
        return response

    def del_vlan(self, context, id_, vlan_infos):
        LOG.info(_LI("del_vlan: Calling central's del_vlan."))
        response = self.agent.del_vlan(context, id_, vlan_infos)
        return response

    def get_vlan(self, context, vlan_infos):
        LOG.info(_LI("get_vlan: Calling central's get_vlan."))
        response = self.agent.get_vlan(context, vlan_infos)
        return response

    def get_vlans(self, context, vlan_infos):
        LOG.info(_LI("get_vlans: Calling central's get_vlans."))
        response = self.agent.get_vlans(context, vlan_infos)
        return response

    # this is a netservice operation
    def creat_netservice(self, context, netsev_infos):
        LOG.info(_LI("creat_netservice: Calling central's creat_netservice."))
        response = self.agent.creat_netservice(context, netsev_infos)
        return response

    def del_netservice(self, context, id_, netsev_infos):
        LOG.info(_LI("del_netservice: Calling central's del_netservice."))
        response = self.agent.del_netservice(context, id_, netsev_infos)
        return response

    def get_netservice(self, context, netsev_infos):
        LOG.info(_LI("get_netservice: Calling central's get_netservice."))
        response = self.agent.get_netservice(context, netsev_infos)
        return response

    def get_netservices(self, context, netsev_infos):
        LOG.info(_LI("get_netservices: Calling central's get_netservices."))
        response = self.agent.get_netservices(context, netsev_infos)
        return response

    # this is a addrobj operation
    def add_addrobj(self, context, addrobj_infos):
        LOG.info(_LI("add_addrobj: Calling central's add_addrobj."))
        response = self.agent.add_addrobj(context, addrobj_infos)
        return response

    def del_addrobj(self, context, addrobj_infos):
        LOG.info(_LI("del_addrobj: Calling central's del_addrobj."))
        response = self.agent.del_addrobj(
            context, addrobj_infos['id'], addrobj_infos)
        return response

    def get_addrobj(self, context, addrobj_infos):
        LOG.info(_LI("get_addrobj: Calling central's get_addrobj."))
        response = self.agent.get_addrobj(context, addrobj_infos)
        return response

    def get_addrobjs(self, context, addrobj_infos):
        LOG.info(_LI("get_addrobjs: Calling central's get_addrobjs."))
        response = self.agent.get_addrobjs(context, addrobj_infos)
        return response

    # this is a snataddrpool operation
    def add_snataddrpool(self, context, snataddrpool_infos):
        LOG.info(_LI("add_snataddrpool: Calling central's add_snataddrpool."))
        response = self.agent.add_snataddrpool(context, snataddrpool_infos)
        return response

    def del_snataddrpool(self, context, snataddrpool_infos):
        LOG.info(_LI("del_snataddrpool: Calling central's del_snataddrpool."))
        response = self.agent.del_snataddrpool(
            context, snataddrpool_infos['id'], snataddrpool_infos)
        return response

    def get_snataddrpool(self, context, snataddrpool_infos):
        LOG.info(_LI("get_snataddrpool: Calling central's get_snataddrpool."))
        response = self.agent.get_snataddrpool(context, snataddrpool_infos)
        return response

    def get_snataddrpools(self, context, snataddrpool_infos):
        LOG.info(_LI("get_snataddrpools: Calling central's get_snataddrpools."))
        response = self.agent.get_snataddrpools(context, snataddrpool_infos)
        return response


class AgentService(service.RPCService, service.Service):

    """
    Use for handling device-agent's requests and validation
    request parametes
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='add_agent', threads=None):
        self.rpc_topic = topic
        super(AgentService, self).__init__(threads=threads)
        self.agent = agent.get_dns_backend()

    @property
    def service_name(self):
        return self.rpc_topic

    def start(self):
        super(AgentService, self).start()

    def stop(self):
        super(AgentService, self).stop()

    # Zone Methods
    def add_device_agent(self, context, agent):
        LOG.info(_LI("add_dev_agent: Replying rpc client's add_device_agent."))
        centralManager = CentralManager.get_instance()
        agent = centralManager.add_device_agent(agent)
        return agent
