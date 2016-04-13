from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1.firewall import fw_base
from nca47.common.i18n import _
from nca47.common.i18n import _LI, _LE
from nca47.common.exception import Nca47Exception
from oslo_log import log
from nca47.api.controllers.v1 import tools
from nca47.manager.central import CentralManager
from nca47.common.exception import ParamFormatError
from amqp.five import string
from nca47.common.exception import BadRequest
from oslo_messaging.exceptions import MessagingException
from nca47.common import exception

LOG = log.getLogger(__name__)


class SecurityZoneController(fw_base.BaseRestController):
    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(SecurityZoneController, self).__init__()

    def create(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) > 1:
                raise BadRequest(resource="SecurityZone create", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            # ADTEC_COMMENT: 需要加上vfwname 参数
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'name',
                                'ifnames', 'priority']
            values = tools.validat_values(body_values, valid_attributes)
            # input the SecurityZone values with dic format
            LOG.info(_LI("input add_SecurityZone body is %(json)s"),
                     {"json": body_values})
            values["name"] = (values["tenant_id"] + "_" +
                              values["network_zone"] +
                              "_" + values["name"])
            response = self.manager.create_securityZone(context, values)
            return response
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

    def remove(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) > 1:
                raise BadRequest(resource="SecurityZone del", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'id']
            values = tools.validat_values(body_values, valid_attributes)
            # input the SecurityZone values with dic format
            LOG.info(_LI("delete SecurityZone body is %(json)s"),
                     {"json": body_values})
            response = self.manager.del_securityZone(context, values)
            return response
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

    def list(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) > 1:
                raise BadRequest(resource="SecurityZone getAll", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(body_values, valid_attributes)
            # get_all the SecurityZone values with dic format
            LOG.info(_LI("get_all SecurityZone body is %(json)s"),
                     {"json": body_values})
            response = self.manager.get_securityZones(context, values)
            return response
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

    def show(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) > 1:
                raise BadRequest(resource="SecurityZone get", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            # ADETEC_COMMENT: 只参数id 就ok?
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'id']
            values = tools.validat_values(body_values, valid_attributes)
            # get the staticnat values with dic format
            LOG.info(_LI("get SecurityZone body is %(json)s"),
                     {"json": body_values})
            response = self.manager.get_securityZone(context, values)
            return response
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

    def addif(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) > 1:
                raise BadRequest(resource="SecurityZone add vlan", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'id',
                                'ifname']
            values = tools.validat_values(body_values, valid_attributes)
            # input the SecurityZone values with dic format
            LOG.info(_LI("delete SecurityZone body is %(json)s"),
                     {"json": body_values})
            response = self.manager.get_securityZone(context, values)
            if not isinstance(values["ifname"], string):
                raise ParamFormatError(param_name="ifname")
            if values["ifname"] in response.ifnames:
                message = ("securityZone with ifname=" +
                           values["ifname"] + " already exists")
                return tools.ret_info("400", message)
            response.ifnames.append(values["ifname"])
            values["ifnames"] = response.ifnames
            response = self.manager.update_securityZone(context, values)
            return response
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

    def delif(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) > 1:
                raise BadRequest(resource="SecurityZone del vlan", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'id',
                                'ifname']
            values = tools.validat_values(body_values, valid_attributes)
            # input the SecurityZone values with dic format
            LOG.info(_LI("delete SecurityZone body is %(json)s"),
                     {"json": body_values})
            response = self.manager.get_securityZone(context, values)
            if not isinstance(values["ifname"], string):
                raise ParamFormatError(param_name="ifname")
            if values["ifname"] not in response.ifnames:
                message = ("securityZone with ifname=" +
                           values["ifname"]+" don't exist!")
                return tools.ret_info("400", message)
            response.ifnames.remove(values["ifname"])
            values["ifnames"] = response.ifnames
            response = self.manager.update_securityZone(context, values)
            return response
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
