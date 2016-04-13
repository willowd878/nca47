from oslo_log import log as logging
from oslo_serialization import jsonutils as json
from oslo_messaging.exceptions import MessagingException
from nca47.api.controllers.v1.firewall import fw_base
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.manager import central
from nca47.api.controllers.v1 import tools
from nca47.common.exception import BadRequest
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamValueError

LOG = logging.getLogger(__name__)


class VFWController(fw_base.BaseRestController):
    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(VFWController, self).__init__()

    def create(self, req, *args, **kwargs):
        context = req.context
        valid_attributes = ['name', 'type', 'resource', 'tenant_id',
                            'dc_name', 'network_zone',
                            'network_zone_class']
        try:
            if len(args) != 1:
                raise BadRequest(resource="create vfw operation",
                                 msg=req.url)
            body_values = json.loads(req.body)
            values = tools.validat_values(body_values, valid_attributes)
            if 'protection_class' in body_values.keys():
                values['protection_class'] = body_values['protection_class']
            type_range = (2, 4, 8)
            if values['type'] not in type_range:
                raise ParamValueError(param_name='type')
            vfw_info = self.manager.create_vfw(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except MessagingException as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            message = "the values of the body format error"
            return tools.ret_info(self.response.status, message)
        return vfw_info

    def remove(self, req, *args, **kwargs):
        context = req.context
        try:
            if len(args) != 1:
                raise BadRequest(resource="delete vfw operation",
                                 msg=req.url)
            body_values = json.loads(req.body)
            valid_attributes = ['id', 'tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(body_values, valid_attributes)
            vfw_info = self.manager.delete_vfw(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except MessagingException as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            message = "the values of the body format error"
            return tools.ret_info(self.response.status, message)
        return vfw_info

    def list(self, req, *args, **kwargs):
        context = req.context
        try:
            if len(args) != 1:
                raise BadRequest(resource="list vfws operation",
                                 msg=req.url)
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(body_values, valid_attributes)
            if 'protection_class' in body_values.keys():
                values['protection_class'] = body_values['protection_class']
            vfw_info = self.manager.get_all_vfws(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except MessagingException as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            message = "the values of the body format error"
            return tools.ret_info(self.response.status, message)
        return vfw_info

    def show(self, req, *args, **kwargs):
        context = req.context
        try:
            if len(args) != 1:
                raise BadRequest(resource="show vfw operation",
                                 msg=req.url)
            body_values = json.loads(req.body)
            valid_attributes = ['id']
            values = tools.validat_values(body_values, valid_attributes)
            vfw_info = self.manager.get_vfw(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except MessagingException as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            message = "the values of the body format error"
            return tools.ret_info(self.response.status, message)
        return vfw_info
