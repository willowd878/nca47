from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import timeutils
from nca47 import objects
from nca47.manager.cli_manager import CLIManager
from nca47.manager.dns_manager import DNSManager
from nca47.manager.firewall_manager.fw_manager import FirewallManager
from nca47.manager.lb_manager.lb_manager import LBManager
from nca47.common import exception
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
        self.cli_manager = CLIManager.get_instance()
        self.lb_manger = LBManager.get_instance()

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

    def delete_zone(self, context, id):
        """delete target zone"""
        response = self.dns_manager.delete_zone(context, id)
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

    def get_db_zones(self, context, zones):
        """call DB to get all zones"""
        zone_objs = self.dns_manager.get_db_zones(context, zones)
        return zone_objs

    def get_dev_records(self, context, zone_id):
        """ get all records from device"""
        records = self.dns_manager.get_dev_records(context, zone_id)
        return records

    def get_db_records(self, context, zone_id):
        """get all records belong special zone from db"""
        records = self.dns_manager.get_db_records(context, zone_id)
        return records

    def query_records(self, context, rrs):
        """get all records belong special zone from db"""
        records = self.dns_manager.query_records(context, rrs)
        return records

    # TODO this is a test environment method,and it will
    # be deleted after deployment in a production environment
    # Begin
    def query_records_in_test_env(self, context, rrs):
        """get all records belong special zone from db"""
        records = self.dns_manager.query_records_in_test_env(context, rrs)
        return records

    def create_record_in_test_env(self, context, rrs):
        """get all records belong special zone from db"""
        records = self.dns_manager.create_record_in_test_env(context, rrs)
        return records
    # End test environment

    def get_record_from_db(self, context, record_id):
        """get target record detail info from db"""
        record = self.dns_manager.get_record_from_db(context, record_id)
        return record

    def create_record(self, context, record):
        """create one record for special zone"""
        record = self.dns_manager.create_record(context, record)
        return record

    def update_record(self, context, record):
        """update target record info"""
        record = self.dns_manager.update_record(context, record)
        return record

    def delete_record(self, context, rrs):
        """delete target record"""
        response = self.dns_manager.delete_record(context, rrs)
        return response

    def del_cache(self, context, domain):
        """clean cache from dns device"""
        response = self.dns_manager.del_cache(context, domain)
        return response

    def create_region(self, context, region):
        """"create new region"""
        zone_obj = self.dns_manager.create_region(context, region)
        return zone_obj

    def delete_region(self, context, id):
        """delete target region"""
        response = self.dns_manager.delete_region(context, id)
        return response

    def create_member(self, context, member):
        """"create new member"""
        zone_obj = self.dns_manager.create_member(context, member)
        return zone_obj

    def delete_member(self, context, id):
        """delete target member"""
        response = self.dns_manager.delete_member(context, id)
        return response

    def get_members(self, context):
        """show target region details info from db"""
        zone_obj = self.dns_manager.get_members(context)
        return zone_obj

    def get_db_members(self, context, members):
        """call DB to get all members"""
        members_objs = self.dns_manager.get_db_members(context, members)
        return members_objs

    def get_one_member(self, context, members):
        """call DB to get all members"""
        members_objs = self.dns_manager.get_one_member(context, members)
        return members_objs

    def get_region_db_detail(self, context, id):
        """show target region details info from db"""
        zone_obj = self.dns_manager.get_region_db_detail(context, id)
        return zone_obj

    def get_all_db_region(self, context):
        """call DB to get all regions"""
        zone_objs = self.dns_manager.get_all_db_region(context)
        return zone_objs

    def get_db_regions(self, context, regions):
        """call DB to get all regions"""
        regions_objs = self.dns_manager.get_db_regions(context, regions)
        return regions_objs

    def create_sp_policy(self, context, proximity):
        """"create new proximity"""
        zone_obj = self.dns_manager.create_sp_policy(context, proximity)
        return zone_obj

    def delete_sp_policy(self, context, id):
        """delete target proximity"""
        response = self.dns_manager.delete_sp_policy(context, id)
        return response

    def update_sp_policy(self, context, proximity, id):
        """update target proximity"""
        zone_obj = self.dns_manager.update_sp_policy(context, proximity, id)
        return zone_obj

    def get_sp_policy(self, context, id):
        """get policy from device"""
        # handling policy method in RPC
        response = self.dns_manager.get_sp_policy(context, id)
        return response

    def get_sp_policys(self, context):
        """get policys from device"""
        # handling policys method in RPC
        response = self.dns_manager.get_sp_policys(context)
        return response

    def get_proximity_db_detail(self, context, id):
        """show target proximity details info from db"""
        zone_obj = self.dns_manager.get_proximity_db_detail(context, id)
        return zone_obj

    def get_all_db_proximity(self, context):
        """call DB to get all proximitys"""
        zone_objs = self.dns_manager.get_all_db_proximity(context)
        return zone_objs

    def get_db_proximitys(self, context, proximitys):
        """call DB to get all proximitys"""
        proximitys_objs = self.dns_manager.get_db_proximitys(
            context, proximitys)
        return proximitys_objs

    def get_gmembers_db(self, context, dic):
        """get all gmembers"""
        response = self.dns_manager.get_gmembers_db(context, dic)
        return response

    def get_one_gmember_db(self, context, gmember_uuid):
        """get a gmember"""
        response = self.dns_manager.get_one_gmember_db(context, gmember_uuid)
        return response

    def create_gmember(self, context, dic):
        """create a gmember"""
        response = self.dns_manager.create_gmember(context, dic)
        return response

    def update_gmember(self, context, dic, gmember_uuid):
        """update gmember info"""
        response = self.dns_manager.update_gmember(context, dic, gmember_uuid)
        return response

    def delete_gmember(self, context, gmember_uuid):
        """delete target gmember"""
        response = self.dns_manager.delete_gmember(context, gmember_uuid)
        return response

    def get_hm_templates_db(self, context, dic):
        """get all hm_templates"""
        response = self.dns_manager.get_hm_templates_db(context, dic)
        return response

    def get_one_hm_template_db(self, context, template_uuid):
        """get a hm_template"""
        return self.dns_manager.get_one_hm_template_db(context,
                                                       template_uuid)

    def create_hm_template(self, context, dic):
        """create a hm_template"""
        response = self.dns_manager.create_hm_template(context, dic)
        return response

    def update_hm_template(self, context, dic, template_uuid):
        """update hm_template info"""
        response = self.dns_manager.update_hm_template(context,
                                                       dic, template_uuid)
        return response

    def delete_hm_template(self, context, template_uuid):
        """delete target hm_template"""
        response = self.dns_manager.delete_hm_template(context, template_uuid)
        return response

    # this is a vlan operation
    def create_vlan(self, context, dic):
        return self.fw_manager.create_vlan(context, dic)

    def del_vlan(self, context, dic):
        return self.fw_manager.del_vlan(context, dic)

    def get_vlan(self, context, id):
        return self.fw_manager.get_vlan(context, id)

    def get_vlans(self, context, dic):
        return self.fw_manager.get_vlans(context, dic)

    # this is a netservice operation
    def create_netservice(self, context, netsev_infos):
        return self.fw_manager.create_netservice(context, netsev_infos)

    def del_netservice(self, context, netsev_infos):
        return self.fw_manager.del_netservice(context, netsev_infos)

    def get_netservice(self, context, id):
        return self.fw_manager.get_netservice(context, id)

    def get_netservices(self, context, netsev_infos):
        return self.fw_manager.get_netservices(context, netsev_infos)

    def get_netservices_by_fuzzy_query(self, context, netsev_infos):
        return self.fw_manager.get_netservices_by_fuzzy_query(context,
                                                              netsev_infos)

    # this is a addrobj operation
    def add_addrobj(self, context, addrobj_infos):
        return self.fw_manager.add_addrobj(context, addrobj_infos)

    def delete_addrobj(self, context, addrobj_infos):
        return self.fw_manager.delete_addrobj(context, addrobj_infos)

    def get_addrobj(self, context, id):
        return self.fw_manager.get_addrobj(context, id)

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

    def get_vfw(self, context, id):
        return self.fw_manager.get_vfw(context, id)

    def get_all_vfws(self, context, vfw):
        return self.fw_manager.get_all_vfws(context, vfw)

    def get_vfws_by_fuzzy_query(self, context, vfw):
        return self.fw_manager.get_vfws_by_fuzzy_query(context, vfw)

    def create_dnat(self, context, dnat):
        return self.fw_manager.create_dnat(context, dnat)

    def delete_dnat(self, context, dnat):
        return self.fw_manager.delete_dnat(context, dnat)

    def get_dnat(self, context, id):
        return self.fw_manager.get_dnat(context, id)

    def get_all_dnats(self, context, dnat):
        return self.fw_manager.get_all_dnats(context, dnat)

    def get_dnats_by_fuzzy_query(self, context, dnat):
        return self.fw_manager.get_dnats_by_fuzzy_query(context, dnat)

    def create_packetfilter(self, context, packetfilter):
        return self.fw_manager.create_packetfilter(context, packetfilter)

    def delete_packetfilter(self, context, packetfilter):
        return self.fw_manager.delete_packetfilter(context, packetfilter)

    def get_packetfilter(self, context, id):
        return self.fw_manager.get_packetfilter(context, id)

    def get_all_packetfilters(self, context, packetfilter):
        return self.fw_manager.get_all_packetfilters(context, packetfilter)

    # this is a vfw operation
    def create_vrf(self, context, fw_object):
        return self.fw_manager.create_vrf(context, fw_object)

    def del_vrf(self, context, fw_object):
        return self.fw_manager.del_vrf(context, fw_object)

    def get_vrf(self, context, id):
        return self.fw_manager.get_vrf(context, id)

    def get_vrfs(self, context, fw_object):
        return self.fw_manager.get_vrfs(context, fw_object)

    # this is a snat operation
    def create_snat(self, context, fw_object):
        return self.fw_manager.create_snat(context, fw_object)

    def del_snat(self, context, fw_object):
        return self.fw_manager.del_snat(context, fw_object)

    def get_snats_by_fuzzy_query(self, context, fw_object):
        return self.fw_manager.get_snats_by_fuzzy_query(context, fw_object)

    def get_snat(self, context, id):
        return self.fw_manager.get_snat(context, id)

    def get_snats(self, context, fw_object):
        return self.fw_manager.get_snats(context, fw_object)

    # this is a securityZone operation
    def create_securityzone(self, context, fw_object):
        return self.fw_manager.create_securityzone(context, fw_object)

    def update_securityzone(self, context, fw_object):
        return self.fw_manager.update_securityzone(context, fw_object)

    def delete_securityzone(self, context, fw_object):
        return self.fw_manager.delete_securityzone(context, fw_object)

    def get_securityzone(self, context, id):
        return self.fw_manager.get_securityzone(context, id)

    def get_securityzones(self, context, fw_object):
        return self.fw_manager.get_securityzones(context, fw_object)

    def securityzone_addif(self, context, fw_object):
        return self.fw_manager.securityzone_addif(context, fw_object)

    def securityzone_delif(self, context, fw_object):
        return self.fw_manager.securityzone_delif(context, fw_object)

    # this is a staticnat operation
    def create_staticnat(self, context, fw_object):
        return self.fw_manager.create_staticnat(context, fw_object)

    def del_staticnat(self, context, fw_object):
        return self.fw_manager.del_staticnat(context, fw_object)

    def get_staticnat(self, context, fw_object):
        return self.fw_manager.get_staticnat(context, fw_object)

    def get_staticnats_by_fuzzy_query(self, context, fw_object):
        return self.fw_manager.get_staticnats_by_fuzzy_query(context,
                                                             fw_object)

    # this is a gslb_zone operation
    def create_gslb_zone(self, context, dns_object):
        return self.dns_manager.create_gslb_zone(context, dns_object)

    def del_gslb_zone(self, context, dns_object):
        return self.dns_manager.del_gslb_zone(context, dns_object)

    def update_gslb_zone(self, context, zone_id, dns_object):
        return self.dns_manager.update_gslb_zone(context, zone_id, dns_object)

    def get_gslb_zone(self, context, dns_object):
        return self.dns_manager.get_gslb_zone(context, dns_object)

    def get_gslb_zones(self, context, dns_object):
        return self.dns_manager.get_gslb_zones(context, dns_object)

    def create_syngroup(self, context, syngroup_dict):
        return self.dns_manager.create_syngroup(context, syngroup_dict)

    def update_syngroup(self, context, syngroup_dict):
        return self.dns_manager.update_syngroup(context, syngroup_dict)

    def remove_syngroup(self, context, syngroup_id):
        return self.dns_manager.remove_syngroup(context, syngroup_id)

    def get_syngroups(self, context, values):
        return self.dns_manager.get_syngroups(context, values)

    def get_syngroup(self, context, syngroup_id):
        return self.dns_manager.get_syngroup(context, syngroup_id)

    def delete_syngroup(self, context, values):
        return self.dns_manager.delete_syngroup(context, values)

    def create_gpool(self, context, gpool_dict):
        return self.dns_manager.create_gpool(context, gpool_dict)

    def update_gpool(self, context, gpool_dict):
        return self.dns_manager.update_gpool(context, gpool_dict)

    def get_gpools(self, context, values):
        return self.dns_manager.get_gpools(context, values)

    def get_gpool(self, context, gpool_id):
        return self.dns_manager.get_gpool(context, gpool_id)

    def delete_gpool(self, context, values):
        return self.dns_manager.delete_gpool(context, values)

    def create_gmap(self, context, gmap_dict):
        return self.dns_manager.create_gmap(context, gmap_dict)

    def update_gmap(self, context, gmap_dict):
        return self.dns_manager.update_gmap(context, gmap_dict)

    def get_gmaps(self, context, values):
        return self.dns_manager.get_gmaps(context, values)

    def get_gmap(self, context, gmap_id):
        return self.dns_manager.get_gmap(context, gmap_id)

    def delete_gmap(self, context, values):
        return self.dns_manager.delete_gmap(context, values)

    def execute_commands(self, context, commands):
        return self.cli_manager.execute_commands(context, commands)

    def create_pool(self, context, real_dic):
        return self.lb_manger.create_pool(context, real_dic)

    def create_lb_member(self, context, member_dic):
        return self.lb_manger.create_member(context, member_dic)

    def create_vip(self, context, vip_dic):
        return self.lb_manger.create_vip(context, vip_dic)

    def create_server(self, context, server_dic):
        return self.lb_manger.create_server(context, server_dic)

    def delete_real_service(self, context, real_dic):
        return self.lb_manger.delete_real_service(context, real_dic)

    def get_agent_list(self, context):
        agents = objects.Agent(context)
        agent_list = agents.get_objects(context)
        for agent in agent_list:
            print CONF.agent.agent_down_time
            is_down = timeutils.is_older_than(agent.update_time,
                                              CONF.agent.agent_down_time)
            agent_status = "xxx" if is_down else ':-)'
            agent['status'] = agent_status
        return agent_list
