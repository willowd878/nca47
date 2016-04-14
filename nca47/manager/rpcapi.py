from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from nca47.common import rpc

from nca47.common.i18n import _LI

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

DNS_MANAGER_API = None
FW_MANAGER_API = None


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

    def delete_zone(self, context, zone, zone_id):
        LOG.info(_LI("delete_zone: Calling central's delete_zone."))
        return self.client.call(context, 'delete_zone', zone=zone,
                                zone_id=zone_id)

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
                     "create_zone_record."))
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

    def delete_record(self, context, records_dic, zone_id, rrs_id):
        LOG.info(_LI("delete_zone_record: Calling central's"
                     "delete_zone_record."))
        return self.client.call(context, 'delete_record',
                                records_dic=records_dic, zone_id=zone_id,
                                record_id=rrs_id)

    def del_cache(self, context, cache_dic):
        LOG.info(_LI("del_cache: Calling central's del_cache."))
        return self.client.call(context, 'del_cache', cache_dic=cache_dic)


class FWManagerAPI(object):

    """
    Client side of the Firewall manager RPC API.

    API version history:

        1.0 - Initial version
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='firewall_manager'):
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
        global FW_MANAGER_API
        if not FW_MANAGER_API:
            FW_MANAGER_API = cls()
        return FW_MANAGER_API

    def create_record(self, context, records_dic, zone_id):
        LOG.info(_LI("create_zone_records: Calling central's"
                     "create_zone_record."))
        return self.client.call(context, 'create_record',
                                records_dic=records_dic, zone_id=zone_id)

    # this is a vlan operation
    def creat_vlan(self, context, vlan_infos):
        LOG.info(_LI("creat_vlan: Calling central's"
                     "creat_vlan."))
        return self.client.call(context, 'creat_vlan',
                                vlan_infos=vlan_infos)

    def del_vlan(self, context, id_, vlan_infos):
        LOG.info(_LI("del_vlan: Calling central's"
                     "del_vlan."))
        return self.client.call(context, 'del_vlan',
                                id_=id_, vlan_infos=vlan_infos)

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

    # this is a netservice operation
    def creat_netservice(self, context, netsev_infos):
        LOG.info(_LI("creat_netservice: Calling central's"
                     "creat_netservice."))
        return self.client.call(context, 'creat_netservice',
                                netsev_infos=netsev_infos)

    def del_netservice(self, context, id_, netsev_infos):
        LOG.info(_LI("del_netservice: Calling central's"
                     "del_netservice."))
        return self.client.call(context, 'del_netservice',
                                id_=id_, netsev_infos=netsev_infos)

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

    # this is a addrobj operation
    def add_addrobj(self, context, addrobj_infos):
        LOG.info(_LI("add_addrobj: Calling central's"
                     "add_addrobj."))
        return self.client.call(context, 'add_addrobj',
                                addrobj_infos=addrobj_infos)

    def del_addrobj(self, context, addrobj_infos):
        LOG.info(_LI("del_addrobj: Calling central's"
                     "del_addrobj."))
        return self.client.call(context, 'del_addrobj',
                                id_=addrobj_infos['id'],
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

    # this is a snataddrpool operation
    def add_snataddrpool(self, context, snataddrpool_infos):
        LOG.info(_LI("add_snataddrpool: Calling central's"
                     "add_snataddrpool."))
        return self.client.call(context, 'add_snataddrpool',
                                snataddrpool_infos=snataddrpool_infos)

    def del_snataddrpool(self, context, snataddrpool_infos):
        LOG.info(_LI("del_snataddrpool: Calling central's"
                     "del_snataddrpool."))
        return self.client.call(context, 'del_snataddrpool',
                                id_=snataddrpool_infos['id'],
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
