from oslo_config import cfg
from oslo_db import exception as db_exception
from oslo_log import log as logging
from nca47 import objects
from nca47.common.i18n import _LE
from nca47.manager.dns_manager import DNSManager
from nca47.manager.firewall_manager.fw_manager import FirewallManager
CONF = cfg.CONF
LOG = logging.getLogger(__name__)

CENTRAL_MANAGER = None


class CentralManager(object):

    """
    nca47 central handler class, using for response api client requests,
    dispatch client request to dns, firewall or loadbalancer manager
    """

    def __init__(self):
        self.dns_manager = DNSManager.get_instance()
        self.fw_manager = FirewallManager.get_instance()

    @classmethod
    def get_instance(cls):
        global CENTRAL_MANAGER
        if not CENTRAL_MANAGER:
            CENTRAL_MANAGER = cls()
        return CENTRAL_MANAGER

    def create_zone(self, context, zone):
        """"create new zone"""
        zone_obj = self.dns_manager.create_zone(context, zone)
        return zone_obj

    def update_zone(self, context, zone, id):
        """update target zone"""
        zone_obj = self.dns_manager.update_zone(context, zone, id)
        return zone_obj

    def update_zone_owners(self, context, zone, id):
        """update target zone's owners"""
        zone_obj = self.dns_manager.update_zone_owners(context, zone, id)
        return zone_obj

    def delete_zone(self, context, zone, id):
        """delete target zone"""
        response = self.dns_manager.delete_zone(context, zone, id)
        return response

    def get_zones(self, context):
        """get zones from device"""
        # handling zones method in RPC
        response = self.dns_manager.get_zones(context)
        return response

    def get_zone_db_details(self, context, id):
        """show target zone details info from db"""
        zone_obj = self.dns_manager.get_zone_db_details(context, id)
        return zone_obj

    def get_all_db_zone(self, context):
        """call DB to get all zones"""
        zone_objs = self.dns_manager.get_all_db_zone(context)
        return zone_objs

    def get_dev_records(self, context, zone_id):
        """ get all records from device"""
        records = self.dns_manager.get_dev_records(context, zone_id)
        return records

    def get_db_records(self, context, zone_id):
        """get all records belong special zone from db"""
        records = self.dns_manager.get_db_records(context, zone_id)
        return records

    def get_record_from_db(self, context, record_id):
        """get target record detail info from db"""
        record = self.dns_manager.get_record_from_db(context, record_id)
        return record

    def create_record(self, context, record, zone_id):
        """create one record for special zone"""
        record = self.dns_manager.create_record(context, record, zone_id)
        return record

    def update_record(self, context, record, zone_id, record_id):
        """update target record info"""
        record = self.dns_manager.update_record(context, record, zone_id,
                                                record_id)
        return record

    def delete_record(self, context, record, zone_id, record_id):
        """delete target record"""
        response = self.dns_manager.delete_record(context, record, zone_id,
                                                  record_id)
        return response

    def del_cache(self, context, domain):
        """clean cache from dns device"""
        response = self.dns_manager.del_cache(context, domain)
        return response

    def add_device_agent(self, agent):
        context = []
        agent_obj = objects.AgentZone(context, **agent)
        # Check the zone which have same name if is exist in DB
        try:
            # create the zone in db
            quit_obj = agent_obj.get_objects(context, **agent_obj.as_dict())
            if len(quit_obj) != 0:
                return True
            agent_obj.create(context, agent_obj.as_dict())
        except db_exception:
            LOG.error(_LE("Create/Insert db operation failed!"))
            raise db_exception
        return True

    # this is a vlan operation
    def create_vlan(self, context, dic):
        return self.fw_manager.create_vlan(context, dic)

    def del_vlan(self, context, dic):
        return self.fw_manager.del_vlan(context, dic)

    def get_vlan(self, context, dic):
        return self.fw_manager.get_vlan(context, dic)

    def get_vlans(self, context, dic):
        return self.fw_manager.get_vlans(context, dic)

    # this is a netservice operation
    def creat_netservice(self, context, netsev_infos):
        return self.fw_manager.creat_netservice(context, netsev_infos)

    def del_netservice(self, context, netsev_infos):
        return self.fw_manager.del_netservice(context, netsev_infos)

    def get_netservice(self, context, netsev_infos):
        return self.fw_manager.get_netservice(context, netsev_infos)

    def get_netservices(self, context, netsev_infos):
        return self.fw_manager.get_netservices(context, netsev_infos)

    # this is a addrobj operation
    def add_addrobj(self, context, addrobj_infos):
        return self.fw_manager.add_addrobj(context, addrobj_infos)

    def del_addrobj(self, context, addrobj_infos):
        return self.fw_manager.del_addrobj(context, addrobj_infos)

    def get_addrobj(self, context, addrobj_infos):
        return self.fw_manager.get_addrobj(context, addrobj_infos)

    def get_addrobjs(self, context, addrobj_infos):
        return self.fw_manager.get_addrobjs(context, addrobj_infos)

    # this is a snataddrpool operation
    def add_snataddrpool(self, context, snataddrpool_infos):
        return self.fw_manager.add_snataddrpool(context, snataddrpool_infos)

    def del_snataddrpool(self, context, snataddrpool_infos):
        return self.fw_manager.del_snataddrpool(context, snataddrpool_infos)

    def get_snataddrpool(self, context, snataddrpool_infos):
        return self.fw_manager.get_snataddrpool(context, snataddrpool_infos)

    def get_snataddrpools(self, context, snataddrpool_infos):
        return self.fw_manager.get_snataddrpools(context, snataddrpool_infos)

    def create_vfw(self, context, vfw):
        return self.fw_manager.create_vfw(context, vfw)

    def delete_vfw(self, context, vfw):
        return self.fw_manager.delete_vfw(context, vfw)

    def get_vfw(self, context, vfw):
        return self.fw_manager.get_vfw(context, vfw)

    def get_all_vfws(self, context, vfw):
        return self.fw_manager.get_all_vfws(context, vfw)

    def create_dnat(self, context, dnat):
        return self.fw_manager.create_dnat(context, dnat)

    def delete_dnat(self, context, dnat):
        return self.fw_manager.delete_dnat(context, dnat)

    def get_dnat(self, context, dnat):
        return self.fw_manager.get_dnat(context, dnat)

    def get_all_dnats(self, context, dnat):
        return self.fw_manager.get_all_dnats(context, dnat)

    def create_packetfilter(self, context, packetfilter):
        return self.fw_manager.create_packetfilter(context, packetfilter)

    def delete_packetfilter(self, context, packetfilter):
        return self.fw_manager.delete_packetfilter(context, packetfilter)

    def get_packetfilter(self, context, packetfilter):
        return self.fw_manager.get_packetfilter(context, packetfilter)

    def get_all_packetfilters(self, context, packetfilter):
        return self.fw_manager.get_all_packetfilters(context, packetfilter)

    # this is a vfw operation
    def create_vrf(self, context, fw_object):
        return self.fw_manager.create_vrf(context, fw_object)

    def del_vrf(self, context, fw_object):
        return self.fw_manager.del_vrf(context, fw_object)

    def get_vrf(self, context, fw_object):
        return self.fw_manager.get_vrf(context, fw_object)

    def get_vrfs(self, context, fw_object):
        return self.fw_manager.get_vrfs(context, fw_object)

    # this is a snat operation
    def create_snat(self, context, fw_object):
        return self.fw_manager.create_snat(context, fw_object)

    def del_snat(self, context, fw_object):
        return self.fw_manager.del_snat(context, fw_object)

    def get_snat(self, context, fw_object):
        return self.fw_manager.get_snat(context, fw_object)

    def get_snats(self, context, fw_object):
        return self.fw_manager.get_snats(context, fw_object)

    # this is a securityZone operation
    def create_securityZone(self, context, fw_object):
        return self.fw_manager.create_securityZone(context, fw_object)

    def update_securityZone(self, context, fw_object):
        return self.fw_manager.update_securityZone(context, fw_object)

    def del_securityZone(self, context, fw_object):
        return self.fw_manager.del_securityZone(context, fw_object)

    def get_securityZone(self, context, fw_object):
        return self.fw_manager.get_securityZone(context, fw_object)

    def get_securityZones(self, context, fw_object):
        return self.fw_manager.get_securityZones(context, fw_object)

    # this is a staticnat operation
    def create_staticnat(self, context, fw_object):
        return self.fw_manager.create_staticnat(context, fw_object)

    def del_staticnat(self, context, fw_object):
        return self.fw_manager.del_staticnat(context, fw_object)

    def get_staticnat(self, context, fw_object):
        return self.fw_manager.get_staticnat(context, fw_object)

    def get_staticnats(self, context, fw_object):
        return self.fw_manager.get_staticnats(context, fw_object)
