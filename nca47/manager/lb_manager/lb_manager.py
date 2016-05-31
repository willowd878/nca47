from oslo_config import cfg
from oslo_log import log as logging
from nca47 import objects
from nca47.manager import db_common
from nca47.manager.lb_manager import lb_model as model


CONF = cfg.CONF
LOG = logging.getLogger(__name__)

LB_MANAGER = None


class LBManager(object):

    """
    LB operation handler class, using for handle client requests,
    """

    def __init__(self):
        self.db_common = db_common.DBCommon.get_instance()

    @classmethod
    def get_instance(cls):

        global LB_MANAGER
        if not LB_MANAGER:
            LB_MANAGER = cls()
        return LB_MANAGER

    def create_pool(self, context, real_dic):
        pool_list = []
        var_dic = {}
        var_dic["deleted"] = False
        pool = objects.lb_realServer_object(context)
        pool = pool.get_objects(context, **var_dic)
        index = len(pool)
        input_dic = real_dic
        rip = real_dic["rip"]
        for key in rip:
            index = index+1
            input_dic["rip"] = key
            input_dic["realservername"] = (
                                           input_dic["environment_name"] +
                                           "_" +
                                           input_dic["application"] + "_" +
                                           "R_" +
                                           str(index))
            input_dic["command_input"] = model.get_realserver(**input_dic)
            pool = objects.lb_realServer_object(context, **input_dic)
            pool = pool.create(context, pool.as_dict())
            pool_list.append(pool)
        return pool_list

    def create_member(self, context, member_dic):
        # member_list = []
        var_dic = {}
        sql = ("select * , count(distinct groupname) from \
                lb_group_info where deleted = 0 group by groupname;")
        var_dic["sql"] = sql
        member = objects.lb_group_object(context)
        member = member.get_all_objects(context, **var_dic)
        index = len(member) + 1
        input_dic = member_dic
        input_dic["groupname"] = (
                                  input_dic["environment_name"] +
                                  "_" +
                                  input_dic["application"] + "_" +
                                  "G_" +
                                  str(index))
        realservernames = member_dic["realservername"]
        realservername_list = []
        for key in realservernames:
            realservername_list.append(key["realservername"])
        input_dic["realservername"] = realservername_list
        input_dic["command_input"] = model.get_group(**input_dic)
        member = objects.lb_group_object(context, **input_dic)
        member = member.create(context, member.as_dict())
        # member_list.append(member)
        return member

    def create_vip(self, context, vip_dic):
        var_dic = {}
        var_dic["deleted"] = False
        vip = objects.lb_vip_object(context)
        vip = vip.get_objects(context, **var_dic)
        index = len(vip) + 1
        input_dic = vip_dic
        input_dic["virtualservername"] = (
                                          input_dic["environment_name"] +
                                          "_" +
                                          input_dic["application"] + "_" +
                                          "V_" +
                                          str(index))
        input_dic["command_input"] = model.get_vip(**input_dic)
        vip = objects.lb_vip_object(context, **input_dic)
        vip = vip.create(context, vip.as_dict())
        return vip

    def create_server(self, context, server_dic):
        server_list = []
        var_dic = {}
        var_dic["deleted"] = False
        server_ = objects.lb_server_object(context)
        server_ = server_.get_objects(context, **var_dic)
        input_dic = server_dic
        virt_name = server_dic["virtualservername"]
        froup_name = server_dic["groupname"]
        input_dic["virtualservername"] = virt_name["virtualservername"]
        input_dic["groupname"] = froup_name["groupname"]
        rports = server_dic["rport"]
        vports = server_dic["vport"]
        index = 0
        for key in rports:
            input_dic["rport"] = key
            input_dic["vport"] = vports[index]
            index = index+1
            input_dic["command_input"] = model.get_service(**input_dic)
            server_ = objects.lb_server_object(context, **input_dic)
            server_ = server_.create(context, server_.as_dict())
            server_list.append(server_)
        return server_list

    def delete_real_service(self, context, real_dic):
        var_dic = {}
        delete_list = []
        realservername = real_dic["realservername"]
        sql = ("select * , count(distinct groupname) from lb_group_info \
        where deleted = 0 and realservername like '%%" +
               realservername + "%%' group by groupname;")
        var_dic["sql"] = sql
        member = objects.lb_group_object(context)
        member = member.get_all_objects(context, **var_dic)
        member_list = []
        for key in member:
            member_list.append(key["groupname"])
        real_dic["groupname"] = member_list
        real_list = model.delete_realserver(
                                                   realservername)
        delete_list.append(real_list)
        for key in member_list:
            del_group_real_dic = {}
            del_group_real_dic["groupname"] = key
            del_group_real_dic["realservername"] = realservername
            group_del_list = model.delete_group_realser(**del_group_real_dic)
            delete_list.append(group_del_list)
        return delete_list
