from oslo_config import cfg
from oslo_serialization import jsonutils as json
from oslo_log import log as logging
from nca47 import objects
from nca47.common.i18n import _LW
from nca47.common.i18n import _LE
from nca47.manager import rpcapi
from nca47.manager import db_common
from nca47.api.controllers.v1 import tools
from nca47.common import exception
from nca47.manager.firewall_manager import protocol


CONF = cfg.CONF
LOG = logging.getLogger(__name__)

FIREWALL_MANAGER = None


class FirewallManager(object):

    """
    DNS operation handler class, using for handle client requests,
    validate parameters whether is legal,  handling DB operations and
    calling rpc client's corresponding method to send messaging to agent
    endpoints
    """

    def __init__(self):
        self.db_common = db_common.DBCommon.get_instance()
        self.rpc_api = rpcapi.FWManagerAPI.get_instance()
        self.proto_match = protocol.ProtoNet.get_instance()

    @classmethod
    def get_instance(cls):

        global FIREWALL_MANAGER
        if not FIREWALL_MANAGER:
            FIREWALL_MANAGER = cls()
        return FIREWALL_MANAGER

    # this is a vlan operation
    def create_vlan(self, context, dic):
        """
        create a vlan handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # operation veiw
        kw = self.db_common.merge_dict_view(dic)
        view = self.db_common.get_vres_agent_view(context, **kw)
        # tenant_id is or not exist
        if view is None:
            raise exception.IsNotExistError(param_name=dic['tenant_id'])
        vres_id = view["vres_id"]
        input_str = json.dumps(dic)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=input_str,
                                                          method='CREATE_VLAN',
                                                          status='FAILED')
        vlanid = '%s%s' % ('vlan_if', dic['vlan_id'])
        dic_vlan = {}
        dic_vlan["vlan_id"] = vlanid
        dic_vlan['deleted'] = False
        # query the vlan_id is or not exist
        # if the vlan_id is not existed,it raise exception
        vlan_query = objects.FwVlanInfo(context, **dic_vlan)
        val_valn = vlan_query.get_objects(context, **dic_vlan)
        if len(val_valn) != 0:
            raise exception.HaveSameObject(object_name=dic['vlan_id'])
        dic["vres_id"] = vres_id
        dic["vlan_id"] = vlanid
        vlan_obj = objects.FwVlanInfo(context, **dic)
        res = self.db_common.create_in_storage(context, vlan_obj)
        # response_fw = self.rpc_api.create_record(context, vlan_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return res

    def del_vlan(self, context, dic):
        """
        delete a vlan handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        kw = self.db_common.merge_dict_view(dic)
        view = self.db_common.get_vres_agent_view(context, **kw)
        # tenant_id is or not exist
        if view is None:
            raise exception.IsNotExistError(param_name=dic['tenant_id'])
        vres_id = view["vres_id"]
        input_str = json.dumps(dic)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=input_str,
                                                          method='DEL_VLAN',
                                                          status='FAILED')
        dic["vres_id"] = vres_id
        uuid = dic["id"]
        dic_vlan = {}
        dic_vlan["id"] = uuid
        dic_vlan['deleted'] = False
        # query the vlan is or not exist
        # if the vlan is not existed,it raise exception
        vlan_query = objects.FwVlanInfo(context, **dic_vlan)
        is_vlan = vlan_query.get_objects(context, **dic_vlan)
        if len(is_vlan) == 0:
            raise exception.IsNotExistError(param_name=uuid)
        remote_dic = dic["ifnames"]
        local_dic = is_vlan["ifnames"]
        val_ifnames = tools.get_complementary_set(remote_dic, local_dic)
        if val_ifnames is None:
            raise exception.ParamValueError(param_name=remote_dic)
        target_values = {}
        target_values["ifnames"] = val_ifnames

        vlan_obj = objects.FwVlanInfo(context, **target_values)
        response = vlan_obj.update(context, uuid, vlan_obj.as_dict())
        ifnames_len = len(response["ifnames"])
        if ifnames_len == 0:
            vlan_obj = objects.FwVlanInfo(context, **response)
            response = vlan_obj.delete(context, response["id"])
        # try:
        # response_fw = self.rpc_api.del_vlan(context, id_, vlan_infos)
        # except Exception as e:
        #    raise e
        self.db_common.update_operation_history(context, history.id,
                                                status='SUCCESS')
        return response

    def get_vlan(self, context, dic):
        """
        get a vlan handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        target_values = {}
        target_values["id"] = dic["id"]
        target_values['deleted'] = False
        target_values = dict(target_values)
        vlan_obj = objects.FwVlanInfo(context, **target_values)
        try:
            response = vlan_obj.get_object(context, **target_values)
        except Exception:
            LOG.warning(
                _LW("No vlan with id=%(id)s in DB"),
                {"id": target_values["id"]})
            raise exception.IsNotExistError(
                param_name="vlan with id=" + target_values['id'])
        return response

    def get_vlans(self, context, dic):
        """
        get all vlans handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        kw = self.db_common.merge_dict_view(dic)
        view = self.db_common.get_vres_agent_view(context, **kw)
        # tenant_id is or not exist
        if view is None:
            raise exception.IsNotExistError(param_name=dic['tenant_id'])
        vres_id = view["vres_id"]
        target_values = {}
        target_values["vres_id"] = vres_id
        target_values['deleted'] = False
        vlan_obj = objects.FwVlanInfo(context, **target_values)
        return vlan_obj.get_objects(context, **target_values)

    # this is a netservice operation
    def creat_netservice(self, context, dic):
        """
        create a netservice handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        kw = self.db_common.merge_dict_view(dic)
        view = self.db_common.get_vres_agent_view(context, **kw)
        # tenant_id is or not exist
        if view is None:
            raise exception.IsNotExistError(param_name=dic['tenant_id'])
        vres_id = view["vres_id"]
        input_str = json.dumps(dic)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=input_str,
                                                          method='ADD_NETSERV',
                                                          status='FAILED')
        # VFW is or not exist
        vfw = self.db_common.get_fw_vfw_id(context,
                                           vfw_name=dic["vfwname"],
                                           vres_id=vres_id)
        if vfw is None:
            raise exception.IsNotExistError(param_name=dic['vfwname'])
        vfw_id = vfw["id"]
        proto_name = self.proto_match.match_proto(dic['proto'])
        name = "%s%s" % (proto_name, dic['port'])
        target_values = {}
        target_values['vfw_id'] = vfw_id
        target_values['name'] = name
        target_values['deleted'] = False
        netserv_obj = objects.FwNetservicesInfo(context, **target_values)
        ner_serv = netserv_obj.get_objects(context, **target_values)
        if len(ner_serv) != 0:
            raise exception.HaveSameObject(object_name="%s,%s" % (dic['proto'],
                                                                  dic['port']))
        vfwname = vfw["vfw_name"]
        dic["name"] = name
        dic["vfw_id"] = vfw_id
        dic["vfwname"] = vfwname
        netserv_obj = objects.FwNetservicesInfo(context, **dic)
        res = netserv_obj.create(context, netserv_obj.as_dict())
        # response_fw = self.rpc_api.creat_netservice(context, netsev_infos)
        self.db_common.update_operation_history(context, history.id,
                                                status='SUCCESS')
        return res

    def del_netservice(self, context, dic):
        """
        delete a netservice handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        kw = self.db_common.merge_dict_view(dic)
        view = self.db_common.get_vres_agent_view(context, **kw)
        # tenant_id is or not exist
        if view is None:
            raise exception.IsNotExistError(param_name=dic['tenant_id'])
        vres_id = view["vres_id"]
        input_str = json.dumps(dic)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=input_str,
                                                          method='DEL_NETSERV',
                                                          status='FAILED')
        uuid = dic["id"]
        target_values = {}
        target_values['id'] = uuid
        target_values['deleted'] = False
        netserv_obj = objects.FwNetservicesInfo(context, **target_values)
        # query is or not net service by id
        is_netserv = netserv_obj.get_objects(context, **target_values)
        if len(is_netserv) == 0:
            raise exception.IsNotExistError(param_name=uuid)
        netserv_obj = objects.FwNetservicesInfo(context, **dic)
        response = netserv_obj.delete(context, uuid)
        # try:
        # response_fw = self.rpc_api.del_netservice(context, id_,
        #                                          netsev_infos)
        # except Exception as e:
        # raise e
        self.db_common.update_operation_history(context, history.id,
                                                status='SUCCESS')
        return response

    def get_netservice(self, context, netsev_infos):
        """
        get a netservice handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        target_values = {}
        target_values["id"] = netsev_infos["id"]
        target_values['deleted'] = False
        netserv_obj = objects.FwNetservicesInfo(context, **target_values)
        try:
            response = netserv_obj.get_object(context, **target_values)
        except Exception:
            LOG.warning(
                _LW("No netserivce with id=%(id)s in DB"),
                {"id": target_values["id"]})
            raise exception.IsNotExistError(
                param_name="netserivce with id=" + target_values['id'])
        return response

    def get_netservices(self, context, dic):
        """
        get all netservices handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        kw = self.db_common.merge_dict_view(dic)
        view = self.db_common.get_vres_agent_view(context, **kw)
        # tenant_id is or not exist
        if view is None:
            raise exception.IsNotExistError(param_name=dic['tenant_id'])
        vres_id = view["vres_id"]
        # get the colunm vfw_id(fw_vfw_info_id)
        vfw_dic = {}
        vfw_dic['vfw_name'] = dic['vfwname']
        vfw_dic['vres_id'] = vres_id
        vfw_info = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        target_values = {}
        target_values["vfw_id"] = vfw_info["id"]
        target_values['deleted'] = False
        netserv_obj = objects.FwNetservicesInfo(context, **target_values)
        return netserv_obj.get_objects(context, **target_values)

    # this is a addrobj operation
    def add_addrobj(self, context, addrobj_infos):
        """
        create addrobj handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # get the agent info
        vres_agent_dic = {}
        vres_agent_dic['agent_type'] = 'FW'
        vres_agent_dic['tenant_id'] = addrobj_infos['tenant_id']
        vres_agent_dic['network_zone'] = addrobj_infos['network_zone']
        vres_agent_dic['dc_name'] = addrobj_infos['dc_name']
        vres_agent_obj = self.db_common.get_vres_agent_view(context,
                                                            **vres_agent_dic)
        # insert operation history type with Creating in DB
        input_str = json.dumps(addrobj_infos)
        input_operation_history = {}
        input_operation_history['vres_id'] = vres_agent_obj.vres_id
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'CREATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
                        context, **input_operation_history)
        try:
            # get the value vfw_id(fw_vfw_info_id)
            vfw_dic = {}
            vfw_dic['vfw_name'] = addrobj_infos['vfwname']
            vfw_dic['vres_id'] = vres_agent_obj.vres_id
            rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        except Exception:
            LOG.warning(
                _LW("No addrobj with vres_id=%(vres_id)s in DB"),
                {"id": vres_agent_obj.vres_id})
            raise exception.IsNotExistError(
                param_name="vfw with vres_id=" + vres_agent_obj.vres_id)
        # init the DB operations object
        find_addrobj_dic = {}
        find_addrobj_dic['ip'] = addrobj_infos['ip']
        find_addrobj_dic['name'] = addrobj_infos['name']
        find_addrobj_dic['vfw_id'] = rstfwvfw.id
        find_addrobj = objects.FwAddrObjInfo(context, **find_addrobj_dic)
        # Check the addrobj which have same name if is exist in DB
        target_addrobj = self._valid_if_addrobj_exist(context, find_addrobj,
                                                      flag='addrobj')
        if target_addrobj is not None:
            LOG.warning(_LW("Have same zone id/name in DB"))
            raise exception.HaveSameObject(object_name=target_addrobj.name)
        # change the addrobj values with dic format
        target_values = {}
        target_values['vfwname'] = addrobj_infos['vfwname']
        target_values['vfw_id'] = rstfwvfw.id
        target_values['operation_fro'] = 'AUTO'
        merge_dict = tools.dict_merge(addrobj_infos, target_values)
        addrobj = objects.FwAddrObjInfo(context, **merge_dict)
        # create the addrobj info in db
        result = self.db_common.create_in_storage(context, addrobj)
        # response_fw = self.rpc_api.add_addrobj(context, addrobj_infos)
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
        return result

    def del_addrobj(self, context, addrobj_infos):
        """
        delete addrobj handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # get the agent info
        vres_agent_dic = {}
        vres_agent_dic['agent_type'] = 'FW'
        vres_agent_dic['tenant_id'] = addrobj_infos['tenant_id']
        vres_agent_dic['network_zone'] = addrobj_infos['network_zone']
        vres_agent_dic['dc_name'] = addrobj_infos['dc_name']
        vres_agent_obj = self.db_common.get_vres_agent_view(context,
                                                            **vres_agent_dic)
        # insert operation history type with Creating in DB
        input_str = json.dumps(addrobj_infos)
        input_operation_history = {}
        input_operation_history['vres_id'] = vres_agent_obj.vres_id
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
                        context, **input_operation_history)
        # delete the addrobj in db
        addrobj_infos = dict(addrobj_infos)
        addrobj = objects.FwAddrObjInfo(context, **addrobj_infos)
        result = addrobj.delete(context, addrobj_infos['id'])
        # response_fw = self.rpc_api.del_addrobj(context, addrobj_infos)
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
        return result

    def get_addrobj(self, context, addrobj_infos):
        """
        get one addrobj handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # get the one addrobj in db
        target_values = {}
        target_values['deleted'] = False
        merge_dict = tools.dict_merge(addrobj_infos, target_values)
        addrobj = objects.FwAddrObjInfo(context, **merge_dict)
        # try/catch the no one get
        try:
            result = addrobj.get_object(context, **merge_dict)
        except Exception:
            LOG.warning(
                _LW("No addrobj with id=%(id)s in DB"),
                {"id": merge_dict['id']})
            raise exception.IsNotExistError(
                param_name="addrobj with id=" + merge_dict['id'])
        return result

    def get_addrobjs(self, context, addrobj_infos):
        """
        get all addrobjs handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # get the agent info
        vres_agent_dic = {}
        vres_agent_dic['agent_type'] = 'FW'
        vres_agent_dic['tenant_id'] = addrobj_infos['tenant_id']
        vres_agent_dic['network_zone'] = addrobj_infos['network_zone']
        vres_agent_dic['dc_name'] = addrobj_infos['dc_name']
        vres_agent_obj = self.db_common.get_vres_agent_view(context,
                                                            **vres_agent_dic)
        try:
            # get the value vfw_id(fw_vfw_info_id)
            vfw_dic = {}
            vfw_dic['vfw_name'] = addrobj_infos['vfwname']
            vfw_dic['vres_id'] = vres_agent_obj.vres_id
            rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        except Exception:
            LOG.warning(
                _LW("No addrobj with vres_id=%(vres_id)s in DB"),
                {"id": vres_agent_obj.vres_id})
            raise exception.IsNotExistError(
                param_name="vfw with vres_id=" + vres_agent_obj.vres_id)
        # get the one addrobj in db
        target_values = {}
        target_values['vfw_id'] = rstfwvfw.id
        target_values['vfwname'] = addrobj_infos['vfwname']
        target_values['deleted'] = False
        addrobj = objects.FwAddrObjInfo(context, **target_values)
        # try/catch the no one get
        try:
            result = addrobj.get_objects(context, **target_values)
        except Exception:
            LOG.warning(_LW("No addrobj with vfw_id=%(vfw_id)s in DB"), {
                        "vfw_id": target_values['vfw_id']})
            raise exception.IsNotExistError(
                param_name="addrobj with vfw_id=" + target_values['vfw_id'])
        return result

    # this is a snataddrpool operation
    def add_snataddrpool(self, context, snataddrpool_infos):
        """
        create addrobj handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # get the agent info
        vres_agent_dic = {}
        vres_agent_dic['agent_type'] = 'FW'
        vres_agent_dic['tenant_id'] = snataddrpool_infos['tenant_id']
        vres_agent_dic['network_zone'] = snataddrpool_infos['network_zone']
        vres_agent_dic['dc_name'] = snataddrpool_infos['dc_name']
        vres_agent_obj = self.db_common.get_vres_agent_view(context,
                                                            **vres_agent_dic)
        # insert operation history type with Creating in DB
        input_str = json.dumps(snataddrpool_infos)
        input_operation_history = {}
        input_operation_history['vres_id'] = vres_agent_obj.vres_id
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'CREATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
                       context, **input_operation_history)
        try:
            # get the colunm vfw_id(fw_vfw_info_id)
            vfw_dic = {}
            vfw_dic['vfw_name'] = snataddrpool_infos['vfwname']
            vfw_dic['vres_id'] = vres_agent_obj.vres_id
            rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        except Exception:
            LOG.warning(
                _LW("No addrobj with vres_id=%(vres_id)s in DB"),
                {"id": vres_agent_obj.vres_id})
            raise exception.IsNotExistError(
                param_name="vfw with vres_id=" + vres_agent_obj.vres_id)
        # init the DB operations object
        find_addrobj_dic = {}
        find_addrobj_dic['name'] = snataddrpool_infos['name']
        find_addrobj_dic['vfw_id'] = rstfwvfw.id
        find_snataddrpool = objects.FwSnatAddrPoolInfo(context,
                                                       **find_addrobj_dic)
        # Check the addrobj which have same name if is exist in DB
        target_addrobj = self._valid_if_addrobj_exist(context,
                                                      find_snataddrpool,
                                                      flag='snataddrpool')
        if target_addrobj is not None:
            LOG.warning(_LW("Have same zone id/name in DB"))
            raise exception.HaveSameObject(object_name=target_addrobj.name)
        # change the snataddrpool values with dic format
        target_values = {}
        target_values['vfwname'] = snataddrpool_infos['vfwname']
        target_values['vfw_id'] = rstfwvfw.id
        target_values['operation_fro'] = 'AUTO'
        merge_dict = tools.dict_merge(snataddrpool_infos, target_values)
        snataddrpool = objects.FwSnatAddrPoolInfo(context, **merge_dict)
        # create the snataddrpool info in db
        result = self.db_common.create_in_storage(context, snataddrpool)
        # response_fw = self.rpc_api.add_snataddrpool(context,
        # snataddrpool_infos)
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
        return result

    def del_snataddrpool(self, context, snataddrpool_infos):
        """
        delete snataddrpool handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # get the agent info
        vres_agent_dic = {}
        vres_agent_dic['agent_type'] = 'FW'
        vres_agent_dic['tenant_id'] = snataddrpool_infos['tenant_id']
        vres_agent_dic['network_zone'] = snataddrpool_infos['network_zone']
        vres_agent_dic['dc_name'] = snataddrpool_infos['dc_name']
        vres_agent_obj = self.db_common.get_vres_agent_view(context,
                                                            **vres_agent_dic)
        # insert operation history type with Creating in DB
        input_str = json.dumps(snataddrpool_infos)
        input_operation_history = {}
        input_operation_history['vres_id'] = vres_agent_obj.vres_id
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
                        context, **input_operation_history)
        # delete the snataddrpool in db
        snataddrpool_infos = dict(snataddrpool_infos)
        snataddrpool = objects.FwSnatAddrPoolInfo(context,
                                                  **snataddrpool_infos)
        result = snataddrpool.delete(context, snataddrpool_infos['id'])
        # response_fw = self.rpc_api.del_snataddrpool(context,
        # snataddrpool_infos)
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
        return result

    def get_snataddrpool(self, context, snataddrpool_infos):
        """
        get one snataddrpool handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # get the one snataddrpool in db
        target_values = {}
        target_values['deleted'] = False
        merge_dict = tools.dict_merge(snataddrpool_infos, target_values)
        snataddrpool = objects.FwSnatAddrPoolInfo(context, **merge_dict)
        # try/catch the no one get
        try:
            result = snataddrpool.get_object(context, **merge_dict)
        except Exception:
            LOG.warning(
                _LW("No snataddrpool with id=%(id)s in DB"),
                {"id": merge_dict['id']})
            raise exception.IsNotExistError(
                param_name="snataddrpool with id=" + merge_dict['id'])
        return result

    def get_snataddrpools(self, context, snataddrpool_infos):
        """
        get all snataddrpools handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # get the agent info
        vres_agent_dic = {}
        vres_agent_dic['agent_type'] = 'FW'
        vres_agent_dic['tenant_id'] = snataddrpool_infos['tenant_id']
        vres_agent_dic['network_zone'] = snataddrpool_infos['network_zone']
        vres_agent_dic['dc_name'] = snataddrpool_infos['dc_name']
        vres_agent_obj = self.db_common.get_vres_agent_view(context,
                                                            **vres_agent_dic)
        try:
            # get the colunm vfw_id(fw_vfw_info_id)
            vfw_dic = {}
            vfw_dic['vfw_name'] = snataddrpool_infos['vfwname']
            vfw_dic['vres_id'] = vres_agent_obj.vres_id
            rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        except Exception:
            LOG.warning(
                _LW("No addrobj with vres_id=%(vres_id)s in DB"),
                {"id": vres_agent_obj.vres_id})
            raise exception.IsNotExistError(
                param_name="vfw with vres_id=" + vres_agent_obj.vres_id)
        # get the one snataddrpool in db
        target_values = {}
        target_values['vfwname'] = snataddrpool_infos['vfwname']
        target_values['vfw_id'] = rstfwvfw.id
        target_values['deleted'] = False
        snataddrpool = objects.FwSnatAddrPoolInfo(context, **target_values)
        # try/catch the no one get
        try:
            result = snataddrpool.get_objects(context, **target_values)
        except Exception:
            LOG.warning(_LW("No snataddrpool with vfw_id=%(vfw_id)s in DB"), {
                        "vfw_id": target_values['vfw_id']})
            raise exception.IsNotExistError(
                param_name="snataddrpool vfw_id=" + target_values['vfw_id'])
        return result

    def _valid_if_addrobj_exist(self, context, qry_db_obj, flag):
        """Check the addrobj which have same name if is exist in DB"""
        qry_db_obj_dic = {}
        if flag == 'addrobj':
            qry_db_obj_dic['ip'] = qry_db_obj.ip
        qry_db_obj_dic['name'] = qry_db_obj.name
        qry_db_obj_dic['vfw_id'] = qry_db_obj.vfw_id
        qry_db_obj_dic['deleted'] = False
        rst_qry_db_obj = None
        try:
            # get the addrobj in db
            rst_qry_db_obj = qry_db_obj.get_object(context, **qry_db_obj_dic)
        except Exception:
            pass
        return rst_qry_db_obj

    def create_vfw(self, context, vfw):
        target_vfw = self._make_vfw_object(vfw)
        tenant_id = vfw['tenant_id']
        net_zone = vfw['network_zone']
        dc_name = vfw['dc_name']
        view_obj = self.db_common.get_vres_agent_view(context,
                                                      tenant_id=tenant_id,
                                                      agent_type='FW',
                                                      network_zone=net_zone,
                                                      dc_name=dc_name)
        vres_id = view_obj['vres_id']
        target_vfw['vres_id'] = vres_id
        vfw_obj = objects.VFW(context, **target_vfw)
        # insert operation history
        vfw_str = json.dumps(vfw)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=vfw_str,
                                                          method='CREATE',
                                                          status='FAILED')
        check_vfw_dic = {}
        check_vfw_dic['vfw_name'] = target_vfw['vfw_name']
        check_vfw_dic['vres_id'] = vres_id
        check_vfw_obj = objects.VFW(context, **check_vfw_dic)
        if self.db_common.is_exist_object(context, check_vfw_obj):
            raise exception.HaveSameObject(object_name=check_vfw_obj.vfw_name)
        response_vfw = self.db_common.create_in_storage(context, vfw_obj)

        # todo list - rpc call
        self.db_common.update_operation_history(context, history.id,
                                                status='SUCCESS')
        return response_vfw

    def delete_vfw(self, context, vfw):
        tenant_id = vfw['tenant_id']
        net_zone = vfw['network_zone']
        dc_name = vfw['dc_name']
        view_obj = self.db_common.get_vres_agent_view(context,
                                                      tenant_id=tenant_id,
                                                      agent_type='FW',
                                                      network_zone=net_zone,
                                                      dc_name=dc_name)
        vres_id = view_obj['vres_id']
        vfw_str = json.dumps(vfw)
        vfw_obj = objects.VFW(context, **vfw)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=vfw_str,
                                                          method='DELETE',
                                                          status='FAILED')
        vfw_dic = {}
        vfw_dic['id'] = vfw['id']
        vfw_dic['deleted'] = False
        try:
            vfw_obj.get_object(context, **vfw_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="vfw with id=" +
                                            vfw_dic['id'])
        response_vfw = vfw_obj.delete(context, vfw['id'])
        # todo list - rpc call
        self.db_common.update_operation_history(context, history.id,
                                                status='SUCCESS')
        return response_vfw

    def get_vfw(self, context, vfw):
        vfw_dic = {}
        vfw_dic['id'] = vfw['id']
        vfw_dic['deleted'] = False
        vfw_obj = objects.VFW(context)
        try:
            response_vfw = vfw_obj.get_object(context, **vfw_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="vfw with id=" +
                                            vfw_dic['id'])
        return response_vfw

    def get_all_vfws(self, context, vfw):
        vfw_obj = objects.VFW(context)
        vfw_dic = {}
        vfw_dic['network_zone_name'] = vfw['network_zone']
        vfw_dic['dc_name'] = vfw['dc_name']
        vfw_dic['deleted'] = False
        response_vfw = vfw_obj.get_objects(context, **vfw_dic)
        return response_vfw

    def _make_vfw_object(self, values):
        target_values = {}
        for k in values.keys():
            if k == 'name':
                target_values['vfw_name'] = values[k]
            elif k == 'type':
                target_values['vfw_type'] = values[k]
            elif k == 'resource':
                target_values['vfw_info'] = values[k]
            elif k == 'network_zone':
                target_values['network_zone_name'] = values[k]
            else:
                target_values[k] = values[k]
        return target_values

    def create_dnat(self, context, dnat):
        tenant_id = dnat['tenant_id']
        net_zone = dnat['network_zone']
        dc_name = dnat['dc_name']
        view_obj = self.db_common.get_vres_agent_view(context,
                                                      tenant_id=tenant_id,
                                                      agent_type='FW',
                                                      network_zone=net_zone,
                                                      dc_name=dc_name)
        vres_id = view_obj['vres_id']

        # get the colunm vfw_id(fw_vfw_info_id)
        vfw_dic = {}
        vfw_dic['vfw_name'] = dnat['vfwname']
        vfw_dic['vres_id'] = vres_id
        rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        target_values = {}
        target_values['vfw_id'] = rstfwvfw.id
        merge_dict = tools.dict_merge(dnat, target_values)
        dnat_obj = objects.Dnat(context, **merge_dict)
        # insert operation history
        dnat_str = json.dumps(dnat)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=dnat_str,
                                                          method='CREATE',
                                                          status='FAILED')
        check_dnat_dic = {}
        check_dnat_dic['vfw_id'] = rstfwvfw.id
        check_dnat_dic['name'] = dnat['name']
        check_dnat_obj = objects.Dnat(context, **check_dnat_dic)
        if self.db_common.is_exist_object(context, check_dnat_obj):
            raise exception.HaveSameObject(object_name=check_dnat_obj.name)
        response_dnat = self.db_common.create_in_storage(context, dnat_obj)

        # todo list - rpc call
        self.db_common.update_operation_history(context, history.id,
                                                status='SUCCESS')
        return response_dnat

    def delete_dnat(self, context, dnat):
        dnat_obj = objects.Dnat(context)
        dnat_dic = {}
        dnat_dic['id'] = dnat['id']
        dnat_dic['deleted'] = False
        try:
            dnat_obj.get_object(context, **dnat_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="dnat with id=" +
                                            dnat_dic['id'])
        dnat_info = dnat_obj.delete(context, dnat['id'])

        return dnat_info

    def get_dnat(self, context, dnat):
        dnat_dic = {}
        dnat_dic['id'] = dnat['id']
        dnat_dic['deleted'] = False
        dnat_obj = objects.Dnat(context)
        try:
            dnat_info = dnat_obj.get_object(context, **dnat_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="dnat with id=" +
                                            dnat_dic['id'])
        return dnat_info

    def get_all_dnats(self, context, dnat):
        tenant_id = dnat['tenant_id']
        net_zone = dnat['network_zone']
        dc_name = dnat['dc_name']
        view_obj = self.db_common.get_vres_agent_view(context,
                                                      tenant_id=tenant_id,
                                                      agent_type='FW',
                                                      network_zone=net_zone,
                                                      dc_name=dc_name)
        vres_id = view_obj['vres_id']
        # get the colunm vfw_id(fw_vfw_info_id)
        vfw_dic = {}
        vfw_dic['vfw_name'] = dnat['vfwname']
        vfw_dic['vres_id'] = vres_id
        rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        dnat_dic = {}
        dnat_dic['vfw_id'] = rstfwvfw.id
        dnat_dic['deleted'] = False
        dnat_obj = objects.Dnat(context)
        response_dnat = dnat_obj.get_objects(context, **dnat_dic)
        return response_dnat

    def _make_dnat_object(self, values):
        """
        From client request, the parameters in lowercase by unify,
        in order to operation on target device, we must convert these
        parameters into device can know parameters
        """
        target_values = {}
        for k in values.keys():
            if k == 'inifname':
                target_values['inIfName'] = values[k]
            elif k == 'wanip':
                target_values['wanIp'] = values[k]
            elif k == 'wantcpports':
                target_values['wanTcpPorts'] = values[k]
            elif k == 'wanudpports':
                target_values['wanUdpPorts'] = values[k]
            elif k == 'lanipstart':
                target_values['lanIpStart'] = values[k]
            elif k == 'lanipend':
                target_values['lanIpEnd'] = values[k]
            elif k == 'lanport':
                target_values['lanport'] = values[k]
            elif k == 'vfwname':
                target_values['vfwName'] = values[k]
            else:
                target_values[k] = values[k]
        return target_values

    def create_packetfilter(self, context, packetfilter):
        tenant_id = packetfilter['tenant_id']
        net_zone = packetfilter['network_zone']
        dc_name = packetfilter['dc_name']
        view_obj = self.db_common.get_vres_agent_view(context,
                                                      tenant_id=tenant_id,
                                                      agent_type='FW',
                                                      network_zone=net_zone,
                                                      dc_name=dc_name)
        vres_id = view_obj['vres_id']
        # get the colunm vfw_id(fw_vfw_info_id)
        vfw_dic = {}
        vfw_dic['vfw_name'] = packetfilter['vfwname']
        vfw_dic['vres_id'] = vres_id
        rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        # insert operation history
        pf_str = json.dumps(packetfilter)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=pf_str,
                                                          method='CREATE',
                                                          status='FAILED')
        # Check src/dst address object base on address object ip info
        srcIpObjNames = []
        dstIpObjNames = []
        if 'srcipobjips' in packetfilter.keys():
            srcIps = packetfilter['srcipobjips']
            for ip in srcIps:
                name = self._get_addrObjName(context, rstfwvfw.id, ip)
                srcIpObjNames.append(name)
        if 'dstipobjips' in packetfilter.keys():
            srcIps = packetfilter['dstipobjips']
            dstIpObjNames = []
            for ip in srcIps:
                name = self._get_addrObjName(context, rstfwvfw.id, ip)
                dstIpObjNames.append(name)
        target_values = {}
        target_values['vfw_id'] = rstfwvfw.id
        # if srcIpObjNames/dstIpObjNames is [], it's mean 'no ip limit'
        target_values['srcipobjnames'] = srcIpObjNames
        target_values['dstipobjnames'] = dstIpObjNames
        merge_dict = tools.dict_merge(packetfilter, target_values)
        packetfilter_obj = objects.PacketFilter(context, **merge_dict)

        check_packetfilter_dic = {}
        check_packetfilter_dic['name'] = packetfilter['name']
        check_packetfilter_dic['vfw_id'] = rstfwvfw.id
        checkpacketfilter = objects.PacketFilter(context,
                                                 **check_packetfilter_dic)
        if self.db_common.is_exist_object(context, checkpacketfilter):
            raise exception.HaveSameObject(object_name=checkpacketfilter.name)
        response = self.db_common.create_in_storage(context, packetfilter_obj)

        # todo list - rpc call
        self.db_common.update_operation_history(context, history.id,
                                                status='SUCCESS')
        return response

    def delete_packetfilter(self, context, packetfilter):
        tenant_id = packetfilter['tenant_id']
        net_zone = packetfilter['network_zone']
        dc_name = packetfilter['dc_name']
        view_obj = self.db_common.get_vres_agent_view(context,
                                                      tenant_id=tenant_id,
                                                      agent_type='FW',
                                                      network_zone=net_zone,
                                                      dc_name=dc_name)
        vres_id = view_obj['vres_id']
        input_str = json.dumps(packetfilter)
        packetfilter_obj = objects.PacketFilter(context)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=input_str,
                                                          method='DELETE',
                                                          status='FAILED')
        packetfilter_dic = {}
        packetfilter_dic['id'] = packetfilter['id']
        packetfilter_dic['deleted'] = False
        try:
            packetfilter_obj.get_object(context, **packetfilter_dic)
        except Exception:
            LOG.error(
                _LE("No target packetfilter with id=%s" % packetfilter['id']))
            raise exception.IsNotExistError(param_name="packetfilter"
                                            " with id=" + packetfilter['id'])
        response = packetfilter_obj.delete(context, packetfilter['id'])
        # todo list - rpc call
        self.db_common.update_operation_history(context, history.id,
                                                status='SUCCESS')
        return response

    def get_packetfilter(self, context, packetfilter):
        packetfilter_obj = objects.PacketFilter(context)
        packetfilter_dic = {}
        packetfilter_dic['id'] = packetfilter['id']
        packetfilter_dic['deleted'] = False
        try:
            response = packetfilter_obj.get_object(context, **packetfilter_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="packetfilter"
                                            " with id=" + packetfilter['id'])
        return response

    def get_all_packetfilters(self, context, packetfilter):
        tenant_id = packetfilter['tenant_id']
        net_zone = packetfilter['network_zone']
        dc_name = packetfilter['dc_name']
        view_obj = self.db_common.get_vres_agent_view(context,
                                                      tenant_id=tenant_id,
                                                      agent_type='FW',
                                                      network_zone=net_zone,
                                                      dc_name=dc_name)
        vres_id = view_obj['vres_id']
        # get the colunm vfw_id(fw_vfw_info_id)
        vfw_dic = {}
        vfw_dic['vfw_name'] = packetfilter['vfwname']
        vfw_dic['vres_id'] = vres_id
        rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        packetfilter_dic = {}
        packetfilter_dic['vfw_id'] = rstfwvfw.id
        packetfilter_dic['deleted'] = False
        packetfilter_obj = objects.PacketFilter(context)
        packetfilters = packetfilter_obj.get_objects(context,
                                                     **packetfilter_dic)

        return packetfilters

    def _make_packetfilter_object(self, values):
        """
        From client request, the parameters in lowercase by unify,
        in order to operation on target device, we must convert these
        parameters into the parameters which device can know
        """
        target_values = {}
        for k in values.keys():
            if k == 'srczonename':
                target_values['srcZoneName'] = values[k]
            elif k == 'dstzonename':
                target_values['dstZoneName'] = values[k]
            elif k == 'srcipobjnames':
                target_values['srcIpObjNames'] = values[k]
            elif k == 'dstipobjnames':
                target_values['dstIpObjNames'] = values[k]
            elif k == 'servicenames':
                target_values['serviceNames'] = values[k]
            elif k == 'vfwname':
                target_values['vfwName'] = values[k]
            else:
                target_values[k] = values[k]
        return target_values

    def _get_addrObjName(self, context, vfwId, addrObjIp):
        """
        Use for get address object name by the address object's
        corresponding IP info and related vfw info
        """
        target_addrObj = objects.FwAddrObjInfo(context)
        addr_obj_dic = {}
        addr_obj_dic['vfw_id'] = vfwId
        addr_obj_dic['ip'] = addrObjIp
        addr_obj_dic['deleted'] = False
        try:
            addrObjInfo = target_addrObj.get_object(context, **addr_obj_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="addrObjInfo"
                                            " with ip=" + addr_obj_dic['ip'] +
                                            "and vfw_id=" +
                                            addr_obj_dic['vfw_id'])
        return addrObjInfo.name

    # this is a vrf operation
    def create_vrf(self, context, fw_object):
        """
        create vrf handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_object)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'CREATE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # input the vrf value with dic format
        fw_object['vres_id'] = revs_agent.vres_id
        fw_object['operation_fro'] = 'AUTO'
        fw_obj = objects.FW_Vrf_Object(context, **fw_object)
        # create the vrf info in db
        result = self.db_common.create_in_storage(context, fw_obj)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return result

    def del_vrf(self, context, fw_object):
        """
        del vrf handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_object)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'DELETE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # del the vrf values with dic format
        fw_obj = objects.FW_Vrf_Object(context, **fw_object)
        # del the vrf info in db
        result = fw_obj.delete(context, fw_object["id"])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return result

    def get_vrf(self, context, fw_object):
        """
        get vrf handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        # get the vrf values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values["id"] = fw_object["id"]
        target_values['vres_id'] = revs_agent.vres_id

#         merge_dict = tools.dict_merge(fw_object, target_values)
        fw_obj = objects.FW_Vrf_Object(context, **target_values)
        # get the vrf info in db

        try:
            result = fw_obj.get_object(context, **target_values)
        except Exception:
            raise exception.IsNotExistError(param_name="vrf with id=" +
                                            target_values['id'])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result

    def get_vrfs(self, context, fw_object):
        """
        get_all vrf handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        # get the vrf values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values['vres_id'] = revs_agent.vres_id

