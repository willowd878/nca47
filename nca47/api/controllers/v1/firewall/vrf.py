from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1.firewall import fw_base
from nca47.common.i18n import _
from nca47.common.i18n import _LI, _LE
from nca47.common.exception import Nca47Exception
from oslo_log import log
from nca47.api.controllers.v1 import tools
from nca47.manager.central import CentralManager
from nca47.common.exception import BadRequest
from oslo_messaging.exceptions import MessagingException

LOG = log.getLogger(__name__)


class VRFController(fw_base.BaseRestController):
    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(VRFController, self).__init__()

    def create(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) > 1:
                raise BadRequest(resource="VRF create", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'name',
                                'vrfInterface']
            values = tools.validat_values(body_values, valid_attributes)
        # input the staticnat values with dic format
            LOG.info(_LI("input add_vrf body is %(json)s"),
                     {"json": body_values})
            response = self.manager.create_vrf(context, values)
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
            if len(args) > 1:
                raise BadRequest(resource="VRF del", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'id']
            values = tools.validat_values(body_values, valid_attributes)
        # input the vrf values with dic format
            LOG.info(_LI("delete vrf body is %(json)s"),
                     {"json": body_values})
            response = self.manager.del_vrf(context, values)
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
            if len(args) > 1:
                raise BadRequest(resource="VRF getAll", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(body_values, valid_attributes)
        # input the staticnat values with dic format
            LOG.info(_LI("get_all vrf body is %(json)s"),
                     {"json": body_values})
            response = self.manager.get_vrfs(context, values)
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
            if len(args) > 1:
                raise BadRequest(resource="VRF get", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'id']
            values = tools.validat_values(body_values, valid_attributes)
        # input the staticnat values with dic format
            LOG.info(_LI("get vrf body is %(json)s"),
                     {"json": body_values})
            response = self.manager.get_vrf(context, values)
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
