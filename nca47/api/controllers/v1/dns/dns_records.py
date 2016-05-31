from nca47.api.controllers.v1 import base
from nca47.common.i18n import _
from nca47.api.controllers.v1 import tools as tool
from oslo_log import log as logging
from nca47.manager import central
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamIsNotHaveError
from nca47.common.exception import ParamNull
from nca47.common.exception import ParamValueError
from nca47.common.exception import ParamFormatError
from oslo_serialization import jsonutils as json
from nca47.common.i18n import _LE
from oslo_messaging import RemoteError

LOG = logging.getLogger(__name__)


class DnsRecordsController(base.BaseRestController):

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(DnsRecordsController, self).__init__()

    def create(self, req, *args, **kwargs):
        """create the dns zone_record"""
        try:
            # test environment begin
            list1 = ['name', 'type', 'rdata', "tenant_id", "environment_name"]
            # end
            # production environment
            # list1 = ['name', 'type', 'rdata', "tenant_id"]
            # Add a default value for the attribute of the list2
            list2 = ['ttl', "klass"]
            # get the body
            dic = json.loads(req.body)
            # validate the in values of the zone_record
            dic_body = self.message_regrouping(dic, list1, list2)
            context = req.context
            LOG.info(_("req is %(json)s, args is %(args)s,"
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            # from rpc server create the zone_record
            # production environment
            # record = self.manager.create_record(context, dic_body)
            # test environment
            record = self.manager.create_record_in_test_env(context, dic_body)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tool.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tool.ret_info(self.response.status, exception.message)
        LOG.info(_("Return of create_zone_record JSON is %(record)s !"),
                 {"record": record})
        return record

    def update(self, req, id, *args, **kwargs):
        """update the dns zone_record"""
        try:
            dic = json.loads(req.body)
            dic['id'] = id
            list_ = ["tenant_id", "id"]
            if "ttl" not in dic.keys() and "rdata" not in dic.keys():
                raise ParamIsNotHaveError(param_name="rdata or ttl")
            if "ttl" in dic.keys():
                if tool.check_ttl(dic['ttl']):
                    list_.append("ttl")
                else:
                    raise ParamFormatError(param_name="ttl")
            if "rdata" in dic.keys():
                if tool.check_rdata(dic['rdata']):
                    list_.append("rdata")
                else:
                    raise ParamFormatError(param_name="rdata")
            if len(list_) == 0:
                raise ParamValueError(param_name="JSON")
            # get the body
            # validate the in values of the zone_record
            dic_body = self.validat_parms(dic, list_)
            c = req.context
            LOG.info(_("req is %(json)s, args is %(args)s, "
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            # from rpc server update the zone_record
            record = self.manager.update_record(c, dic_body)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tool.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tool.ret_info(self.response.status, exception.message)
        LOG.info(_("Return of update_record JSON  is %(record)s !"),
                 {"record": record})
        return record

    def remove(self, req, id, *args, **kwargs):
        """delete the dns zone_record"""
        try:
            dic = {}
            dic.update(kwargs)
            list_ = ["tenant_id", "id"]
            dic['id'] = id
            dic_body = self.validat_parms(dic, list_)
            # get the body
            # validate the in values of the zone_record
            c = req.context
            LOG.info(_("server is %(json)s, args is %(args)s, "
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            """from rpc server delete the zone_record"""
            record = self.manager.delete_record(c, dic_body)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tool.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tool.ret_info(self.response.status, exception.message)
        LOG.info(_("Return of remove_record JSON  is %(record)s !"),
                 {"record": record})
        return record

    def show(self, req, id, *args, **kwargs):
        """get the one of the dns zone_record"""
        record = None
        try:
            context = req.context
            if kwargs.get('device'):
                LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                         {"args": args, "kwargs": kwargs})
                # from rpc server show the zone_record
                # the id is ID of the device
                record = self.manager.get_dev_records(context, id)
            else:
                LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                         {"args": args, "kwargs": kwargs})
                # from db server show the zone_record
                record = self.manager.get_db_records(context, args[0])
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tool.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tool.ret_info(self.response.status, exception.message)
        LOG.info(_("Return of show_record JSON  is %(record)s !"),
                 {"record": record})
        return record

    def list(self, req, *args, **kwargs):
        """get the one of the dns zone_record"""
        record = None
        try:
            context = req.context
            LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
            dic = {}
            dic.update(kwargs)
            # production environment
            # record = self.manager.query_records(context, dic)
            # test environment
            list_ = ["tenant_id", "test_environment"]
            for key in list_:
                if key not in dic.keys():
                    raise ParamNull(param_name="tenant_id or test_environment")
            record = self.manager.query_records_in_test_env(context, dic)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tool.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tool.ret_info(self.response.status, exception.message)
        LOG.info(_("Return of query records JSON  is %(record)s !"),
                 {"record": record})
        return record

    def validat_parms(self, values, valid_keys):
        """check the in value is null and nums"""
        recom_msg = tool.validat_values(values, valid_keys)
        for value in recom_msg:
            if value == "name":
                if not tool.check_areaname(values['name']):
                    raise ParamFormatError(param_name=value)
            elif value == "id":
                if not tool.is_not_nil(values['id']):
                    raise ParamNull(param_name=value)
            elif value == "tenant_id":
                if not tool.is_not_nil(values['tenant_id']):
                    raise ParamNull(param_name=value)
            elif value == "type":
                if not tool.is_not_nil(values['type']):
                    raise ParamFormatError(param_name=value)
            elif value == "ttl":
                if not tool.check_ttl(values['ttl']):
                    raise ParamFormatError(param_name=value)
            elif value == "rdata":
                if not tool.check_rdata(values['rdata']):
                    raise ParamFormatError(param_name=value)
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
                if k == "ttl":
                    uni[k] = "3600"
                elif k == "klass":
                    uni[k] = "IN"
                else:
                    continue

        merge = tool.dict_merge(values, uni)

        exist_imp = {}
        for key in dic_key:
            if key == "ttl":
                if tool.is_not_nil(dic[key]):
                    exist_imp[key] = dic[key]
                else:
                    exist_imp[key] = "3600"
            elif key == "klass":
                if tool.is_not_nil(dic[key]):
                    exist_imp[key] = dic[key]
                else:
                    exist_imp[key] = "IN"
            else:
                continue
        new_list = list_imp + list_uni
        new_dic = tool.dict_merge(merge, exist_imp)
        return self.validat_parms(new_dic, new_list)
