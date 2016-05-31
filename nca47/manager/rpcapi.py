from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from nca47.common import rpc

from nca47.common.i18n import _LI

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

DNS_MANAGER_API = None
FW_MANAGER_API = None
CLI_MANAGER_API = None


class DNSManagerAPI(object):
    """
    Client side of the DNS manager RPC API.

    API version history:

        1.0 - Initial version
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='dns_manager'):
        rpc.init(CONF)

        target = messaging.Target(topic=topic, version=self.RPC_API_VERSION)
        self.client = rpc.get_client(target, version_cap=self.RPC_API_VERSION)

    @classmethod
    def get_instance(cls):
        """
        The rpc.get_client() which is called upon the API object initialization
        will cause a assertion error if the designate.rpc.TRANSPORT isn't setup
        by rpc.init() before.

        This fixes that by creating the rpcapi when demanded.
        """
        global DNS_MANAGER_API
        if not DNS_MANAGER_API:
            DNS_MANAGER_API = cls()
        return DNS_MANAGER_API

    # Zone Methods
    def create_zone(self, context, zone):
        LOG.info(_LI("create_zone: Calling central's create_zone."))
        return self.client.call(context, 'create_zone', zone=zone)

    def update_zone(self, context, zone, zone_id):
        LOG.info(_LI("update_zone: Calling central's update_zone."))
        return self.client.call(context, 'update_zone', zone=zone,
                                zone_id=zone_id)

    def update_zone_owners(self, context, zone, zone_id):
        LOG.info(_LI("update_zone_owners: Calling central's update_zone."))
        return self.client.call(context, 'update_zone_owners', zone=zone,
                                zone_id=zone_id)

    def delete_zone(self, context, zone_id):
        LOG.info(_LI("delete_zone: Calling central's delete_zone."))
        return self.client.call(context, 'delete_zone', zone_id=zone_id)

    def get_zone_one(self, context, zone_id):
        LOG.info(_LI("get_zone_one: Replying rpc client's"
                     "get_zone_one."))
        return self.client.call(context, 'get_zone_one',
                                zone_id=zone_id)

    def get_zones(self, context):
        LOG.info(_LI("get_zones: Replying rpc client's get_zones."))
        return self.client.call(context, 'get_zones')

    # Zone_records Methods
    def create_record(self, context, records_dic, zone_id):
        LOG.info(_LI("create_zone_records: Calling central's"
                     " create_zone_record."))
        return self.client.call(context, 'create_record',
                                records_dic=records_dic, zone_id=zone_id)

    def get_records(self, context, zone_id):
        LOG.info(_LI("get_zone_record: Calling central's get_zone_record."))
        '''return self.client.call(context, 'get_record', zone_id=zone_id,
        rrs_id=rrs_id)'''
        return self.client.call(context, 'get_records', zone_id=zone_id)

    def update_record(self, context, records_dic, zone_id, rrs_id):
        LOG.info(_LI("update_zone_record: Calling central's"
                     "update_zone_record."))
        return self.client.call(context, 'update_record',
                                records_dic=records_dic, zone_id=zone_id,
                                record_id=rrs_id)

    def delete_record(self, context, zone_id, rrs_id):
        LOG.info(_LI("delete_zone_record: Calling central's"
                     " delete_zone_record."))
        return self.client.call(context, 'delete_record',
                                zone_id=zone_id, record_id=rrs_id)

    def del_cache(self, context, cache_dic):
        LOG.info(_LI("del_cache: Calling central's del_cache."))
        return self.client.call(context, 'del_cache', cache_dic=cache_dic)

    def glsb_math(self, context, obj_dic, math):
        LOG.info(_LI("glsb_math: Calling central's"
                     "glsb_math."))
        return self.client.call(context, 'glsb_math',
                                obj_dic=obj_dic,
                                math=math)


class FWManagerAPI(object):
    """
    Client side of the Firewall manager RPC API.

    API version history:

        1.0 - Initial version
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='firewall_manager'):
        rpc.init(CONF)
        # Target's base topic as 'firewall_manager' to make sure rpc/service
        # can be connected, since firewall have more than one agent endpoint
        # so when confirming the goal agent info via api parameters, we need
        # reload the topic
        target = messaging.Target(topic=topic, version=self.RPC_API_VERSION)
        self.client = rpc.get_client(target, version_cap=self.RPC_API_VERSION)

    @classmethod
    def get_instance(cls):
        """
        The rpc.get_client() which is called upon the API object initialization
        will cause a assertion error if the designate.rpc.TRANSPORT isn't setup
        by rpc.init() before.

        This fixes that by creating the rpcapi when demanded.
        """
        global FW_MANAGER_API
        if not FW_MANAGER_API:
            FW_MANAGER_API = cls()
        return FW_MANAGER_API

    def reload_topic(self, target_host, topic='firewall_manager'):
        """
        Reload topic info base on target_host value to make sure message can be
        send to the corresponding rpc service endpoint
        """
        self.client.target.topic = '%s.%s' % (topic, target_host)

    def create_vlan(self, context, vlan_infos):
        LOG.info(_LI("create_vlan: Calling central's"
                     "create_vlan."))
        return self.client.call(context, 'create_vlan',
                                vlan_infos=vlan_infos)

    def del_vlan(self, context, vlan_infos):
        LOG.info(_LI("del_vlan: Calling central's"
                     "del_vlan."))
        return self.client.call(context, 'del_vlan',
                                vlan_infos=vlan_infos)

    def get_vlan(self, context, vlan_infos):
        LOG.info(_LI("get_vlan: Calling central's"
                     "get_vlan."))
        return self.client.call(context, 'get_vlan',
                                vlan_infos=vlan_infos)

    def get_vlans(self, context, vlan_infos):
        LOG.info(_LI("get_vlans: Calling central's"
                     "get_vlans."))
        return self.client.call(context, 'get_vlans',
                                vlan_infos=vlan_infos)

    def create_netservice(self, context, netsev_infos):
        LOG.info(_LI("create_netservice: Calling central's"
                     "create_netservice."))
        return self.client.call(context, 'create_netservice',
                                netsev_infos=netsev_infos)

    def del_netservice(self, context, netsev_infos):
        LOG.info(_LI("del_netservice: Calling central's"
                     " del_netservice."))
        return self.client.call(context, 'del_netservice',
                                netsev_infos=netsev_infos)

    def get_netservice(self, context, netsev_infos):
        LOG.info(_LI("get_netservice: Calling central's"
                     "get_netservice."))
        return self.client.call(context, 'get_netservice',
                                netsev_infos=netsev_infos)

    def get_netservices(self, context, netsev_infos):
        LOG.info(_LI("get_netservices: Calling central's"
                     "get_netservices."))
        return self.client.call(context, 'get_netservices',
                                netsev_infos=netsev_infos)

    def add_addrobj(self, context, addrobj_infos):
        LOG.info(_LI("add_addrobj: Calling central's"
                     "add_addrobj."))
        return self.client.call(context, 'add_addrobj',
                                addrobj_infos=addrobj_infos)

    def del_addrobj(self, context, addrobj_infos):
        LOG.info(_LI("del_addrobj: Calling central's"
                     "del_addrobj."))
        return self.client.call(context, 'del_addrobj',
                                addrobj_infos=addrobj_infos)

    def get_addrobj(self, context, addrobj_infos):
        LOG.info(_LI("get_addrobj: Calling central's"
                     "get_addrobj."))
        return self.client.call(context, 'get_addrobj',
                                addrobj_infos=addrobj_infos)

    def get_addrobjs(self, context, addrobj_infos):
        LOG.info(_LI("get_addrobjs: Calling central's"
                     "get_addrobjs."))
        return self.client.call(context, 'get_addrobjs',
                                addrobj_infos=addrobj_infos)

    def add_snataddrpool(self, context, snataddrpool_infos):
        LOG.info(_LI("add_snataddrpool: Calling central's"
                     "add_snataddrpool."))
        return self.client.call(context, 'add_snataddrpool',
                                snataddrpool_infos=snataddrpool_infos)

    def del_snataddrpool(self, context, snataddrpool_infos):
        LOG.info(_LI("del_snataddrpool: Calling central's"
                     "del_snataddrpool."))
        return self.client.call(context, 'del_snataddrpool',
                                snataddrpool_infos=snataddrpool_infos)

    def get_snataddrpool(self, context, snataddrpool_infos):
        LOG.info(_LI("get_snataddrpool: Calling central's"
                     "get_snataddrpool."))
        return self.client.call(context, 'get_snataddrpool',
                                snataddrpool_infos=snataddrpool_infos)

    def get_snataddrpools(self, context, snataddrpool_infos):
        LOG.info(_LI("get_snataddrpools: Calling central's"
                     "get_snataddrpools."))
        return self.client.call(context, 'get_snataddrpools',
                                snataddrpool_infos=snataddrpool_infos)

    def create_vfw(self, context, vfw):
        LOG.info(_LI("create_vfw: Calling central's create_vfw."))
        return self.client.call(context, 'create_vfw', vfw=vfw)

    def delete_vfw(self, context, vfw):
        LOG.info(_LI("delete_vfw: Calling central's delete_vfw."))
        return self.client.call(context, 'delete_vfw',
                                vfw=vfw)

    def get_vfw(self, context, vfw):
        LOG.info(_LI("get_vfw: Calling central's get_vfw."))
        return self.client.call(context, 'get_vfw', vfw=vfw)

    def get_all_vfws(self, context, vfw):
        LOG.info(_LI("get_all_vfws: Calling central's get_all_vfws."))
        return self.client.call(context, 'get_all_vfws', vfw=vfw)

    def create_dnat(self, context, dnat):
        LOG.info(_LI("create_dnat: Calling central's create_dnat."))
        return self.client.call(context, 'create_dnat', dnat=dnat)

    def delete_dnat(self, context, dnat):
        LOG.info(_LI("delete_dnat: Calling central's delete_dnat."))
        return self.client.call(context, 'delete_dnat', dnat=dnat)

    def get_dnat(self, context, dnat):
        LOG.info(_LI("get_dnat: Calling central's get_dnat."))
        return self.client.call(context, 'get_dnat', dnat=dnat)

    def get_all_dnats(self, context, dnat):
        LOG.info(_LI("get_all_dnats: Calling central's get_all_dnats."))
        return self.client.call(context, 'get_all_dnats', dnat=dnat)

    def create_packetfilter(self, context, packetfilter):
        LOG.info(_LI("create_packetfilter: Calling central's"
                     "create_packetfilter."))
        return self.client.call(context, 'create_packetfilter',
                                packetfilter=packetfilter)

    def delete_packetfilter(self, context, packetfilter):
        LOG.info(_LI("delete_packetfilter: Calling central's"
                     "delete_packetfilter."))
        return self.client.call(context, 'delete_packetfilter',
                                packetfilter=packetfilter)

    def get_packetfilter(self, context, packetfilter):
        LOG.info(_LI("get_packetfilter: Calling central's"
                     "get_packetfilter."))
        return self.client.call(context, 'get_packetfilter',
                                packetfilter=packetfilter)

    def get_all_packetfilters(self, context, packetfilter):
        LOG.info(_LI("get_all_packetfilters: Calling central's"
                     "get_all_packetfilters."))
        return self.client.call(context, 'get_all_packetfilters',
                                packetfilter=packetfilter)

    def create_vrf(self, context, vrf):
        LOG.info(_LI("create_vrf: Calling central's create_vrf."))
        return self.client.call(context, 'create_vrf', vrf=vrf)

    def del_vrf(self, context, vrf, agent_info):
        LOG.info(_LI("del_vrf: Calling central's del_vrf."))
        return self.client.call(context, 'del_vrf', vrf=vrf)

    def get_vrf(self, context, vrf, agent_info):
        LOG.info(_LI("get_vrf: Calling central's get_vrf."))
        return self.client.call(context, 'get_vrf', vrf=vrf)

    def get_vrfs(self, context, vrf, agent_info):
        LOG.info(_LI("get_vrfs: Calling central's get_vrfs."))
        return self.client.call(context, 'get_vrfs', vrf=vrf)

    def create_snat(self, context, snat):
        LOG.info(_LI("create_snat: Calling central's create_snat."))
        return self.client.call(context, 'create_snat', snat=snat)

    def del_snat(self, context, snat):
        LOG.info(_LI("del_snat: Calling central's del_snat."))
        return self.client.call(context, 'del_snat', snat=snat)

    def get_snat(self, context, snat):
        LOG.info(_LI("get_snat: Calling central's get_snat."))
        return self.client.call(context, 'get_snat', snat=snat)

    def get_snats(self, context, snat):
        LOG.info(_LI("get_snats: Calling central's get_snats."))
        return self.client.call(context, 'get_snats', snat=snat)

    def create_securityZone(self, context, sec_infos):
        LOG.info(_LI("create_securityZone: Calling central's"
                     "create_securityZone."))
        return self.client.call(context, 'create_securityZone',
                                sec_infos=sec_infos)

    def securityZone_addif(self, context, sec_infos):
        LOG.info(_LI("securityZone_addif: Calling central's"
                     "securityZone_addif."))
        return self.client.call(context, 'securityZone_addif',
                                sec_infos=sec_infos)

    def securityZone_delif(self, context, sec_infos):
        LOG.info(_LI("securityZone_delif: Calling central's"
                     "securityZone_delif."))
        return self.client.call(context, 'securityZone_delif',
                                sec_infos=sec_infos)

    def delete_securityZone(self, context, sec_infos):
        LOG.info(_LI("del_securityZone: Calling central's del_securityZone."))
        return self.client.call(context, 'delete_securityZone',
                                sec_infos=sec_infos)

    def get_securityZone(self, context, securityzone):
        LOG.info(_LI("get_securityZone: Calling central's get_securityZone."))
        return self.client.call(context, 'get_securityZone',
                                securityzone=securityzone)

    def get_securityZones(self, context, securityzone, agent_info):
        LOG.info(_LI("get_securityZones: Calling central's"
                     "get_securityZones."))
        return self.client.call(context, 'get_securityZones',
                                securityzone=securityzone,
                                agent_info=agent_info)

    def create_staticnat(self, context, staticnat):
        LOG.info(_LI("create_staticnat: Calling central's create_staticnat."))
        return self.client.call(context, 'create_staticnat',
                                staticnat=staticnat)

    def del_staticnat(self, context, staticnat):
        LOG.info(_LI("del_staticnat: Calling central's"
                     "del_staticnat."))
        return self.client.call(context, 'del_staticnat',
                                staticnat=staticnat)

    def get_staticnat(self, context, staticnat):
        LOG.info(_LI("get_staticnat: Calling central's"
                     "get_staticnat."))
        return self.client.call(context, 'get_staticnat',
                                staticnat=staticnat)

    def get_staticnats(self, context, staticnat):
        LOG.info(_LI("get_staticnats: Calling central's"
                     "get_staticnats."))
        return self.client.call(context, 'get_staticnats',
                                staticnat=staticnat)

    def create_syngroup(self, context, syngroup):
        LOG.info(_LI("create syngroup: calling Central's create syngroup"))
        return self.client.call(context, 'create syngroup', syngroup=syngroup)


class CLIManagerAPI(object):
    """
    Client side of the command-line interface operation manager RPC API.

    API version history:

        1.0 - Initial version
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='cli_manager'):
        rpc.init(CONF)
        target = messaging.Target(topic=topic, version=self.RPC_API_VERSION)
        self.client = rpc.get_client(target, version_cap=self.RPC_API_VERSION)

    def reload_topic(self, target_host, topic='cli_manager'):
        """
        Reload topic info base on target_host value to make sure message can be
        send to the corresponding rpc service endpoint
        """
        self.client.target.topic = '%s.%s' % (topic, target_host)

    @classmethod
    def get_instance(cls):
        """
        The rpc.get_client() which is called upon the API object initialization
        will cause a assertion error if the designate.rpc.TRANSPORT isn't setup
        by rpc.init() before.

        This fixes that by creating the rpcapi when demanded.
        """
        global CLI_MANAGER_API
        if not CLI_MANAGER_API:
            CLI_MANAGER_API = cls()
        return CLI_MANAGER_API

    def execute_commands(self, context, req):
        LOG.info(_LI("execute_commands: Calling central's"
                     "execute_commands."))
        return self.client.call(context, 'execute_commands',
                                req=req)
