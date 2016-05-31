from nca47.manager.central import CentralManager
from nca47.common.exception import ParamFormatError
from nca47.common.exception import Nca47Exception
from oslo_log import log
from nca47.common.i18n import _LI
from nca47.common.i18n import _LE
from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1 import tools
from oslo_messaging import RemoteError
from nca47.api.controllers.v1 import base

LOG = log.getLogger(__name__)


class NetServiceController(base.BaseRestController):

    """the method NetService operation"""

    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(NetServiceController, self).__init__()

    def create(self, req, *args, **kwargs):
        try:
            json_body = req.body
            context = req.context
            dic = json.loads(json_body)
            LOG.info(_LI("create_netservice body is %(json)s,args is "
                         "%(args)s, kwargs is %(kwargs)s"),
                     {"json": dic, "args": args, "kwargs": kwargs})
            list_ = ['tenant_id', 'dc_name', 'proto',
                     'network_zone', 'port', 'vfwname']
            dic_body = self.firewall_params(dic, list_)
            response = self.manager.create_netservice(context, dic_body)
        except Nca47Exception as e:
            LOG.error(_LE('Nca47Exception! error info: ' + e.message))
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as e:
            self.response.status = 500
            return tools.ret_info(self.response.status, e.value)
        except Exception as e:
            LOG.error(_LE('Exception! error info: ' + e.message))
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", response)

    def remove(self, req, id, *args, **kwargs):
        context = req.context
        try:
            LOG.info(_LI("args is %(args)s," "kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
            values = {}
            values.update(kwargs)
            list_ = ['tenant_id', 'dc_name', 'network_zone']
            dic_body = self.firewall_params(values, list_)
            dic_body["id"] = id
            self.manager.del_netservice(context, dic_body)
        except Nca47Exception as e:
            LOG.error(_LE('Nca47Exception! error info: ' + e.message))
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as e:
            self.response.status = 500
            return tools.ret_info(self.response.status, e.value)
        except Exception as e:
            LOG.error(_LE('Exception! error info: ' + e.message))
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", "success")

    def show(self, req, id, *args, **kwargs):
        context = req.context
        try:
            LOG.info(_LI("args is %(args)s,""kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
            response = self.manager.get_netservice(context, id)
        except Nca47Exception as e:
            LOG.error(_LE('Nca47Exception! error info: ' + e.message))
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as e:
            self.response.status = 500
            return tools.ret_info(self.response.status, e.value)
        except Exception as e:
            LOG.error(_LE('Exception! error info: ' + e.message))
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", response)

    def list(self, req, *args, **kwargs):
        try:
            context = req.context
            LOG.info(_LI("netserivce list args is %(args)s,kwargs"
                         " is %(kwargs)s"), {"args": args, "kwargs": kwargs})
            values = {}
            values.update(kwargs)
            list_ = ['tenant_id', 'dc_name', 'network_zone']
            self.firewall_params(values, list_)
            response = self.manager.get_netservices_by_fuzzy_query(context,
                                                                   values)
        except Nca47Exception as e:
            LOG.error(_LE('Nca47Exception! error info: ' + e.message))
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as e:
            self.response.status = 500
            return tools.ret_info(self.response.status, e.value)
        except Exception as e:
            LOG.error(_LE('Exception! error info: ' + e.message))
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", response)

    def firewall_params(self, dic, list_):
        dic = tools.filter_string_not_null(dic, list_)
        dic_key = dic.keys()
        for key in dic_key:
            val_key = dic[key]
            if key == "proto":
                if not tools.is_proto_range(val_key):
                    raise ParamFormatError(param_name=key)
            elif key == "port":
                if not tools._is_valid_port_range(val_key):
                    raise ParamFormatError(param_name=key)
            else:
                continue
        return dic