#         merge_dict = tools.dict_merge(fw_object, target_values)
        fw_obj = objects.FW_Vrf_Object(context, **target_values)
        # get the vrf info in db

        result = fw_obj.get_objects(context, **target_values)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result

    # this is a snat operation
    def create_snat(self, context, fw_object):
        """
        create snat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_object)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'CREATE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # get the value vfw_id(fw_vfw_info_id)
        rstfwvfw = self.db_common.get_fw_vfw_id(context,
                                                vfw_name=fw_object['vfwname'],
                                                vres_id=revs_agent.vres_id,
                                                )
        # IP address is converted to an address object
        vfw_id = rstfwvfw.id
        srcipobjname = fw_object['srcipobjname']
        dstipobjname = fw_object['dstipobjname']
        srcipobjname_new = []
        dstipobjname_new = []
        addrobj = {}
        addrobj["vfw_id"] = vfw_id
        if len(srcipobjname) == 0:
            srcipobjname_new.append("all")
        elif len(srcipobjname) == 1:
            if (srcipobjname[0] is not "all"):
                addrobj["ip"] = srcipobjname[0]
                ipName = self.db_common.get_addrobj_name(context, **addrobj)
                srcipobjname_new.append(ipName)
            else:
                srcipobjname_new.append("all")
        else:
            for key in srcipobjname:
                addrobj["ip"] = key
                ipName = self.db_common.get_addrobj_name(context, **addrobj)
                srcipobjname_new.append(ipName)

        if len(dstipobjname) == 0:
            dstipobjname_new.append("all")
        elif len(dstipobjname) == 1:
            if (dstipobjname[0] is not "all"):
                addrobj["ip"] = dstipobjname[0]
                ipName = self.db_common.get_addrobj_name(context, **addrobj)
                dstipobjname_new.append(ipName)
            else:
                dstipobjname_new.append("all")
        else:
            for key in dstipobjname:
                addrobj["ip"] = key
                ipName = self.db_common.get_addrobj_name(context, **addrobj)
                dstipobjname_new.append(ipName)
        fw_object['srcipobjname'] = srcipobjname_new
        fw_object['dstipobjname'] = dstipobjname_new
        # input the snat values with dic format
#         fw_object['vfwname'] = revs_agent.tenant_id
        fw_object['vfw_id'] = vfw_id
        fw_object['operation_fro'] = 'AUTO'
        fw_obj = objects.FW_Snat_Object(context, **fw_object)
        # create the snat info in db
        result = self.db_common.create_in_storage(context, fw_obj)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return result

    def del_snat(self, context, fw_object):
        """
        del snat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_object)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'DELETE'
        vargs_history['status'] = 'FAILED'

        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # del the snat values with dic format
        fw_obj = objects.FW_Snat_Object(context, **fw_object)
        # del the snat info in db
        result = fw_obj.delete(context, fw_object["id"])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return result

    def get_snat(self, context, fw_object):
        """
        get snat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        # get the staticnat values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values["id"] = fw_object["id"]

#         merge_dict = tools.dict_merge(fw_object, target_values)
        fw_obj = objects.FW_Snat_Object(context, **target_values)
        # get the staticnat info in db
        try:
            result = fw_obj.get_object(context, **target_values)
        except Exception:
            raise exception.IsNotExistError(param_name="snat with id=" +
                                            target_values['id'])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result

    def get_snats(self, context, fw_object):
        """
        get snat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        # get the value vfw_id(fw_vfw_info_id)
        rstfwvfw = self.db_common.get_fw_vfw_id(context,
                                                vfw_name=fw_object['vfwname'],
                                                vres_id=revs_agent.vres_id,
                                                )

        # get_all the snat values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values['vfw_id'] = rstfwvfw.id
