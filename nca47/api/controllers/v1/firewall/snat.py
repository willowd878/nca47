from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1 import base
from nca47.common.i18n import _LI, _LE
from nca47.common.exception import Nca47Exception
from oslo_log import log
from nca47.api.controllers.v1 import tools
from nca47.manager.central import CentralManager
from oslo_messaging import RemoteError

LOG = log.getLogger(__name__)


class SNATController(base.BaseRestController):
    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(SNATController, self).__init__()

    def create(self, req, *args, **kwargs):
        try:
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'name', 'outIfName', 'vfwname']
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
            LOG.info(_LI("input the snat values with dic format"
                         " is %(json)s"), {"json": body_values})
            response = self.manager.create_snat(context, values)
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

    def remove(self, req, id, *args, **kwargs):
        try:
            context = req.context
            key_values = {}
            key_values.update(kwargs)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(key_values, valid_attributes)
            values["id"] = id
            # input the snat values with dic format
            LOG.info(_LI("delete the snat values with dic format"
                         " is %(json)s"), {"json": key_values})
            self.manager.del_snat(context, values)
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
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(key_values, valid_attributes)
            # input the staticnat values with dic format
            LOG.info(_LI("get_all the snat values with dic format"
                         " is %(json)s"), {"json": key_values})
            response = self.manager.get_snats_by_fuzzy_query(context, values)
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
            response = self.manager.get_snats(context, id)
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
