from oslo_serialization import jsonutils as json
from oslo_config import cfg
from oslo_log import log as logging
from nca47.agent.firewall_driver import soap_client
from nca47.api.controllers.v1 import tools
from nca47.common.exception import DeviceError as deviceError

CONF = cfg.CONF
LOG = logging.getLogger(__name__)
FW_DRIVER = None


class fw_driver(object):

    def __init__(self):
        self.ws_client = soap_client.fw_client.get_instance()

    @classmethod
    def get_instance(cls):
        global FW_DRIVER
        if not FW_DRIVER:
            FW_DRIVER = cls()
        return FW_DRIVER

    def create_vlan(self, context, vlan_infos):
        """  creat vlan to webservice  """
        vlan_id = int(vlan_infos["vlan_number"])
        ip_addr = tools.joinString(vlan_infos["ipaddr"])
        if_names = tools.joinString(vlan_infos["ifnames"])
        url_dir = "/func/web_main/wsdl/vlan/vlan.wsdl"
        LOG.info("creat vlan to webservice: " + url_dir)
        service = self.ws_client.get_client(url_dir)
        vlan_dic = {}
        vlan_dic['vlanId'] = vlan_id
        vlan_dic['ipAddr'] = ip_addr
        vlan_dic['ifNames'] = if_names
        try:
            response = service.addVlan(**vlan_dic)
        except Exception:
            raise deviceError
        return response

    def del_vlan(self, context, vlan_infos):
        """  del vlan to webservice  """
        vlan_id = int(vlan_infos["vlan_number"])
        if_names = tools.joinString(vlan_infos["ifnames"])
        # ws_ip = view['agent_nat_ip']
        other_ip = "/func/web_main/wsdl/vlan/vlan.wsdl"
        # url = "%s%s" % (ws_ip, other_ip)
        url = other_ip
        LOG.info("del vlan to webservice: " + url)
        service = self.ws_client.get_client(url)
        response = service.delVlan(vlan_id, if_names)
        return response

    def get_dev_vlan(self, context, view, dic):
        """  get a vlan to webservice  """
        vlan_id = dic["vlan_id"]
        ws_ip = view['agent_nat_ip']
        other_ip = "/func/web_main/wsdl/vlan/vlan.wsdl"
        url = "%s%s" % (ws_ip, other_ip)
        LOG.info("get a vlan to webservice: " + url)
        client = self.ws_client.get_client(url)
        response = client.service.getVlan(vlan_id)
        # TODO zhuxy return , print only for test
        print json.loads(response)

    def get_dev_vlans(self, context, view, dic):
        """  get vlans to webservice  """
        ws_ip = view['agent_nat_ip']
        other_ip = "/func/web_main/wsdl/vlan/vlan.wsdl"
        url = "%s%s" % (ws_ip, other_ip)
        LOG.info("get vlans to webservice: " + url)
        client = self.ws_client.get_client(url)
        response = client.service.getVlanAll()
        # TODO zhuxy return , print only for test
        print json.loads(response)

    # this is a netservice operation
    def create_netservice(self, context, dic):
        """  creat netservice to webservice  """
        wsdl = {}
        wsdl["name"] = dic["name"]
        wsdl["proto"] = dic["proto"]
        wsdl["port"] = dic["port"]
        wsdl["vfwName"] = dic["vfwname"]
        url = "/func/web_main/wsdl/netservice/netservice.wsdl"
        LOG.info("creat netservice to webservice: " + url)
        client = self.ws_client.get_client(url)
        try:
            response = client.addService(**wsdl)
        except Exception:
            raise deviceError
        return response

    def del_netservice(self, context, dic):
        """  delete netservice to webservice  """
        wsdl = {}
        wsdl["name"] = dic["name"]
        wsdl["vfwName"] = dic["vfwname"]
        url = "/func/web_main/wsdl/netservice/netservice.wsdl"
        LOG.info("delete netservice to webservice: " + url)
        client = self.ws_client.get_client(url)
        try:
            response = client.delService(**wsdl)
        except Exception:
            raise deviceError
        return response

    def get_dev_netservice(self, context, view, dic):
        """  get a netservice to webservice  """
        ws_ip = view['agent_nat_ip']
        name = dic["name"]
        vfwName = dic["vfwname"]
        other_ip = "/func/web_main/wsdl/netservice/netservice.wsdl"
        url = "%s%s" % (ws_ip, other_ip)
        LOG.info("get a netservice to webservice: " + url)
        client = self.ws_client.get_client(url)
        response = client.service.getService(name, vfwName)
        # TODO zhuxy return , print only for test
        print json.loads(response)

    def get_dev_netservices(self, context, view, dic):
        """  get all netservices to webservice  """
        ws_ip = view['agent_nat_ip']
        vfwName = dic["vfwname"]
        other_ip = "/func/web_main/wsdl/netservice/netservice.wsdl"
        url = "%s%s" % (ws_ip, other_ip)
        LOG.info("get all netservices to webservice: " + url)
        client = self.ws_client.get_client(url)
        response = client.service.getServiceAll(vfwName)
        # TODO zhuxy return , print only for test
        print json.loads(response)

    # this is a addrobj operation
    def add_addrobj(self, context, addr_infos):
        """  create addrobj to webservice  """
        url = "/func/web_main/wsdl/netaddr/netaddr.wsdl"
        LOG.info("create addrobj to webservice: " + url)
        service = self.ws_client.get_client(url)
        # response = service.addAddrObj(addr_infos)
        # TODO return , print only for test
        try:
            response = service.addAddrObj(**addr_infos)
        except Exception:
            raise deviceError
        return response

    def del_addrobj(self, context, dic):
        """  delete addrobj to webservice  """
        # ws_ip = view['agent_nat_ip']
        # name = dic["name"]
        # vfwName = dic["vfwname"]
        url = "/func/web_main/wsdl/netaddr/netaddr.wsdl"
        # url = "%s" % ( other_ip)
        LOG.info("delete addrobj to webservice: " + url)
        client = self.ws_client.get_client(url)
        response = client.delAddrObj(**dic)
        # TODO return , print only for test
        return response

    def get_dev_addrobj(self, context, view, dic):
        """  get a addrobj to webservice  """
        ws_ip = view['agent_nat_ip']
        name = dic["name"]
        vfwName = dic["vfwname"]
        other_ip = "/func/web_main/wsdl/netaddr/netaddr.wsdl"
        url = "%s%s" % (ws_ip, other_ip)
        LOG.info("get a addrobj to webservice: " + url)
        client = self.ws_client.get_client(url)
        response = client.service.getAddrObj(name, vfwName)
        # TODO return , print only for test
        print json.loads(response)

    def get_dev_addrobjs(self, context, view, dic):
        """  get a addrobj to webservice  """
        ws_ip = view['agent_nat_ip']
        vfwName = dic["vfwname"]
        other_ip = "/func/web_main/wsdl/netaddr/netaddr.wsdl"
        url = "%s%s" % (ws_ip, other_ip)
        LOG.info("get a addrobj to webservice: " + url)
        client = self.ws_client.get_client(url)
        response = client.service.getAddrObjAll(vfwName)
        # TODO return , print only for test
        print json.loads(response)

    def create_packetfilter(self, context, packet_info):
        """create packetfilter"""
        # url = agent_info_dict['agent_ip']

        url = "/func/web_main/wsdl/pf_policy/pf_policy/pf_policy.wsdl"
        trans_info_dict = {
            'name': '',
            'srcZoneName': '',
            'dstZoneName': "",
            "srcIpObjNames": '',
            'dstIpObjNames': "",
            'serviceNames': '',
            'action': '',
            'log': '',
            'vfwName': ''
        }
        for key in trans_info_dict.keys():
            if key.lower() in packet_info.keys():
                trans_info_dict[key] = str(packet_info[key.lower()])
        trans_info_dict['action'] = int(trans_info_dict['action'])
        trans_info_dict['log'] = int(trans_info_dict['log'])
        client = self.ws_client.get_client(url)
        LOG.info("create fw_packetfilter:" + url)
        try:
            response = client.addPacketFilter(**trans_info_dict)
        except Exception as e:
            print e
            raise e
        return response
        # if ret == 0:
        #     return 0
        # else:
        #     return 'soap fault'

    def delete_packetfilter(self, context, packet_info_dict):
        """delete packetfilter"""
        url = '/func/web_main/wsdl/pf_policy/pf_policy/pf_policy.wsdl'
        LOG.info("delete fw_packetfilter:" + url)
        client = self.ws_client.get_client(url)
        LOG.info("create fw_packetfilter:" + url)
        ret = client.delPacketFilter(**packet_info_dict)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def get_dev_packetfilter(self, context, packet_info_dict, agent_info_dict):
        """get packetfilter"""
        url = agent_info_dict['agent_ip']
        url += '/func/web_main/webservice/security_zone/security_zone'
        LOG.info("get fw_SecurityZone:" + url)
        trans_info_dict = {
            'name': '',
            'vfwName': ''
        }
        for key in trans_info_dict.keys():
            if key.lower() in packet_info_dict.keys():
                trans_info_dict[key] = packet_info_dict[key.lower()]
        client = self.ws_client.get_client(url)
        ret = client.getZone(**packet_info_dict)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def getall_dev_packetfilter(self, context,
                                packet_info_dict, agent_info_dict):
        """GetAll packetfilter"""
        url = agent_info_dict['agent_ip']
        url += '/func/web_main/webservice/security_zone/security_zone'
        LOG.info("getall fw_SecurityZone:" + url)
        client = self.ws_client.get_client(url)
        trans_info_dict = {
            'name': '',
        }
        for key in trans_info_dict.keys():
            if key.lower() in packet_info_dict.keys():
                trans_info_dict[key] = packet_info_dict[key.lower()]
        ret = client.getZoneAll(**packet_info_dict)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def create_securityzone(self, context, sec_infos):
        """create securityZone"""
        # url = agent_info_dict['agent_ip']

        url = '/func/web_main/wsdl/security_zone/security_zone.wsdl'
        # url_dir = "/func/web_main/wsdl/vlan/vlan.wsdl"
        LOG.info("create fw_SecurityZone:" + url)
        client = self.ws_client.get_client(url)
        trans_info_dict = dict()
        trans_info_dict['ifNames'] = tools.joinString(sec_infos['ifnames'])
        trans_info_dict['name'] = sec_infos['name']
        trans_info_dict['vfwName'] = sec_infos['vfwname']
        trans_info_dict['priority'] = sec_infos['priority']
        try:
            ret = client.addZone(**trans_info_dict)
        except Exception as e:
            raise e
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def delete_securityzone(self, context, sec_infos):
        """delete SecurityZone"""
        url = '/func/web_main/wsdl/security_zone/security_zone.wsdl'
        LOG.info("delete fw_SecurityZone:" + url)
        client = self.ws_client.get_client(url)
        ret = client.delZone(**sec_infos)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def get_dev_securityzone(self, context, zone_info_dict, agent_info_dict):
        """get SecurityZone if """
        url = agent_info_dict['agent_ip']
        url += '/func/web_main/webservice/security_zone/security_zone'
        LOG.info("get fw_SecurityZone:" + url)
        trans_info_dict = {
            'name': '',
            'vfwName': ''
        }
        for key in trans_info_dict.keys():
            if key.lower() in zone_info_dict.keys():
                trans_info_dict[key] = zone_info_dict[key.lower()]
        client = self.ws_client.get_client(url)
        ret = client.addZoneIf(**zone_info_dict)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def getall_dev_securityzone(
            self,
            context,
            zone_info_dict,
            agent_info_dict):
        """GetAll SecurityZone"""
        url = agent_info_dict['agent_ip']
        url += '/func/web_main/webservice/security_zone/security_zone'
        LOG.info("getall fw_SecurityZone:" + url)
        client = self.ws_client.get_client(url)
        trans_info_dict = {
            'name': '',
        }
        for key in trans_info_dict.keys():
            if key.lower() in zone_info_dict.keys():
                trans_info_dict[key] = zone_info_dict[key.lower()]
        ret = client.getZoneAll(**zone_info_dict)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def securityzone_addif(self, context, sec_infos):
        """GetAll SecurityZone"""
        url = '/func/web_main/wsdl/security_zone/security_zone.wsdl'
        LOG.info("addif fw_SecurityZone:" + url)
        client = self.ws_client.get_client(url)
        ret = client.addZoneIf(**sec_infos)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def securityzone_delif(self, context, sec_infos):
        """GetAll SecurityZone"""
        url = '/func/web_main/wsdl/security_zone/security_zone.wsdl'
        LOG.info("delif fw_SecurityZone:" + url)
        client = self.ws_client.get_client(url)
        ret = client.delZoneIf(**sec_infos)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def create_staticnat(self, context, static_info_dict):
        """  creat staticnat to webservice  """

        static_dic = {}
        static_dic["name"] = static_info_dict["name"]
        static_dic["ifName"] = static_info_dict["ifname"]
        static_dic["lanIp"] = static_info_dict["lanip"]
        static_dic["wanIp"] = static_info_dict["wanip"]
        static_dic["slot"] = static_info_dict["slot"]
        static_dic["vfwName"] = static_info_dict["vfwname"]
        url_dir = "/func/web_main/wsdl/nat/NatManager.wsdl"
        LOG.info("creat staticnat to webservice: " + url_dir)
        service = self.ws_client.get_client(url_dir)
        try:
            response = service.addStaticNat(**static_dic)
        except Exception as _e:
            raise deviceError
        return response

    def delete_staticnat(self, context, static_info_dict):
        """  creat staticnat to webservice  """
        static_dic = {}
        static_dic["name"] = static_info_dict["name"]
        static_dic["vfwName"] = static_info_dict["vfwName"]
        url_dir = "/func/web_main/wsdl/nat/NatManager.wsdl"
        LOG.info("creat staticnat to webservice: " + url_dir)
        service = self.ws_client.get_client(url_dir)
        try:
            response = service.delStaticNat(**static_dic)
        except Exception as _e:
            raise deviceError
            return response

    def get_dev_staticnat(self, context, static_info_dict, agent_info_dict):
        # get staticnat
        """  creat staticnat to webservice  """
        static_dic = {}
        static_dic["name"] = static_info_dict["name"]
        static_dic["vfwName"] = static_info_dict["vfwName"]
        url_dir = "/func/web_main/wsdl/nat/NatManager.wsdl"
        LOG.info("creat staticnat to webservice: " + url_dir)
        service = self.ws_client.get_client(url_dir)
        try:
            response = service.getStaticNat(**static_dic)
        except Exception as _e:
            raise deviceError
        return response

    def getall_dev_staticnat(self, context, static_info_dict, agent_info_dict):
        # get all staticnat
        """  creat staticnat to webservice  """
        static_dic = {}
        static_dic["vfwName"] = static_info_dict["vfwName"]
        url_dir = "/func/web_main/wsdl/nat/nat.wsdl"
        LOG.info("creat staticnat to webservice: " + url_dir)
        service = self.ws_client.get_client(url_dir)
        try:
            response = service.getStaticNatAll(**static_dic)
        except Exception as _e:
            raise deviceError
        return response

    def create_dnat(self, context, dic):
        url = '/func/web_main/wsdl/nat/NatManager.wsdl'
        LOG.info("create fw_DNat:" + url)
        wsdl = {}
        wsdl["name"] = dic["name"]
        wsdl["inIfName"] = dic["inifname"]
        wsdl["wanIp"] = dic["wanip"]
        keys = dic.keys()
        if "wantcpports" in keys:
            wsdl["wanTcpPorts"] = dic["wantcpports"]
        if "wanudpports" in keys:
            wsdl["wanUdpPorts"] = dic["wanudpports"]
        wsdl["lanIpStart"] = dic["lanipstart"]
        wsdl["lanIpEnd"] = dic["lanipend"]
        wsdl["lanPort"] = dic["lanport"]
        wsdl["slot"] = dic["slot"]
        wsdl["vfwName"] = dic["vfwname"]
        client = self.ws_client.get_client(url)
        try:
            ret = client.addDnat(**wsdl)
        except Exception:
            raise deviceError
        return ret

    def delete_dnat(self, context, dic):
        # delete dnat
        url = '/func/web_main/wsdl/nat/NatManager.wsdl'
        LOG.info("delete fw_DNat:" + url)
        wsdl = {}
        wsdl["name"] = dic["name"]
        wsdl["vfwName"] = dic["vfwname"]
        client = self.ws_client.get_client(url)
        try:
            ret = client.delDnat(**wsdl)
        except Exception:
            raise deviceError
        return ret

    def create_snat(self, context, dic):
        # create dnat
        url = '/func/web_main/wsdl/nat/NatManager.wsdl'
        LOG.info("create fw_snat:" + url)
        wsdl = {}
        wsdl["name"] = dic["name"]
        wsdl["outIfname"] = dic["outIfName"]
        wsdl["vfwName"] = dic["vfwname"]
        keys = dic.keys()
        if "srcipobjname" in keys:
            wsdl["srcIpObjName"] = dic["srcipobjname"]
        if "dstipobjname" in keys:
            wsdl["dstIpObjName"] = dic["dstipobjname"]
        if "wanippoolname" in keys:
            wsdl["wanIpPoolName"] = dic["wanippoolname"]
        client = self.ws_client.get_client(url)
        try:
            ret = client.addSnat(**wsdl)
        except Exception:
            raise deviceError
        return ret

    def delete_snat(self, context, dic):
        # delete dnat
        url = '/func/web_main/wsdl/nat/NatManager.wsdl'
        LOG.info("delete fw_snat:" + url)
        wsdl = {}
        wsdl["name"] = dic["name"]
        wsdl["vfwName"] = dic["vfwname"]
        client = self.ws_client.get_client(url)
        try:
            ret = client.delSnat(**wsdl)
        except Exception:
            raise deviceError
        return ret

    def get_dev_dnat(self, context, dnat_info_dict, agent_info_dict):
        # get dnat
        url = agent_info_dict['agent_ip']
        url += '/func/web_main/webservice/nat/nat'
        LOG.info("delete fw_DNat:" + url)
        trans_info_dict = {
            'name': '',
            "vfwName": ""
        }
        for key in trans_info_dict.keys():
            if key.lower() in dnat_info_dict.keys():
                trans_info_dict[key] = dnat_info_dict[key.lower()]
        client = self.ws_client.get_client(url)
        ret = client.getDnat(**dnat_info_dict)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def getall_dev_dnat(self, context, dnat_info_dict, agent_info_dict):
        # getall dnat
        url = agent_info_dict['agent_ip']
        url += '/func/web_main/webservice/nat/nat'
        LOG.info("delete fw_DNat:" + url)
        trans_info_dict = {
            "vfwName": ""
        }
        for key in trans_info_dict.keys():
            if key.lower() in dnat_info_dict.keys():
                trans_info_dict[key] = dnat_info_dict[key.lower()]
        client = self.ws_client.get_client(url)
        ret = client.getDnat_all(**dnat_info_dict)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def create_vfw(self, context, vfw):
        # create vfw
        wsdl = {}
        wsdl["name"] = vfw["name"]
        wsdl["type"] = vfw["type"]
        wsdl["resource"] = vfw["resource"]
        url = "/func/web_main/wsdl/vfw/vfw.wsdl"
        LOG.info(" create_vfw to webservice: " + url)
        client = self.ws_client.get_client(url)
        try:
            response = client.addNewVsys(**wsdl)
        except Exception:
            raise deviceError
        return response

    def delete_vfw(self, context, vfw):
        # delete
        url = "/func/web_main/wsdl/vfw/vfw.wsdl"
        LOG.info("delete fw_vfw:" + url)
        wsdl = {}
        wsdl["name"] = vfw["name"]
        client = self.ws_client.get_client(url)
        try:
            response = client.delVsys(**wsdl)
        except Exception:
            raise deviceError
        return response

    def get_dev_vfw(self, context, vfw_info_dict, agent_info_dict):
        # get vfw
        url = agent_info_dict['agent_ip']
        url += '/func/web_main/webservice/vfw/vfw'
        LOG.info("get fw_vfw:" + url)
        trans_info_dict = {
            'name': ''
        }
        for key in trans_info_dict.keys():
            if key.lower() in vfw_info_dict.keys():
                trans_info_dict[key] = vfw_info_dict[key.lower()]
        client = self.ws_client.get_client(url)
        ret = client.getVsys(**vfw_info_dict)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def getall_dev_vfw(self, context, vfw_info_dict, agent_info_dict):
        # getall vfw
        url = agent_info_dict['agent_ip']
        url += '/func/web_main/webservice/vfw/vfw'
        LOG.info("getall fw_vfw:" + url)
        trans_info_dict = {
            'name': ''
        }
        for key in trans_info_dict.keys():
            if key.lower() in vfw_info_dict.keys():
                trans_info_dict[key] = vfw_info_dict[key.lower()]
        client = self.ws_client.get_client(url)
        ret = client.getVsysAll(**vfw_info_dict)
        if ret == 0:
            return 0
        else:
            return 'soap fault'

    def add_snataddrpool(self, context, sap):
        # create snataddrpool
        url = "/func/web_main/wsdl/addrpool/addrpool.wsdl"
        client = self.ws_client.get_client(url)
        trans_dict = {
            "name": "",
            "ipStart": "",
            "ipEnd": "",
            "slotIp": "",
            "vfwName": ""
        }
        for key in trans_dict.keys():
            if key.lower() in sap.keys():
                trans_dict[key] = str(sap[key.lower()])
        response = client.addSnatAddrPool(**trans_dict)
        return response

    def del_snataddrpool(self, context, sap):
        # create snataddrpool
        url = "/func/web_main/wsdl/addrpool/addrpool.wsdl"
        client = self.ws_client.get_client(url)
        trans_dict = {
            "name": "",
            "vfwName": ""
        }
        for key in trans_dict.keys():
            if key.lower() in sap.keys():
                trans_dict[key] = str(sap[key.lower()])
        response = client.delSnatAddrPool(**trans_dict)
        return response