#         merge_dict = tools.dict_merge(fw_object, target_values)
        fw_obj = objects.FW_Snat_Object(context, **target_values)
        # del the staticnat info in db

        result = fw_obj.get_objects(context, **target_values)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result

    # this is a snat operation
    def create_securityZone(self, context, fw_object):
        """
        create securityZone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_object)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'CREATE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # get the value vfw_id(fw_vfw_info_id)
        # get the value vfw_id(fw_vfw_info_id)
        rstfwvfw = self.db_common.get_fw_vfw_id(context,
                                                vfw_name=fw_object['vfwname'],
                                                vres_id=revs_agent.vres_id,
                                                )
        # input the securityZone values with dic format
#         fw_object['vfwname'] = revs_agent.tenant_id
        fw_object['vfw_id'] = rstfwvfw.id
        fw_object['operation_fro'] = 'AUTO'
        fw_obj = objects.FW_SecurityZone_Object(context, **fw_object)
        # create the securityZone info in db
        result = self.db_common.create_in_storage(context, fw_obj)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return result

    def update_securityZone(self, context, fw_object):
        """
        update securityZone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_object)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'UPDATE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # input the staticnat values with dic format
        fw_obj = objects.FW_SecurityZone_Object(context, **fw_object)
        # create the staticnat info in db
        result = fw_obj.update(context, fw_object['id'], fw_object)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return result

    def del_securityZone(self, context, fw_object):
        """
        del securityZone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_object)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'UPDATE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # del the securityZone values with dic format
        fw_obj = objects.FW_SecurityZone_Object(context, **fw_object)
        # del the securityZone info in db
        result = fw_obj.delete(context, fw_object["id"])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return result

    def get_securityZone(self, context, fw_object):
        """
        get_all securityZone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        # get_all the securityZone values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values["id"] = fw_object["id"]
