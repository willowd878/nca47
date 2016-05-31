from oslo_config import cfg
from oslo_serialization import jsonutils as json
from oslo_log import log as logging
from nca47 import objects
from nca47.common.i18n import _LW
from nca47.common.i18n import _LE
from nca47.common.i18n import _LI
from nca47.manager import rpcapi
from nca47.manager import db_common
from nca47.api.controllers.v1 import tools
from nca47.common import exception
from nca47.manager.firewall_manager import protocol
from nca47.common.exception import NonExistParam
from nca47.common.exception import IsNotExistError
from copy import deepcopy

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

FIREWALL_MANAGER = None


class FirewallManager(object):
    """
    Firewall operation handler class, using for handle client requests,
    validate parameters whether is legal,  handling DB operations and
    calling rpc client's corresponding method to send messaging to agent
    endpoints
    """

    def __init__(self):
        self.db_common = db_common.DBCommon.get_instance()
        self.rpc_api = rpcapi.FWManagerAPI.get_instance()

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
        dic['agent_type'] = 'FW'
        kw = self.db_common.merge_dict_view(dic)
        view = self.db_common.get_vres_agent_view(context, **kw)
        vres_id = view["vres_id"]
        input_str = json.dumps(dic)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=input_str,
                                                          method='CREATE_VLAN',
                                                          status='FAILED')
        dic['vres_id'] = vres_id
        # dic["vlan_id_o"] = dic['vlan_id']
        vlan_name = '%s%s' % ('vlan_if', dic['vlan_number'])
        dic["vlan_name"] = vlan_name
        dic_vlan = {}
        dic_vlan["vlan_number"] = dic['vlan_number']
        dic_vlan['vlan_name'] = dic['vlan_name']
        dic_vlan['deleted'] = False
        dic_vlan['vres_id'] = vres_id
        vlan_obj = objects.FwVlanInfo(context, **dic)
        vlan_query = objects.FwVlanInfo(context, **dic_vlan)
        is_exist = False
        try:
            val_vlan = dict(vlan_query.get_object(context, **dic_vlan))
        except:
            res = self.db_common.create_in_storage(context, vlan_obj)
        else:
            is_exist = True
            for ifname in val_vlan['ifnames']:
                if ifname not in dic['ifnames']:
                    dic['ifnames'].append(ifname)
            res = vlan_query.update(context, val_vlan['id'], dic)
        self.rpc_api.reload_topic(view['agent_ip'])
        try:
            self.rpc_api.create_vlan(context, dic)
        except Exception as e:
            if is_exist:
                vlan_query.update(context, res.id,
                                  val_vlan)
            else:
                vlan_obj.delete(context, res.id)
            raise e
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return res

    def del_vlan(self, context, dic):
        """
        delete a vlan handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """

        org_obj = objects.FwVlanInfo(context, **dic)
        dic['agent_type'] = 'FW'
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
        vlan_query = objects.FwVlanInfo(context, **dic_vlan)
        try:
            is_vlan = dict(vlan_query.get_object(context, **dic_vlan))
        except Exception as e:
            raise exception.IsNotExistError(param_name=uuid)
        val_ifnames = []
        val_ifnames += is_vlan['ifnames']
        for ifname in dic['ifnames']:
            if ifname not in is_vlan['ifnames']:
                raise exception.ParamValueError(param_name=ifname)
            else:
                val_ifnames.remove(ifname)
        if len(val_ifnames) == 0:
            vlan_obj = objects.FwVlanInfo(context)
            response = vlan_obj.delete(context, is_vlan['id'])
        else:
            target_values = {}
            target_values["ifnames"] = val_ifnames
            vlan_obj = objects.FwVlanInfo(context, **target_values)
            response = vlan_obj.update(context, uuid, vlan_obj.as_dict())
        self.rpc_api.reload_topic(view['agent_ip'])
        try:
            rpc_dict = {}
            rpc_dict['vlan_number'] = is_vlan['vlan_number']
            rpc_dict['ifnames'] = dic['ifnames']
            response_fw = self.rpc_api.del_vlan(context, rpc_dict)
        except Exception as e:
            vlan_obj = objects.FwVlanInfo(context)
            vlan_ret = vlan_obj.update(context, dic['id'], is_vlan)
            raise e
        self.db_common.update_operation_history(context, history['id'],
                                                status='SUCCESS')
        return response

    def get_vlan(self, context, id):
        """
        get a vlan handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        target_values = {}
        target_values["id"] = id
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
        vlan_obj = objects.FwVlanInfo(context)
        sql_str_header = "select fw_vlan_info.* from" \
                         " fw_vlan_info,vres_agent_view" \
                         " where fw_vlan_info.vres_id = " \
                         "vres_agent_view.vres_id " \
                         "and fw_vlan_info.deleted = '0' "
        name_dic = dic
        lik_list = ['ifnames', 'ipaddr']
        search_list = ['tenant_id', 'dc_name', 'network_zone']
        lik_dic, search_dic = tools.classfiy_sql_keys(
            name_dic, lik_list, search_list)
        sql_str = self.db_common.put_sql(sql_str_header, lik_dic, search_dic)
        vlan_objs = vlan_obj.get_all_objects(context, sql_str)
        return vlan_objs

    # this is a netservice operation
    def create_netservice(self, context, dic):
        """
        create a netservice handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        dic['agent_type'] = 'FW'
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
        vfw_dic = {}
        vfw_dic['vfw_name'] = dic['vfwname']
        vfw_dic['vres_id'] = vres_id
        vfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
        if vfw is None:
            raise exception.IsNotExistError(param_name=dic['vfwname'])
        vfw_id = vfw["id"]
        proto_name = protocol.match_proto(dic['proto'])
        name = "%s%s" % (proto_name, dic['port'])
        target_values = {}
        target_values['vfw_id'] = vfw_id
        target_values['name'] = name
        target_values['deleted'] = False
        netserv_obj = objects.FwNetservicesInfo(context, **target_values)
        ner_serv = netserv_obj.get_objects(context, **target_values)
        if len(ner_serv) != 0:
            raise exception.HaveSameObject(param_name="%s,%s" % (dic['proto'],
                                                                 dic['port']))
        vfwname = vfw["vfw_name"]
        dic["name"] = name
        dic["vfw_id"] = vfw_id
        dic["vfwname"] = vfwname
        netserv_obj = objects.FwNetservicesInfo(context, **dic)
        res = netserv_obj.create(context, netserv_obj.as_dict())
        self.rpc_api.reload_topic(view['agent_ip'])
        try:
            response_fw = self.rpc_api.create_netservice(context, dic)
        except Exception as e:
            LOG.error(_LE("Create Netservice response on device failed"))
            netserv_obj.delete(context, res["id"])
            raise e

        self.db_common.update_operation_history(context, history['id'],
                                                status='SUCCESS')
        return res

    def del_netservice(self, context, dic):
        """
        delete a netservice handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        dic['agent_type'] = 'FW'
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
        try:
            netserv_info = netserv_obj.get_object(context, **target_values)
        except Exception:
            raise exception.IsNotExistError(param_name=uuid)
        response = netserv_obj.delete(context, uuid)
        self.rpc_api.reload_topic(view['agent_ip'])
        try:
            self.rpc_api.del_netservice(context, netserv_info)
        except Exception as e:
            LOG.error(_LE("delete netservice on device failed"))
            netserv_obj.update(context, uuid, netserv_info)
            raise e
        self.db_common.update_operation_history(context, history['id'],
                                                status='SUCCESS')
        return response

    def get_netservice(self, context, id):
        """
        get a netservice handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        target_values = {}
        target_values["id"] = id
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
        dic['agent_type'] = 'FW'
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

    def get_netservices_by_fuzzy_query(self, context, dic):
        LOG.info(_LI("the fuzzy_query_for_netservices method of"
                     " the fw_manager start"))
        view = {}
        view['tenant_id'] = dic['tenant_id']
        view['network_zone'] = dic['network_zone']
        view['dc_name'] = dic['dc_name']
        view_infos = self.db_common.get_vres_agent_vfw_view(context, **view)
        if len(view_infos) == 0:
            return view_infos

        # init the DB operations object
        obj = objects.FwNetservicesInfo(context)
        dic['deleted'] = "0"
        search_list = ['deleted']
        like_list = []
        keys = dic.keys()
        if "vfwname" in keys:
            if tools.is_not_nil(dic['vfwname']):
                search_list.append("vfwname")
        if "proto" in keys:
            if tools.is_not_nil(dic['proto']):
                search_list.append("proto")
        response = []
        for views in view_infos:
            dic["vfw_id"] = views["vfw_id"]
            search_list.append("vfw_id")
            like_dic, search_dic = tools.classfiy_sql_keys(dic, like_list,
                                                           search_list)
            infos = obj.get_all_objects_by_conditions(context,
                                                      like_dic, search_dic)
            response.extend(infos)
        return response

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
        # get the value vfw_id(fw_vfw_info_id)
        vfw_dic = {}
        vfw_dic['vfw_name'] = addrobj_infos['vfwname']
        vfw_dic['vres_id'] = vres_agent_obj.vres_id
        rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)
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
            raise exception.HaveSameObject(param_name=target_addrobj.name)
        # change the addrobj values with dic format
        target_values = {}
        target_values['vfwname'] = addrobj_infos['vfwname']
        target_values['vfw_id'] = rstfwvfw.id
        target_values['operation_fro'] = 'AUTO'
        merge_dict = tools.dict_merge(addrobj_infos, target_values)
        addrobj = objects.FwAddrObjInfo(context, **merge_dict)
        # create the addrobj info in db
        result = self.db_common.create_in_storage(context, addrobj)
        self.rpc_api.reload_topic(vres_agent_obj['agent_ip'])
        try:
            dic = {}
            dic['name'] = addrobj_infos['name']
            dic['ip'] = addrobj_infos['ip']
            # dic['expIp'] = tools.joinString(addrobj_infos['expip'])
            dic['vfwName'] = addrobj_infos['vfwname']
            response_fw = self.rpc_api.add_addrobj(context, dic)
        except Exception as e:
            result = addrobj.delete(context, result['id'])
            raise e
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return result

    def delete_addrobj(self, context, addrobj_infos):
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
        # addrobj_infos = dict(addrobj_infos)
        addrobj = objects.FwAddrObjInfo(context, **addrobj_infos)
        try:
            dic = addrobj.as_dict()
            org_addr_ret = addrobj.get_object(context, **dic)
        except Exception as e:
            raise IsNotExistError(param_name=addrobj_infos['id'])
            # raise e
        result = addrobj.delete(context, addrobj_infos['id'])
        self.rpc_api.reload_topic(vres_agent_obj['agent_ip'])
        try:
            trans_dict = {}
            trans_dict['name'] = result.name
            trans_dict['vfwName'] = result.vfwname
            response_fw = self.rpc_api.del_addrobj(context, trans_dict)
        except Exception as e:
            result = addrobj.update(context, addrobj_infos['id'], org_addr_ret)
            raise e
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return result

    def get_addrobj(self, context, id):
        # get the one addrobj in db
        target_values = {}
        target_values = id
        target_values['deleted'] = False
        addrobj = objects.FwAddrObjInfo(context)
        # try/catch the no one get
        try:
            result = addrobj.get_object(context, **target_values)
        except Exception:
            LOG.warning(
                _LW("No addrobj with id=%(id)s in DB"),
                {"id": target_values['id']})
            raise exception.IsNotExistError(
                param_name="addrobj with id=" + target_values['id'])
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
            raise exception.HaveSameObject(param_name=target_addrobj.name)
        # change the snataddrpool values with dic format
        target_values = {}
        target_values['vfwname'] = snataddrpool_infos['vfwname']
        target_values['vfw_id'] = rstfwvfw.id
        target_values['operation_fro'] = 'AUTO'
        merge_dict = tools.dict_merge(snataddrpool_infos, target_values)
        snataddrpool = objects.FwSnatAddrPoolInfo(context, **merge_dict)
        # create the snataddrpool info in db
        result = self.db_common.create_in_storage(context, snataddrpool)
        self.rpc_api.reload_topic(vres_agent_obj['agent_ip'])
        try:
            response_fw = self.rpc_api.add_snataddrpool(context,
                                                        snataddrpool_infos)
        except Exception as e:
            snataddrpool.delete(context, result['id'])
            raise e
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
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
        org_obj = objects.FwSnatAddrPoolInfo(context, **snataddrpool_infos)
        try:
            dic = org_obj.as_dict()
            dic['deleted'] = False
            org_dict = dict(org_obj.get_object(context, **dic))
        except Exception as e:
            raise IsNotExistError(param_name=snataddrpool_infos['id'])
        snataddrpool = objects.FwSnatAddrPoolInfo(context,
                                                  **snataddrpool_infos)
        result = snataddrpool.delete(context, snataddrpool_infos['id'])
        self.rpc_api.reload_topic(vres_agent_obj['agent_ip'])
        try:
            response_fw = self.rpc_api.del_snataddrpool(context,
                                                        org_dict)
        except Exception as e:
            snataddrpool.update(context, snataddrpool_infos['id'], org_dict)
            raise e
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
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
        # get the colunm vfw_id(fw_vfw_info_id)
        vfw_dic = {}
        vfw_dic['vfw_name'] = snataddrpool_infos['vfwname']
        vfw_dic['vres_id'] = vres_agent_obj.vres_id
        rstfwvfw = self.db_common.get_fw_vfw_id(context, **vfw_dic)

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
            raise exception.HaveSameObject(param_name=check_vfw_obj.vfw_name)
        response_vfw = self.db_common.create_in_storage(context, vfw_obj)
        self.rpc_api.reload_topic(view_obj['agent_ip'])
        try:
            self.rpc_api.create_vfw(context, vfw)
        except Exception as e:
            LOG.error(_LE("Create vfw on device failed"))
            # since create failed in device, so delete object in DB
            vfw_obj.delete(context, response_vfw['id'])
            raise e
        self.db_common.update_operation_history(context, history['id'],
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
            vfw_info = vfw_obj.get_object(context, **vfw_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="vfw with id=" +
                                                       vfw_dic['id'])
        vfw["name"] = vfw_info["vfw_name"]
        response_vfw = vfw_obj.delete(context, vfw['id'])
        self.rpc_api.reload_topic(view_obj['agent_ip'])
        try:
            self.rpc_api.delete_vfw(context, vfw)
        except Exception as e:
            LOG.error(_LE("Delete vfw on device failed"))
            vfw_obj.update(context, response_vfw['id'], vfw_dic)
            raise e
        self.db_common.update_operation_history(context, history['id'],
                                                status='SUCCESS')
        return response_vfw

    def get_vfw(self, context, id):
        vfw_dic = {}
        vfw_dic['id'] = id
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

    def get_vfws_by_fuzzy_query(self, context, dic):
        view = {}
        view['tenant_id'] = dic['tenant_id']
        view['network_zone'] = dic['network_zone']
        view['dc_name'] = dic['dc_name']
        view_infos = self.db_common.get_vres_agent_view_for_fw(context, **view)
        if len(view_infos) == 0:
            return view_infos

        # init the DB operations object
        obj = objects.VFW(context)
        dic['deleted'] = "0"
        search_list = ['deleted']
        like_list = []
        keys = dic.keys()
        if "network_zone_class" in keys:
            if tools.is_not_nil(dic['network_zone_class']):
                search_list.append("network_zone_class")
        if "protection_class" in keys:
            if tools.is_not_nil(dic['protection_class']):
                search_list.append("protection_class")
        if "resource" in keys:
            if tools.is_not_nil(dic['resource']):
                like_list.append("resource")
        if "name" in keys:
            if tools.is_not_nil(dic['name']):
                like_list.append("name")
        response = []
        for views in view_infos:
            dic["vres_id"] = views["vres_id"]
            search_list.append("vres_id")
            like_dic, search_dic = tools.classfiy_sql_keys(dic, like_list,
                                                           search_list)
            infos = obj.get_all_objects_by_conditions(context,
                                                      like_dic, search_dic)
            response.extend(infos)
        return response

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
            raise exception.HaveSameObject(param_name=check_dnat_obj.name)
        response_dnat = self.db_common.create_in_storage(context, dnat_obj)
        self.rpc_api.reload_topic(view_obj['agent_ip'])

        try:
            self.rpc_api.create_dnat(context, dnat)
        except Exception as e:
            LOG.error(_LE("Create vfw on device failed"))
            # since create failed in device, so delete object in DB
            dnat_obj.delete(context, response_dnat['id'])
            raise e
        self.db_common.update_operation_history(context, history['id'],
                                                status='SUCCESS')
        return response_dnat

    def delete_dnat(self, context, dnat):
        tenant_id = dnat['tenant_id']
        net_zone = dnat['network_zone']
        dc_name = dnat['dc_name']
        view_obj = self.db_common.get_vres_agent_view(context,
                                                      tenant_id=tenant_id,
                                                      agent_type='FW',
                                                      network_zone=net_zone,
                                                      dc_name=dc_name)
        vres_id = view_obj['vres_id']
        # insert operation history
        dnat_str = json.dumps(dnat)
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=dnat_str,
                                                          method='CREATE',
                                                          status='FAILED')
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
        dnat["vfwname"] = dnat_info["vfwname"]
        dnat["name"] = dnat_info["name"]
        self.rpc_api.reload_topic(view_obj['agent_ip'])
        try:
            self.rpc_api.delete_dnat(context, dnat)
        except Exception as e:
            LOG.error(_LE("Delete dnat on device failed"))
            dnat_obj.update(context, dnat_info['id'], dnat_dic)
            raise e
        self.db_common.update_operation_history(context, history['id'],
                                                status='SUCCESS')

        return dnat_info

    def get_dnat(self, context, id):
        dnat_dic = {}
        dnat_dic['id'] = id
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

    def get_dnats_by_fuzzy_query(self, context, dic):
        """
        get dnat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        view = {}
        view['tenant_id'] = dic['tenant_id']
        view['network_zone'] = dic['network_zone']
        view['dc_name'] = dic['dc_name']
        view_infos = self.db_common.get_vres_agent_vfw_view(context, **view)
        if len(view_infos) == 0:
            return view_infos

        # init the DB operations object
        obj = objects.Dnat(context)
        dic['deleted'] = "0"
        search_list = ['deleted']
        like_list = []
        keys = dic.keys()
        if "vfwname" in keys:
            if tools.is_not_nil(dic['vfwname']):
                search_list.append("vfwname")
        if "inifname" in keys:
            if tools.is_not_nil(dic['inifname']):
                like_list.append("inifname")
        if "slot" in keys:
            if tools.is_not_nil(dic['slot']):
                like_list.append("slot")
        if "lanipstart" in keys:
            if tools.is_not_nil(dic['lanipstart']):
                like_list.append("lanipstart")
        if "wanip" in keys:
            if tools.is_not_nil(dic['wanip']):
                like_list.append("wanip")
        if "lanipend" in keys:
            if tools.is_not_nil(dic['lanipend']):
                like_list.append("lanipend")
        response = []
        for views in view_infos:
            dic["vfw_id"] = views["vfw_id"]
            search_list.append("vfw_id")
            like_dic, search_dic = tools.classfiy_sql_keys(dic, like_list,
                                                           search_list)
            infos = obj.get_all_objects_by_conditions(context,
                                                      like_dic, search_dic)
            response.extend(infos)
        return response

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
        srcipobjnames = []
        dstipobjnames = []
        if 'srcipobjips' in packetfilter.keys():
            srcips = packetfilter['srcipobjips']
            for ip in srcips:
                name = self._get_addrobjname(context, rstfwvfw.id, ip)
                srcipobjnames.append(name)
        if 'dstipobjips' in packetfilter.keys():
            srcips = packetfilter['dstipobjips']
            dstipobjnames = []
            for ip in srcips:
                name = self._get_addrobjname(context, rstfwvfw.id, ip)
                dstipobjnames.append(name)
        target_values = {}
        target_values['vfw_id'] = rstfwvfw.id
        # if srcIpObjNames/dstIpObjNames is [], it's mean 'no ip limit'
        target_values['srcipobjnames'] = srcipobjnames
        target_values['dstipobjnames'] = dstipobjnames
        merge_dict = tools.dict_merge(packetfilter, target_values)
        packetfilter_obj = objects.PacketFilter(context, **merge_dict)
        check_packetfilter_dic = {}
        check_packetfilter_dic['name'] = packetfilter['name']
        check_packetfilter_dic['vfw_id'] = rstfwvfw.id
        checkpacketfilter = objects.PacketFilter(context,
                                                 **check_packetfilter_dic)
        if self.db_common.is_exist_object(context, checkpacketfilter):
            raise exception.HaveSameObject(param_name=checkpacketfilter.name)
        response = self.db_common.create_in_storage(context, packetfilter_obj)
        self.rpc_api.reload_topic(view_obj['agent_ip'])
        try:
            merge_dict['srcipobjnames'] = tools.joinString(
                merge_dict['srcipobjnames'])
            merge_dict['dstipobjnames'] = tools.joinString(
                merge_dict['dstipobjnames'])
            merge_dict['servicenames'] = tools.joinString(
                merge_dict['servicenames'])
            self.rpc_api.create_packetfilter(context, merge_dict)
        except Exception as e:
            LOG.error(_LE("Create vfw on device failed"))
            # since create failed in device, so delete object in DB
            packetfilter_obj.delete(context, response['id'])
            raise e
        self.db_common.update_operation_history(context, history['id'],
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
            raise exception.IsNotExistError(
                param_name="packetfilter"
                           " with id=" + packetfilter['id'])
        response = packetfilter_obj.delete(context, packetfilter['id'])
        self.rpc_api.reload_topic(view_obj['agent_ip'])
        try:
            trans_dict = {}
            trans_dict['vfwName'] = response.vfwname
            trans_dict['name'] = response.name
            self.rpc_api.delete_packetfilter(context, trans_dict)
        except Exception as e:
            LOG.error(_LE("Delete packetfilter on device failed"))
            packetfilter_obj.update(context, response['id'], packetfilter_dic)
            raise e
        self.db_common.update_operation_history(context, history['id'],
                                                status='SUCCESS')
        return response

    def get_packetfilter(self, context, id):
        packetfilter_obj = objects.PacketFilter(context)
        packetfilter_dic = {}
        packetfilter_dic['id'] = id
        packetfilter_dic['deleted'] = False
        try:
            response = packetfilter_obj.get_object(context, **packetfilter_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="packetfilter"
                                                       " with id=" + id)
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

    def _get_addrobjname(self, context, vfwid, addrobjip):
        """
        Use for get address object name by the address object's
        corresponding IP info and related vfw info
        """
        target_addrobj = objects.FwAddrObjInfo(context)
        addr_obj_dic = {}
        addr_obj_dic['vfw_id'] = vfwid
        addr_obj_dic['ip'] = addrobjip
        addr_obj_dic['deleted'] = False
        try:
            addrobjinfo = target_addrobj.get_object(context, **addr_obj_dic)
        except Exception:
            raise exception.IsNotExistError(
                param_name="addrObjInfo"
                           " with ip=" +
                           addr_obj_dic['ip'] +
                           "and vfw_id=" +
                           addr_obj_dic['vfw_id'])
        return addrobjinfo.name

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
        self.rpc_api.reload_topic(revs_agent['agent_ip'])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
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
        self.rpc_api.reload_topic(revs_agent['agent_ip'])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return result

    def get_vrf(self, context, id):

        # get the vrf values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values["id"] = id

        fw_obj = objects.FW_Vrf_Object(context, **target_values)
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
                ipname = self.db_common.get_addrobj_name(context, **addrobj)
                srcipobjname_new.append(ipname)
            else:
                srcipobjname_new.append("all")
        else:
            for key in srcipobjname:
                addrobj["ip"] = key
                ipname = self.db_common.get_addrobj_name(context, **addrobj)
                srcipobjname_new.append(ipname)

        if len(dstipobjname) == 0:
            dstipobjname_new.append("all")
        elif len(dstipobjname) == 1:
            if (dstipobjname[0] is not "all"):
                addrobj["ip"] = dstipobjname[0]
                ipname = self.db_common.get_addrobj_name(context, **addrobj)
                dstipobjname_new.append(ipname)
            else:
                dstipobjname_new.append("all")
        else:
            for key in dstipobjname:
                addrobj["ip"] = key
                ipname = self.db_common.get_addrobj_name(context, **addrobj)
                dstipobjname_new.append(ipname)
        fw_object['srcipobjname'] = srcipobjname_new
        fw_object['dstipobjname'] = dstipobjname_new
        # input the snat values with dic format
        #         fw_object['vfwname'] = revs_agent.tenant_id
        fw_object['vfw_id'] = vfw_id
        fw_object['operation_fro'] = 'AUTO'
        fw_obj = objects.FW_Snat_Object(context, **fw_object)
        # create the snat info in db
        result = self.db_common.create_in_storage(context, fw_obj)
        self.rpc_api.reload_topic(revs_agent['agent_ip'])
        try:
            self.rpc_api.create_snat(context, fw_object)
        except Exception as e:
            fw_obj.delete(context, result["id"])
            raise e
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
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
        self.rpc_api.reload_topic(revs_agent['agent_ip'])
        try:
            self.rpc_api.del_snat(context, result)
        except Exception as e:
            val = {}
            val["deleted"] = False
            fw_obj.update(context, result["id"], val)
            raise e
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return result

    def get_snat(self, context, id):
        # get the staticnat values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values["id"] = id

        fw_obj = objects.FW_Snat_Object(context, **target_values)
        # get the staticnat info in db
        try:
            result = fw_obj.get_object(context, **target_values)
        except Exception:
            raise exception.IsNotExistError(param_name="snat with id=" + id)
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

    def get_snats_by_fuzzy_query(self, context, dic):
        """
        get snat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        view = {}
        view['tenant_id'] = dic['tenant_id']
        view['network_zone'] = dic['network_zone']
        view['dc_name'] = dic['dc_name']
        view_infos = self.db_common.get_vres_agent_vfw_view(context, **view)
        if len(view_infos) == 0:
            return view_infos

        # init the DB operations object
        obj = objects.FW_Snat_Object(context)
        dic['deleted'] = "0"
        search_list = ['deleted']
        like_list = []
        keys = dic.keys()
        if "vfwname" in keys:
            if tools.is_not_nil(dic['vfwname']):
                search_list.append("vfwname")
        if "srcIpObjIP" in keys:
            if tools.is_not_nil(dic['srcIpObjIP']):
                search_list.append("srcIpObjIP")
        if "dstIpObjIP" in keys:
            if tools.is_not_nil(dic['dstIpObjIP']):
                search_list.append("dstIpObjIP")
        if "name" in keys:
            if tools.is_not_nil(dic['name']):
                like_list.append("name")
        if "outIfName" in keys:
            if tools.is_not_nil(dic['outIfName']):
                like_list.append("outIfName")
        if "wanIpPoolIP" in keys:
            if tools.is_not_nil(dic['wanIpPoolIP']):
                like_list.append("wanIpPoolIP")
        response = []
        for views in view_infos:
            dic["vfw_id"] = views["vfw_id"]
            search_list.append("vfw_id")
            like_dic, search_dic = tools.classfiy_sql_keys(dic, like_list,
                                                           search_list)
            infos = obj.get_all_objects_by_conditions(context,
                                                      like_dic, search_dic)
            response.extend(infos)
        return response

    # this is a snat operation
    def create_securityzone(self, context, fw_dic):
        """
        create securityZone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vargs = {}
        vargs['tenant_id'] = fw_dic['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_dic['network_zone']
        vargs['dc_name'] = fw_dic['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_dic)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'CREATE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # get the value vfw_id(fw_vfw_info_id)
        # get the value vfw_id(fw_vfw_info_id)
        vfw_ret = self.db_common.get_fw_vfw_id(context,
                                               vfw_name=fw_dic['vfwname'],
                                               vres_id=revs_agent.vres_id,
                                               )
        # input the securityZone values with dic format
        #         fw_object['vfwname'] = revs_agent.tenant_id
        fw_dic['vfw_id'] = vfw_ret.id
        fw_dic['operation_fro'] = 'AUTO'
        fw_obj = objects.FW_SecurityZone_Object(context, **fw_dic)
        # create the securityZone info in db
        result = self.db_common.create_in_storage(context, fw_obj)
        self.rpc_api.reload_topic(revs_agent['agent_ip'])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        try:
            response_fw = self.rpc_api.create_securityzone(context, fw_dic)
        except Exception as e:
            fw_obj.delete(context, result['id'])
            raise e
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return result

    def update_securityzone(self, context, fw_object):
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
        self.rpc_api.reload_topic(revs_agent['agent_ip'])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return result

    def delete_securityzone(self, context, fw_dic):
        """
        del securityZone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        vargs = {}
        vargs['tenant_id'] = fw_dic['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_dic['network_zone']
        vargs['dc_name'] = fw_dic['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)
        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_dic)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'DELETE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        old_ret = None
        try:
            fw_obj = objects.FW_SecurityZone_Object(context, **fw_dic)
            dic = fw_obj.as_dict()
            old_ret = fw_obj.get_object(context, **dic)
        except Exception as e:
            raise IsNotExistError(param_name=fw_dic['id'])
        result = fw_obj.delete(context, fw_dic["id"])
        self.rpc_api.reload_topic(revs_agent['agent_ip'])
        try:
            transe_dict = {}
            transe_dict['name'] = old_ret.name
            transe_dict['vfwName'] = old_ret.vfwname
            response_fw = self.rpc_api.delete_securityzone(
                context, transe_dict)
        except Exception as e:
            fw_obj.update(context, fw_dic['id'], old_ret)
            raise e
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return {"ret_msg": "success", "ret_code": "200"}

    def get_securityzone(self, context, id):
        # get_all the securityZone values with dic format
        target_values = {}
        target_values['deleted'] = False
        target_values["id"] = id
        fw_obj = objects.FW_SecurityZone_Object(context)
        try:
            result = fw_obj.get_object(context, **target_values)
        except Exception:
            raise exception.IsNotExistError(
                param_name="securityZone with id=" + id)
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result

    def get_securityzones(self, context, fw_dic):
        """
        get_all securityZone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        vlan_obj = objects.FwVlanInfo(context)
        sql_str_header = "select fw_security_zone_info.* from " \
                         "fw_security_zone_info,view_vfw_vres_agent " \
                         "where fw_security_zone_info.vres_id = " \
                         "view_vfw_vres_agent.vres_id  " \
                         "and fw_security_zone_info.deleted = '0' " \
                         "and fw_security_zone_info.vfw_id"
        name_dic = fw_dic
        lik_list = ['ifnames', 'ipaddr']
        search_list = ['tenant_id', 'dc_name', 'network_zone']
        lik_dic, search_dic = tools.classfiy_sql_keys(
            name_dic, lik_list, search_list)
        sql_str = self.db_common.put_sql(sql_str_header, lik_dic, search_dic)
        vlan_objs = vlan_obj.get_all_objects(context, sql_str)
        return vlan_objs

        # vargs = {}
        # vargs['tenant_id'] = fw_dic['tenant_id']
        # vargs['agent_type'] = 'FW'
        # vargs['network_zone'] = fw_dic['network_zone']
        # vargs['dc_name'] = fw_dic['dc_name']
        # revs_agent = self.db_common.get_vres_agent_view(context,
        #                                                 **vargs)
        # # get the value vfw_id(fw_vfw_info_id)
        # rstfwvfw = self.db_common.get_fw_vfw_id(context,
        #                                         vfw_name=fw_dic['vfw'],
        #                                         vres_id=revs_agent.vres_id,
        #                                         )
        #
        # # get_all the securityZone values with dic format
        # target_values = {}
        # target_values['deleted'] = False
        # target_values['vfw_id'] = rstfwvfw.id
        # #         merge_dict = tools.dict_merge(fw_object, target_values)
        # fw_obj = objects.FW_SecurityZone_Object(context, **target_values)
        # # get_all the securityZone info in db
        #
        # result = fw_obj.get_objects(context, **target_values)
        # # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        # return result

    def securityzone_addif(self, context, fw_dic):
        vargs = {}
        vargs['tenant_id'] = fw_dic['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_dic['network_zone']
        vargs['dc_name'] = fw_dic['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_dic)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'UPDATE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # input the staticnat values with dic format
        fw_obj = objects.FW_SecurityZone_Object(context, **fw_dic)
        try:
            dic = fw_obj.as_dict()
            old_ret = fw_obj.get_object(context, **dic)
        except:
            raise IsNotExistError(param_name=fw_dic['id'])
        # create the staticnat info in db
        ifnames_dict = {}
        ifnames_dict['ifnames'] = deepcopy(old_ret.ifnames)
        if fw_dic['ifname'] not in ifnames_dict['ifnames']:
            ifnames_dict['ifnames'].append(fw_dic['ifname'])
        reuslt = fw_obj.update(context, fw_dic['id'], ifnames_dict)
        self.rpc_api.reload_topic(revs_agent['agent_ip'])
        try:
            transe_dic = {}
            transe_dic['ifName'] = fw_dic['ifname']
            transe_dic['vfwName'] = old_ret.vfwname
            transe_dic['zoneName'] = old_ret.name
            response_fw = self.rpc_api.securityzone_addif(context, transe_dic)
        except Exception as e:
            fw_obj.update(context, fw_dic['id'], old_ret)
            raise e
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return reuslt

    def securityzone_delif(self, context, fw_dic):
        vargs = {}
        vargs['tenant_id'] = fw_dic['tenant_id']
        vargs['agent_type'] = 'FW'
        vargs['network_zone'] = fw_dic['network_zone']
        vargs['dc_name'] = fw_dic['dc_name']
        revs_agent = self.db_common.get_vres_agent_view(context,
                                                        **vargs)

        vargs_history = {}
        vargs_history['input'] = json.dumps(fw_dic)
        vargs_history['vres_id'] = revs_agent.vres_id
        vargs_history['method'] = 'UPDATE'
        vargs_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **vargs_history)
        # input the staticnat values with dic format
        fw_obj = objects.FW_SecurityZone_Object(context, **fw_dic)
        try:
            dic = fw_obj.as_dict()
            old_ret = fw_obj.get_object(context, **dic)
        except:
            raise IsNotExistError(param_name=fw_dic['id'])
        # create the staticnat info in db
        ifnames_dict = {}
        ifnames_dict['ifnames'] = deepcopy(old_ret.ifnames)
        if fw_dic['ifname'] in ifnames_dict['ifnames']:
            ifnames_dict['ifnames'].remove(fw_dic['ifname'])
        reuslt = fw_obj.update(context, fw_dic['id'], ifnames_dict)
        self.rpc_api.reload_topic(revs_agent['agent_ip'])
        try:
            transe_dic = {}
            transe_dic['ifName'] = fw_dic['ifname']
            response_fw = self.rpc_api.securityzone_delif(context, transe_dic)
        except Exception as e:
            fw_obj.update(context, fw_dic['id'], old_ret)
            raise e
        self.db_common.update_operation_history(
            context, history.id, status='SUCCESS')
        return reuslt

    # this is a staticnat operation
    def create_staticnat(self, context, fw_object):
        """
        create staticnat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        fw_object['agent_type'] = 'FW'
        kw = self.db_common.merge_dict_view(fw_object)
        view = self.db_common.get_vres_agent_view(context, **kw)
        vres_id = view["vres_id"]
        input_str = json.dumps(fw_object)
        history_dic = {}
        history_dic["vres_id"] = vres_id
        history_dic["input"] = input_str
        history_dic["method"] = 'CREATE'
        history_dic["status"] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **history_dic)
        # get the value vfw_id(fw_vfw_info_id)
        varstaticnat = {}
        varstaticnat['vfw_name'] = fw_object['vfwname']
        varstaticnat['vres_id'] = view.vres_id
        varstaticnat['deleted'] = False
        rstfwvfw = self.db_common.get_fw_vfw_id(context, **varstaticnat)
        # input the staticnat values with dic format
        #         fw_object['vfwname'] = fw_object['vfwname']
        fw_object['vfw_id'] = rstfwvfw.id
        fw_object['operation_fro'] = 'AUTO'
        fw_obj = objects.FW_Staticnat_Object(context, **fw_object)
        # create the staticnat info in db
        result = self.db_common.create_in_storage(context, fw_obj)
        self.rpc_api.reload_topic(view['agent_ip'])
        try:
            self.rpc_api.create_staticnat(context, fw_object)
        except Exception as e:

            fw_obj.delete(context, result["id"])
            raise e
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return result

    def del_staticnat(self, context, fw_object):
        """
        del staticnat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        fw_object['agent_type'] = 'FW'
        kw = self.db_common.merge_dict_view(fw_object)
        view = self.db_common.get_vres_agent_view(context, **kw)
        vres_id = view["vres_id"]
        input_str = json.dumps(fw_object)
        history_dic = {}
        history_dic["vres_id"] = vres_id
        history_dic["input"] = input_str
        history_dic["method"] = 'DELETE'
        history_dic["status"] = 'FAILED'
        history = self.db_common.insert_operation_history(context,
                                                          **history_dic)

        # del the staticnat values with dic format
        fw_obj = objects.FW_Staticnat_Object(context, **fw_object)
        # del the staticnat info in db
        result = fw_obj.delete(context, fw_object["id"])
        fw_object["name"] = result["name"]
        fw_object["vfwName"] = result["vfwname"]
        self.rpc_api.reload_topic(view['agent_ip'])
        try:
            self.rpc_api.del_staticnat(context, fw_object)
        except Exception as e:
            val = {}
            val["deleted"] = False
            fw_obj.update(context, result["id"], val)
            raise e
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return result

    def get_staticnat(self, context, fw_object):
        target_values = {}
        target_values['deleted'] = False
        target_values["id"] = fw_object["id"]

        fw_obj = objects.FW_Staticnat_Object(context, **target_values)
        try:
            result = fw_obj.get_object(context, **target_values)
        except Exception:
            raise exception.IsNotExistError(param_name="Staticnat with id=" +
                                                       target_values['id'])
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        return result

    def get_staticnats_by_fuzzy_query(self, context, dic):
        """
        get staticnat handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        view = {}
        view['tenant_id'] = dic['tenant_id']
        view['network_zone'] = dic['network_zone']
        view['dc_name'] = dic['dc_name']
        view_infos = self.db_common.get_vres_agent_vfw_view(context, **view)
        if len(view_infos) == 0:
            return view_infos

        # init the DB operations object
        obj = objects.FW_Staticnat_Object(context)
        dic['deleted'] = "0"
        search_list = ['deleted']
        like_list = []
        keys = dic.keys()
        if "vfwname" in keys:
            if tools.is_not_nil(dic['vfwname']):
                search_list.append("vfwname")
        if "name" in keys:
            if tools.is_not_nil(dic['name']):
                like_list.append("name")
        if "ifname" in keys:
            if tools.is_not_nil(dic['ifname']):
                like_list.append("ifname")
        if "lanip" in keys:
            if tools.is_not_nil(dic['lanip']):
                like_list.append("lanip")
        if "wanip" in keys:
            if tools.is_not_nil(dic['wanip']):
                like_list.append("wanip")
        response = []
        for views in view_infos:
            dic["vfw_id"] = views["vfw_id"]
            search_list.append("vfw_id")
            like_dic, search_dic = tools.classfiy_sql_keys(dic, like_list,
                                                           search_list)
            infos = obj.get_all_objects_by_conditions(context,
                                                      like_dic, search_dic)
            response.extend(infos)
        return response
