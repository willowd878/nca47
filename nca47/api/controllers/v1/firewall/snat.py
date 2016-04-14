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


class SNATController(fw_base.BaseRestController):
    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(SNATController, self).__init__()

    def create(self, req, *args, **kwargs):
        try:
            url = req.url
            if len(args) > 1:
                raise BadRequest(resource="SNAT create", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'name',
                                'outIfName']
            values = tools.validat_values(body_values, valid_attributes)
            values["outifname"] = body_values["outIfName"]

            if "srcIpObjIP" not in body_values.keys():
                values["srcipobjname"] = ["all"]
            else:
                values["srcipobjname"] = body_values["srcIpObjIP"]

            if "dstIpObjIP" not in body_values.keys():
                values["dstipobjname"] = ["all"]
            else:
                values["dstipobjname"] = body_values["dstIpObjIP"]

            if "wanIpPoolIP" not in body_values.keys():
                values["wanippoolname"] = ""
            else:
                values["wanippoolname"] = body_values["wanIpPoolIP"]
        # input the staticnat values with dic format
            LOG.info(_LI("input add_snat body is %(json)s"),
                     {"json": body_values})
            response = self.manager.create_snat(context, values)
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
                raise BadRequest(resource="SNAT del", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'id']
            values = tools.validat_values(body_values, valid_attributes)
        # input the snat values with dic format
            LOG.info(_LI("delete Staticnat body is %(json)s"),
                     {"json": body_values})
            response = self.manager.del_snat(context, values)
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
                raise BadRequest(resource="SNAT getAll", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(body_values, valid_attributes)
        # input the staticnat values with dic format
            LOG.info(_LI("get_all snat body is %(json)s"),
                     {"json": body_values})
            response = self.manager.get_snats(context, values)
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
                raise BadRequest(resource="SNAT get", msg=url)
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'id']
            values = tools.validat_values(body_values, valid_attributes)
        # input the snat values with dic format
            LOG.info(_LI("get snat body is %(json)s"),
                     {"json": body_values})
            response = self.manager.get_snats(context, values)
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
