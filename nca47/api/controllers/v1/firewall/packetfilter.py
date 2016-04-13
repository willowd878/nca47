from oslo_log import log as logging
from oslo_serialization import jsonutils as json
from oslo_messaging.exceptions import MessagingException
from nca47.api.controllers.v1 import tools
from nca47.api.controllers.v1.firewall import fw_base
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.common.exception import BadRequest
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamValueError
from nca47.manager import central

LOG = logging.getLogger(__name__)


class PacketFilterController(fw_base.BaseRestController):
    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(PacketFilterController, self).__init__()

    def create(self, req, *args, **kwargs):
        context = req.context
        try:
            if len(args) != 1:
                raise BadRequest(resource="create packetfilter operation",
                                 msg=req.url)
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'name', 'srczonename', 'dstzonename',
                                'vfwname']

            values = tools.validat_values(body_values, valid_attributes)
            if 'srcipobjips' in body_values.keys():
                for ipinfo in body_values['srcipobjips']:
                    if not tools._is_valid_ipv4_addr(ipinfo):
                        raise ParamValueError(param_name=ipinfo)
                values['srcipobjips'] = body_values['srcipobjips']
            if 'dstipobjips' in body_values.keys():
                for ipinfo in body_values['dstipobjips']:
                    if not tools._is_valid_ipv4_addr(ipinfo):
                        raise ParamValueError(param_name=ipinfo)
                values['dstipobjips'] = body_values['dstipobjips']
            if 'servicenames' in body_values.keys():
                values['servicenames'] = body_values['servicenames']
            valid_range = (0, 1)
            if 'action' in body_values.keys():
                if body_values['action'] not in valid_range:
                    raise ParamValueError(param_name='action')
                values['action'] = body_values['action']
            else:
                values['action'] = 0
            if 'log' in body_values.keys():
                if body_values['log'] not in valid_range:
                    raise ParamValueError(param_name='log')
                values['log'] = body_values['log']
            else:
                values['log'] = 0
            packetfilter_info = self.manager.create_packetfilter(context,
                                                                 values)
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
        return packetfilter_info

    def remove(self, req, *args, **kwargs):
        context = req.context
        try:
            if len(args) != 1:
                raise BadRequest(resource="delete packetfilter operation",
                                 msg=req.url)
            body_values = json.loads(req.body)
            valid_attributes = ['id', 'tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(body_values, valid_attributes)
            packetfilter_info = self.manager.delete_packetfilter(context,
                                                                 values)
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
        return packetfilter_info

    def list(self, req, *args, **kwargs):
        context = req.context
        try:
            if len(args) != 1:
                raise BadRequest(resource="list packetfilters operation",
                                 msg=req.url)
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'vfwname']
            values = tools.validat_values(body_values, valid_attributes)
            packetfilter_infos = self.manager.get_all_packetfilters(context,
                                                                    values)
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
        return packetfilter_infos

    def show(self, req, *args, **kwargs):
        context = req.context
        try:
            if len(args) != 1:
                raise BadRequest(resource="show packetfilter operation",
                                 msg=req.url)
            body_values = json.loads(req.body)
            valid_attributes = ['id']
            values = tools.validat_values(body_values, valid_attributes)
            packetfilter_info = self.manager.get_packetfilter(context, values)
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
        return packetfilter_info
