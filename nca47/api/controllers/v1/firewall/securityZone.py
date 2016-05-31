from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1 import base
from nca47.common.i18n import _LI, _LE
from nca47.common.exception import Nca47Exception
from oslo_log import log
from nca47.api.controllers.v1 import tools
from nca47.manager.central import CentralManager
from nca47.common.exception import BadRequest
from oslo_messaging import RemoteError
from nca47.common import exception

LOG = log.getLogger(__name__)


class SecurityZoneController(base.BaseRestController):

    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(SecurityZoneController, self).__init__()

    def create(self, req, *args, **kwargs):
        try:
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'name', 'ifnames', 'priority', 'vfwname']
            values = tools.validat_values(body_values, valid_attributes)
            LOG.info(_LI("input the SecurityZone values with dic format"
                         " is %(json)s"), {"json": body_values})
            values["name"] = (values["tenant_id"] + "_" +
                              values["network_zone"] +
                              "_" + values["name"])
            response = self.manager.create_securityzone(context, values)
            return response
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)

    def remove(self, req, id, *args, **kwargs):
        try:
            context = req.context
            remove_dict = {}
            remove_dict.update(req.GET)
            valid_attributes = ['id', 'tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(remove_dict, valid_attributes)
            # input the SecurityZone values with dic format
            LOG.info(_LI("delete the SecurityZone values with dic format"
                         " is %(json)s"), {"json": remove_dict})
            self.manager.delete_securityzone(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", "success")

    def list(self, req, *args, **kwargs):
        try:
            context = req.context
            key_values = {}
            key_values.update(kwargs)
            valid_attributes = ['tenant_id', 'dc_name',
                                'network_zone', 'vfwname']
            values = tools.validat_values(key_values, valid_attributes)
            # get_all the SecurityZone values with dic format
            LOG.info(_LI("get_all the SecurityZone values with dic format"
                         " is %(json)s"), {"json": key_values})
            response = self.manager.get_securityzones(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", response)

    def show(self, req, id, *args, **kwargs):
        try:
            context = req.context
            response = self.manager.get_securityzone(context, id)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", response)

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
            LOG.info(_LI("input the SecurityZone values with dic format is"
                         " %(json)s"), {"json": body_values})
            response = self.manager.securityzone_addif(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", response)

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
            LOG.info(_LI("input the SecurityZone values with dic format"
                         " is %(json)s"), {"json": body_values})
            # response = self.manager.securityZone_addif(context, values)
            response = self.manager.securityzone_delif(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", response)
