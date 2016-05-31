from oslo_config import cfg
from oslo_log import log as logging
from nca47.common import service

from oslo_utils import timeutils
from nca47.common.i18n import _
from nca47.common.i18n import _LI
from nca47 import agent
from nca47 import objects
from nca47.agent.agentFlag.agent_rpcapi import AgentAPI
from oslo_service import loopingcall

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

RPC_API_VERSION = '1.0'
count = 0

AGENT_OPTS = [
    cfg.IntOpt('report_interval',
               default='60',
               help=_('Seconds between nodes reporting state to server; '
                      'should be less than agent_down_time, best if it '
                      'is half or less than agent_down_time.')),
    cfg.IntOpt('agent_down_time',
               default='120',
               help=_('Seconds to regard the agent is down; should be at '
                      'least twice report_interval, to be sure the '
                      'agent is down for good.')),
]

opt_group = cfg.OptGroup(name='agent',
                         title='Options for nca47 agent node info')
CONF.register_group(opt_group)
CONF.register_opts(AGENT_OPTS, opt_group)


class DNSService(service.RPCService, service.Service):
    """ Use for handling DNS requests and validation request parameters"""

    RPC_API_VERSION = '1.0'

    # Since the RPC Service class will be use for handle/reply all message
    # for every RPC client, so will initialize some keys
    def __init__(self, topic='dns_manager', agentinfo=None, threads=None):
        self.rpc_topic = topic
        super(DNSService, self).__init__(threads=threads)
        self.agent = agent.get_dns_backend()

#         self.agent_rpcapi = AgentAPI.get_instance()
#         periodic = loopingcall.FixedIntervalLoopingCall(
#                                         self.get_agent_status, agentinfo)
#         periodic.start(interval=CONF.agent.report_interval)

    def get_agent_status(self, agentInfo):
        try:
            self.agent_rpcapi.report_agent_state(agentInfo)
        except Exception as e:
            raise e

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

    def delete_zone(self, context, zone_id):
        LOG.info(_LI("delete_zone: Replying rpc client's delete_zone."))
        response = self.agent.delete_zone(context, zone_id)
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

    def delete_record(self, context, zone_id, record_id):
        LOG.info(_LI("delete_record: Calling central's delete_zone_record."))
        response = self.agent.delete_rrs(context, zone_id, record_id)
        return response

    def del_cache(self, context, cache_dic):
        LOG.info(_LI("del_cache: Calling central's del_cache."))
        response = self.agent.del_cache(context, cache_dic)
        return response

    def glsb_math(self, context, obj_dic, math):
        LOG.info(_LI("glsb_math: Replying rpc client's glsb_math."))
        funt = getattr(self.agent, math)
        response = funt(context, obj_dic)
        return response


