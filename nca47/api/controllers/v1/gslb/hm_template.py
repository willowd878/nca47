from nca47.api.controllers.v1 import base, tools as tool
from nca47.common.exception import ParamNull
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamValueError
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.manager import central
from oslo_log import log as logging
from oslo_messaging import RemoteError
from oslo_serialization import jsonutils as json

LOG = logging.getLogger(__name__)


class HmTemplateController(base.BaseRestController):

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(HmTemplateController, self).__init__()

    def create(self, req, *args, **kwargs):
        """create one hm_template"""
        try:
            LOG.info(_("create hm_template:body is %(json)s, args is %(args)s,"
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            array1 = ["tenant_id", "name", "types"]
            array2 = ["check_interval", "timeout", "max_retries"]
            # get the body
            dic = json.loads(req.body)
            dic_body = self.message_regrouping(dic, array1, array2)
            context = req.context
            response = self.manager.create_hm_template(context, dic_body)
            LOG.info(_("Return of Created hm_template Json is %(response)s !"),
                     {"response": response})
        except Nca47Exception as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = e.code
            return tool.ret_info(e.code, e.message)
        except RemoteError as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            return tool.ret_info(self.response.status, e.value)
        except Exception as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            return tool.ret_info(self.response.status, e.message)
        return tool.ret_info("200", response)

    def update(self, req, id, *args, **kwargs):
        """update the target hm template"""
        try:
            LOG.info(_("update hm template:body is %(json)s, args is %(args)s,"
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            dic = json.loads(req.body)
            dic['id'] = id
            c = req.context
            list_ = ["id", "tenant_id"]
            self.validat_parms(dic, list_)
            # the attributes can be changed
            attr_list = ["check_interval", "timeout", "max_retries",
                         "sendstring", "recvstring", "username", "password"]
            keys = dic.keys()
            if "check_interval" in keys:
                if not tool.is_not_nil(dic["check_interval"]):
                    raise ParamNull(param_name="check_interval")
            if "timeout" in keys:
                if not tool.is_not_nil(dic["timeout"]):
                    raise ParamNull(param_name="timeout")
            if "max_retries" in keys:
                if not tool.is_not_nil(dic["max_retries"]):
                    raise ParamNull(param_name="max_retries")
            upd_dic = {}
            for attr in attr_list:
                if attr in keys:
                    upd_dic[attr] = dic[attr]
                else:
                    continue
            response = self.manager.update_hm_template(c, upd_dic, dic['id'])
            LOG.info(_("Return of update hm template JSON  is %(response)s !"),
                     {"response": response})
        except Nca47Exception as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = e.code
            return tool.ret_info(e.code, e.message)
        except RemoteError as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            message = e.value
            return tool.ret_info(self.response.status, message)
        except Exception as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            return tool.ret_info(self.response.status, e.message)
        return tool.ret_info("200", response)

    def remove(self, req, id, *args, **kwargs):
        """delete the target hm template"""
        try:
            LOG.info(_("delete hm template:body is %(json)s, args is %(args)s,"
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            dic = {}
            dic.update(kwargs)
            dic['id'] = id
            c = req.context
            list_ = ["id", "tenant_id"]
            self.validat_parms(dic, list_)
            """from rpc server delete the hm template"""
            response = self.manager.delete_hm_template(c, dic['id'])
            LOG.info(_("Return of remove hm template JSON  is %(response)s !"),
                     {"response": response})
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except RemoteError as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            message = e.value
            return tool.ret_info(self.response.status, message)
        except Exception as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            return tool.ret_info(self.response.status, e.message)
        return tool.ret_info("200", "success")

    def show(self, req, id, *args, **kwargs):
        """show the target hm template"""
        try:
            LOG.info(_("get a hm template: args is %(args)s, "
                       "kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
            context = req.context
            response = self.manager.get_one_hm_template_db(context, id)
            LOG.info(_("Return of hm template JSON  is %(response)s !"),
                     {"response": response})
        except Nca47Exception as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = e.code
            return tool.ret_info(e.code, e.message)
        except RemoteError as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            message = e.value
            return tool.ret_info(self.response.status, message)
        except Exception as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            return tool.ret_info(self.response.status, e.message)
        return tool.ret_info("200", response)

    def list(self, req, *args, **kwargs):
        """show all of the hm template"""
        try:
            LOG.info(_("Get all hm template: args is %(args)s, "
                       "kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
            context = req.context
            dic = {}
            dic.update(kwargs)
            # from db server show the zone_records
            response = self.manager.get_hm_templates_db(context, dic)
            LOG.info(_("Return of get all hm template JSON is %(response)s !"),
                     {"response": response})
        except Nca47Exception as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = e.code
            return tool.ret_info(e.code, e.message)
        except RemoteError as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            message = e.value
            return tool.ret_info(self.response.status, message)
        except Exception as e:
            LOG.error(_LE('Exception Message: %s !' % (e.message)))
            LOG.exception(e)
            self.response.status = 500
            return tool.ret_info(self.response.status, e.message)
        return tool.ret_info("200", response)

    def validat_parms(self, values, valid_keys):
        """check the in value is null and nums"""
        recom_msg = tool.validat_values(values, valid_keys)
        return recom_msg

    def message_regrouping(self, dic, list_imp, list_uni):
        tool.validat_values(dic, list_imp)
        values = {}
        dic_key = dic.keys()
        for key_imp in list_imp:
            values[key_imp] = dic[key_imp]

        uni = {}
        for k in list_uni:
            if k not in dic_key:
                if k == "check_interval":
                    uni[k] = "10"
                elif k == "timeout":
                    uni[k] = "3"
                elif k == "max_retries":
                    uni[k] = "2"
                else:
                    continue

        merge = tool.dict_merge(values, uni)

        exist_imp = {}
        for key in dic_key:
            if key == "check_interval":
                if tool.is_not_nil(dic[key]):
                    try:
                        val = int(dic[key])
                        if val < 1 or val > 86400:
                            raise ParamValueError(param_name=val)
                    except Exception:
                        raise ParamValueError(param_name=val)
                    exist_imp[key] = dic[key]
                else:
                    exist_imp[key] = "10"
            elif key == "timeout":
                if tool.is_not_nil(dic[key]):
                    try:
                        val = int(dic[key])
                        if val < 1 or val > 86400:
                            raise ParamValueError(param_name=val)
                    except Exception:
                        raise ParamValueError(param_name=val)
                    exist_imp[key] = dic[key]
                else:
                    exist_imp[key] = "3"
            elif key == "max_retries":
                if tool.is_not_nil(dic[key]):
                    try:
                        val = int(dic[key])
                        if val < 1 or val > 10:
                            raise ParamValueError(param_name=val)
                    except Exception:
                        raise ParamValueError(param_name=val)
                    exist_imp[key] = dic[key]
                else:
                    exist_imp[key] = "2"
            else:
                continue
        new_dic = tool.dict_merge(merge, exist_imp)

        types = new_dic["types"]
        if types == "http" or types == "https":
            if "sendstring" in dic_key:
                new_dic["sendstring"] = dic["sendstring"]
            else:
                new_dic["sendstring"] = ""
            if "recvstring" in dic_key:
                new_dic["recvstring"] = dic["recvstring"]
            else:
                new_dic["recvstring"] = ""
            if "username" in dic_key:
                new_dic["username"] = dic["username"]
            else:
                new_dic["username"] = ""
            if "password" in dic_key:
                new_dic["password"] = dic["password"]
            else:
                new_dic["password"] = ""
        elif types == "udp":
            if "sendstring" in dic_key:
                new_dic["sendstring"] = dic["sendstring"]
            else:
                new_dic["sendstring"] = ""
        elif types == "icmp" or types == "tcp_syn":
            pass
        else:
            raise ParamValueError(param_name=types)
        return new_dic
