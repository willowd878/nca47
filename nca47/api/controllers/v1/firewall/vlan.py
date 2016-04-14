from nca47.manager.central import CentralManager
from nca47.common.exception import BadRequest
from nca47.common.exception import Nca47Exception
from oslo_log import log
from nca47.common.i18n import _LI, _LE
from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1 import tools
from oslo_messaging.exceptions import MessagingException
from nca47.api.controllers.v1.firewall import fw_base

LOG = log.getLogger(__name__)


class VLANController(fw_base.BaseRestController):

    """the method vlan operation"""

    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(VLANController, self).__init__()

    def create(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) != 1:
                raise BadRequest(resource="vlan operation", msg=url)
            json_body = req.body
            context = req.context
            dic = json.loads(json_body)
            list_ = ['tenant_id', 'dc_name', 'vlan_id',
                     'network_zone', 'ipaddr', "ifnames"]
            dic_body = tools.firewall_params(dic, list_)
            LOG.info(_LI("add_vlan body is %(json)s,args is %(args)s,"
                         "kwargs is %(kwargs)s"),
                     {"json": dic, "args": args, "kwargs": kwargs})
            response = self.manager.create_vlan(context, dic_body)
            return response
        except Nca47Exception as e:
            LOG.error(_LE('Nca47Exception! error info: ' + e.message))
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except MessagingException as e:
            self.response.status = 500
            return tools.ret_info(self.response.status, e.value)
        except Exception as e:
            LOG.error(_LE('Exception! error info: ' + e.message))
            self.response.status = 500
            message = "the values of the body format is error"
            return tools.ret_info(self.response.status, message)

    def remove(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) != 1:
                raise BadRequest(resource="vlan operation", msg=url)
            json_body = req.body
            context = req.context
            dic = json.loads(json_body)
            list_ = ['tenant_id', 'dc_name', 'id', 'network_zone', "ifnames"]
            dic_body = tools.firewall_params(dic, list_)
            LOG.info(_LI("del_vlan body is %(json)s, args is %(args)s,"
                         "kwargs is %(kwargs)s"),
                     {"json": json_body, "args": args, "kwargs": kwargs})
            response = self.manager.del_vlan(context, dic_body)
            return response
        except Nca47Exception as e:
            LOG.error(_LE('Nca47Exception! error info: ' + e.message))
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except MessagingException as e:
            self.response.status = 500
            return tools.ret_info(self.response.status, e.value)
        except Exception as e:
            LOG.error(_LE('Exception! error info: ' + e.message))
            self.response.status = 500
            message = "the values of the body format is error"
            return tools.ret_info(self.response.status, message)

    def show(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) != 1:
                raise BadRequest(resource="vlan operation", msg=url)
            json_body = req.body
            context = req.context
            dic = json.loads(json_body)
            list_ = ['id']
            dic_body = tools.firewall_params(dic, list_)
            LOG.info(_LI("get_vlan body is %(json)s, args is %(args)s,"
                         "kwargs is %(kwargs)s"),
                     {"json": json_body, "args": args, "kwargs": kwargs})
            response = self.manager.get_vlan(context, dic_body)
            return response
        except Nca47Exception as e:
            LOG.error(_LE('Nca47Exception! error info: ' + e.message))
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except MessagingException as e:
            self.response.status = 500
            return tools.ret_info(self.response.status, e.value)
        except Exception as e:
            LOG.error(_LE('Exception! error info: ' + e.message))
            self.response.status = 500
            message = "the values of the body format is error"
            return tools.ret_info(self.response.status, message)

    def list(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) != 1:
                raise BadRequest(resource="vlan operation", msg=url)
            context = req.context
            json_body = req.body
            dic = json.loads(json_body)
            list_ = ['tenant_id', 'dc_name', 'network_zone']
            dic_body = tools.firewall_params(dic, list_)
            LOG.info(_LI("get_all_vlan body is %(json)s, args is %(args)s,"
                         "kwargs is %(kwargs)s"),
                     {"json": json_body, "args": args, "kwargs": kwargs})
            response = self.manager.get_vlans(context, dic_body)
            return response
        except Nca47Exception as e:
            LOG.error(_LE('Nca47Exception! error info: ' + e.message))
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except MessagingException as e:
            self.response.status = 500
            return tools.ret_info(self.response.status, e.value)
        except Exception as e:
            LOG.error(_LE('Exception! error info: ' + e.message))
            self.response.status = 500
            message = "the values of the body format is error"
            return tools.ret_info(self.response.status, message)
