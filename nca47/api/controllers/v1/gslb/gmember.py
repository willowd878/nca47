from nca47.api.controllers.v1 import base
from nca47.common.i18n import _
from nca47.api.controllers.v1 import tools as tool
from oslo_log import log as logging
from nca47.manager import central
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamValueError
from oslo_serialization import jsonutils as json
from nca47.common.i18n import _LE
from oslo_messaging import RemoteError

LOG = logging.getLogger(__name__)


class GmemberController(base.BaseRestController):

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(GmemberController, self).__init__()

    def create(self, req, *args, **kwargs):
        """create one gmember"""
        try:
            LOG.info(_("create gmember:body is %(json)s, args is %(args)s,"
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            array = ["gslb_zone_name", "tenant_id", "name",
                     "ip", "port", "enable"]
            # get the body
            dic = json.loads(req.body)
            dic_body = self.validat_parms(dic, array)
            context = req.context
            response = self.manager.create_gmember(context, dic_body)
            LOG.info(_("Return of Created Gmember Json is %(response)s !"),
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
        return tool.ret_info('200', response)

    def update(self, req, id, *args, **kwargs):
        """update the dns gmember"""
        try:
            LOG.info(_("update gmember:body is %(json)s, args is %(args)s,"
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            # get the body
            dic = json.loads(req.body)
            dic['id'] = id
            list_ = ["enable", "id", "tenant_id"]
            dic_body = self.validat_parms(dic, list_)
            # the attributes can be changed
            k = dic_body.keys()
            upd_dic = {}
            if "enable" in k:
                upd_dic["enable"] = dic["enable"]
            else:
                pass
            c = req.context
            response = self.manager.update_gmember(c, upd_dic, dic['id'])
            LOG.info(_("Return of update gmember JSON  is %(response)s !"),
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
        return tool.ret_info('200', response)

    def remove(self, req, id, *args, **kwargs):
        """delete the dns gmember"""
        try:
            LOG.info(_("delete gmember:body is %(json)s, args is %(args)s, "
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            c = req.context
            # get the body
            dic = {}
            dic.update(kwargs)
            dic['id'] = id
            list_ = ["id", "tenant_id"]
            self.validat_parms(dic, list_)
            """from rpc server delete the gmember"""
            response = self.manager.delete_gmember(c, dic['id'])
            LOG.info(_("Return of remove gmember JSON  is %(response)s !"),
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
        return tool.ret_info('200', "success")

    def show(self, req, id, *args, **kwargs):
        """get one of the dns gmember"""
        try:
            LOG.info(_("get a gmember: args is %(args)s, "
                       "kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
            context = req.context
            response = self.manager.get_one_gmember_db(context, id)
            LOG.info(_("Return of gmember JSON  is %(response)s !"),
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
        return tool.ret_info('200', response)

    def list(self, req, *args, **kwargs):
        """get  all of the dns gmember"""
        try:
            LOG.info(_("Get all gmembers: args is %(args)s, "
                       "kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
            context = req.context
            dic = {}
            dic.update(req.GET)

            response = self.manager.get_gmembers_db(context, dic)
            LOG.info(_("Return of get all gmember JSON  is %(response)s !"),
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
        return tool.ret_info('200', response)

    def validat_parms(self, values, valid_keys):
        """check the in value is null and nums"""
        recom_msg = tool.validat_values(values, valid_keys)
        dic_key = recom_msg.keys()
        for key in dic_key:
            val_key = recom_msg[key]
            if key == "ip":
                if not tool._is_valid_ipv4_addr(val_key):
                    raise ParamValueError(param_name=key)
            elif key == "port":
                if not tool._is_valid_port(val_key):
                    raise ParamValueError(param_name=key)
            elif key == "enable":
                validat = ["yes", "no"]
                if val_key not in validat:
                    raise ParamValueError(param_name=key)
            else:
                continue
        return recom_msg