#         merge_dict = tools.dict_merge(fw_object, target_values)
        fw_obj = objects.FW_SecurityZone_Object(context, **target_values)
        # get_all the securityZone info in db
        try:
            result = fw_obj.get_object(context, **target_values)
        except Exception:
            raise exception.IsNotExistError(
                    param_name="securityZone with id=" + target_values['id'])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result

    def get_securityZones(self, context, fw_object):
        """
        get_all securityZone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        # get the value vfw_id(fw_vfw_info_id)
        rstfwvfw = self.db_common.get_fw_vfw_id(context,
                                                vfw_name=fw_object['vfwname'],
                                                vres_id=revs_agent.vres_id,
                                                )

        # get_all the securityZone values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values['vfw_id'] = rstfwvfw.id
#         merge_dict = tools.dict_merge(fw_object, target_values)
        fw_obj = objects.FW_SecurityZone_Object(context, **target_values)
        # get_all the securityZone info in db

        result = fw_obj.get_objects(context, **target_values)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result

    # this is a staticnat operation
    def create_staticnat(self, context, fw_object):
        """
        create staticnat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_object)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'CREATE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # get the value vfw_id(fw_vfw_info_id)
        varValu = {}
        varValu['vfw_name'] = fw_object['vfwname']
        varValu['vres_id'] = revs_agent.vres_id
        rstfwvfw = self.db_common.get_fw_vfw_id(context, **varValu)
        # input the staticnat values with dic format