class FWService(service.RPCService, service.Service):
    """
    Use for handling FireWall's requests and validation
    request parametes
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='firewall_manager', agentinfo=None,
                 threads=None):
        if agentinfo:
            self.rpc_topic = '%s.%s' % (topic, agentinfo['agent_ip'])
        else:
            self.rpc_topic = topic
        super(FWService, self).__init__(threads=threads)
        self.agent = agent.get_firewall_backend()
        self.agent_rpcapi = AgentAPI.get_instance()
        periodic = loopingcall.FixedIntervalLoopingCall(self.get_agent_status,
                                                        agentinfo)
        periodic.start(interval=CONF.agent.report_interval)

    def get_agent_status(self, agentInfo):
        try:
            self.agent_rpcapi.report_agent_state(agentInfo)
        except Exception as e:
            raise e

    @property
    def service_name(self):
        return self.rpc_topic

    def start(self):
        super(FWService, self).start()

    def stop(self):
        super(FWService, self).stop()

    # this is a vlan operation
    def create_vlan(self, context, vlan_infos):
        LOG.info(_LI("create_vlan: Calling central's create_vlan."))
        response = self.agent.create_vlan(context, vlan_infos)
        return response

    def del_vlan(self, context, vlan_infos):
        LOG.info(_LI("del_vlan: Calling central's del_vlan."))
        response = self.agent.del_vlan(context, vlan_infos)
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
    def create_netservice(self, context, netsev_infos):
        LOG.info(_LI("create_netservice: Calling central's"
                     " create_netservice."))
        response = self.agent.create_netservice(context, netsev_infos)
        return response

    def del_netservice(self, context, netsev_infos):
        LOG.info(_LI("del_netservice: Calling central's del_netservice."))
        response = self.agent.del_netservice(context, netsev_infos)
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
            context, addrobj_infos)
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
            context, snataddrpool_infos)
        return response

    def get_snataddrpool(self, context, snataddrpool_infos):
        LOG.info(_LI("get_snataddrpool: Calling central's get_snataddrpool."))
        response = self.agent.get_snataddrpool(context, snataddrpool_infos)
        return response

    def get_snataddrpools(self, context, snataddrpool_infos):
        LOG.info(_LI("get_snataddrpools: Calling central's"
                     "get_snataddrpools."))
        response = self.agent.get_snataddrpools(context, snataddrpool_infos)
        return response

    def create_vfw(self, context, vfw):
        LOG.info(_LI("create_vfw: Calling central's create_vfw."))
        response = self.agent.create_vfw(context, vfw)
        return response

    def delete_vfw(self, context, vfw):
        LOG.info(_LI("delete_vfw: Calling central's delete_vfw."))
        response = self.agent.delete_vfw(context, vfw)
        return response

    def get_vfw(self, context, vfw):
        LOG.info(_LI("get_vfw: Calling central's get_vfw."))
        response = self.agent.get_vfw(context, vfw)
        return response

    def get_all_vfws(self, context, vfw):
        LOG.info(_LI("get_all_vfws: Calling central's get_all_vfws."))
        response = self.agent.get_all_vfws(context, vfw)
        return response

    def create_dnat(self, context, dnat):
        LOG.info(_LI("create_dnat: Calling central's create_dnat."))
        response = self.agent.create_dnat(context, dnat)
        return response

    def delete_dnat(self, context, dnat):
        LOG.info(_LI("delete_dnat: Calling central's delete_dnat."))
        response = self.agent.delete_dnat(context, dnat)
        return response

    def get_dnat(self, context, dnat):
        LOG.info(_LI("get_dnat: Calling central's get_dnat."))
        response = self.agent.get_dnat(context, dnat)
        return response

    def get_all_dnats(self, context, dnat):
        LOG.info(_LI("get_all_dnats: Calling central's get_all_dnats."))
        response = self.agent.get_all_dnats(context, dnat)
        return response

    def create_packetfilter(self, context, packetfilter):
        LOG.info(_LI("create_packetfilter: Calling central's"
                     "create_packetfilter."))
        response = self.agent.create_packetfilter(context, packetfilter)
        return response

    def delete_packetfilter(self, context, packetfilter):
        LOG.info(_LI("delete_packetfilter: Calling central's"
                     "delete_packetfilter."))
        response = self.agent.delete_packetfilter(context, packetfilter)
        return response

    def get_packetfilter(self, context, packetfilter):
        LOG.info(_LI("get_packetfilter: Calling central's get_packetfilter."))
        response = self.agent.get_packetfilter(context, packetfilter)
        return response

    def get_all_packetfilters(self, context, packetfilter):
        LOG.info(_LI("get_all_packetfilters: Calling central's"
                     "get_all_packetfilters."))
        response = self.agent.get_all_packetfilters(context, packetfilter)
        return response

    def create_vrf(self, context, vrf):
        LOG.info(_LI("create_vrf: Calling central's create_vrf."))
        response = self.agent.create_vrf(context, vrf)
        return response

    def del_vrf(self, context, vrf):
        LOG.info(_LI("del_vrf: Calling central's del_vrf."))
        response = self.agent.del_vrf(context, vrf)
        return response

    def get_vrf(self, context, vrf):
        LOG.info(_LI("get_vrf: Calling central's get_vrf."))
        response = self.agent.get_vrf(context, vrf)
        return response

    def get_vrfs(self, context, vrf):
        LOG.info(_LI("get_vrfs: Calling central's get_vrfs."))
        response = self.agent.get_vrfs(context, vrf)
        return response

    def create_snat(self, context, snat):
        LOG.info(_LI("create_snat: Calling central's create_snat."))
        response = self.agent.create_snat(context, snat)
        return response

    def del_snat(self, context, snat):
        LOG.info(_LI("del_snat: Calling central's del_snat."))
        response = self.agent.delete_snat(context, snat)
        return response

    def get_snat(self, context, snat):
        LOG.info(_LI("get_snat: Calling central's get_snat."))
        response = self.agent.get_snat(context, snat)
        return response

    def get_snats(self, context, snat):
        LOG.info(_LI("get_snats: Calling central's get_snats."))
        response = self.agent.get_snats(context, snat)
        return response

    def create_securityzone(self, context, sec_infos):
        LOG.info(_LI("create_securityZone: Calling central's"
                     "create_securityZone."))
        response = self.agent.create_securityzone(context, sec_infos)
        return response

    def securityzone_addif(self, context, sec_infos):
        LOG.info(_LI("securityZone_addif: Calling central's"
                     "securityZone_addif."))
        response = self.agent.securityzone_addif(context, sec_infos)
        return response

    def securityzone_delif(self, context, sec_infos):
        LOG.info(_LI("securityZone_delif: Calling central's"
                     "securityZone_delif."))
        response = self.agent.securityzone_delif(context, sec_infos)
        return response

    def delete_securityzone(self, context, sec_infos):
        LOG.info(_LI("del_securityZone: Calling central's del_securityZone."))
        response = self.agent.delete_securityzone(context, sec_infos)
        return response

    def get_securityzone(self, context, securityzone):
        LOG.info(_LI("get_securityZone: Calling central's"
                     "get_securityZone."))
        response = self.agent.get_securityzone(context, securityzone)
        return response

    def get_securityzones(self, context, securityzone):
        LOG.info(_LI("get_securityZones: Calling central's"
                     "get_securityZones."))
        response = self.agent.get_securityzones(context, securityzone)
        return response

    def create_staticnat(self, context, staticnat):
        LOG.info(_LI("create_staticnat: Calling central's create_staticnat."))
        response = self.agent.create_staticnat(context, staticnat)
        return response

    def del_staticnat(self, context, staticnat):
        LOG.info(_LI("del_staticnat: Calling central's del_staticnat."))
        response = self.agent.delete_staticnat(context, staticnat)
        return response

    def get_staticnat(self, context, staticnat):
        LOG.info(_LI("get_staticnat: Calling central's get_staticnat."))
        response = self.agent.get_staticnat(context, staticnat)
        return response

    def get_staticnats(self, context, staticnat):
        LOG.info(_LI("get_staticnats: Calling central's get_staticnats."))
        response = self.agent.get_staticnats(context, staticnat)
        return response


class AgentService(service.RPCService, service.Service):
    """
    Use for handling device-agent's requests and validation
    request parametes
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='check_agent_heartbeat', threads=None):
        self.rpc_topic = topic
        super(AgentService, self).__init__(threads=threads)

    @property
    def service_name(self):
        return self.rpc_topic

    def start(self):
        super(AgentService, self).start()

    def stop(self):
        super(AgentService, self).stop()

    def report_agent_state(self, context, agent_info):
        LOG.info(_LI("updating agent state: Replying rpc client's "
                     "report_agent_state."))
        agent_obj = objects.Agent(context, **agent_info)
        # Check the target agent object whether exist in DB
        conditions = {}
        conditions['dc_name'] = agent_info['dc_name']
        conditions['network_zone'] = agent_info['network_zone']
        conditions['agent_ip'] = agent_info['agent_ip']
        conditions['agent_nat_ip'] = agent_info['agent_nat_ip']
        conditions['agent_type'] = agent_info['agent_type']
        conditions['deleted'] = False
        target_agent = None
        try:
            target_agent = agent_obj.get_object(context, **conditions)
        except:
            LOG.info(_LI('cannot find related agent record in DB, so think '
                         'this agent info as new, need to save in DB'))
            pass
        if target_agent:
            update_agent = {}
            update_agent['update_time'] = timeutils.utcnow()
            update_agent['availiable'] = 'yes'
            update_infos = objects.Agent(context, **update_agent)
            agent_obj.update(context, target_agent['id'],
                             update_infos.as_dict())
        else:
            agent_obj.availiable = 'yes'
            agent_obj.update_time = timeutils.utcnow()
            agent_obj.create(context, agent_obj.as_dict())
        return agent


class CLIService(service.RPCService, service.Service):
    """
    Use for handling command-line interface requests and validation
    request parametes
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='cli_manager', agentinfo=None, threads=None):
        if agentinfo:
            self.rpc_topic = '%s.%s' % (topic, agentinfo['agent_ip'])
        else:
            self.rpc_topic = topic
        super(CLIService, self).__init__(threads=threads)
        self.agent = agent.get_cli_backend()

    @property
    def service_name(self):
        return self.rpc_topic

    def start(self):
        super(CLIService, self).start()

    def stop(self):
        super(CLIService, self).stop()

    def execute_commands(self, context, req):
        cli_client = self.agent.sshClient(**req)
        commands = req['commands']
        response = cli_client.send(commands)
        return response