#         fw_object['vfwname'] = fw_object['vfwname']
        fw_object['vfw_id'] = rstfwvfw.id
        fw_object['operation_fro'] = 'AUTO'
        fw_obj = objects.FW_Staticnat_Object(context, **fw_object)
        # create the staticnat info in db
        result = self.db_common.create_in_storage(context, fw_obj)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return result

    def del_staticnat(self, context, fw_object):
        """
        del staticnat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_object)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'DELETE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # del the staticnat values with dic format
        fw_obj = objects.FW_Staticnat_Object(context, **fw_object)
        # del the staticnat info in db
        result = fw_obj.delete(context, fw_object["id"])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return result

    def get_staticnat(self, context, fw_object):
        """
        get staticnat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        # get the staticnat values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values["id"] = fw_object["id"]

#         merge_dict = tools.dict_merge(fw_object, target_values)
        fw_obj = objects.FW_Staticnat_Object(context, **target_values)
        # get the staticnat info in db

        try:
            result = fw_obj.get_object(context, **target_values)
        except Exception:
            raise exception.IsNotExistError(param_name="Staticnat with id=" +
                                            target_values['id'])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result

    def get_staticnats(self, context, fw_object):
        """
        get staticnat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_object['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_object['network_zone']
        vargs['dc_name'] = fw_object['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        # get the value vfw_id(fw_vfw_info_id)
        rstfwvfw = self.db_common.get_fw_vfw_id(context,
                                                vfw_name=fw_object['vfwname'],
                                                vres_id=revs_agent.vres_id,
                                                )

        # del the staticnat values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values['vfw_id'] = rstfwvfw.id
#         merge_dict = tools.dict_merge(fw_object, target_values)
        fw_obj = objects.FW_Staticnat_Object(context, **target_values)
        # del the staticnat info in db

        result = fw_obj.get_objects(context, **target_values)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result
