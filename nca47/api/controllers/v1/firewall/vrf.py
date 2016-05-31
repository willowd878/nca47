from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1 import base
from nca47.common.i18n import _LI, _LE
from nca47.common.exception import Nca47Exception
from oslo_log import log
from nca47.api.controllers.v1 import tools
from nca47.manager.central import CentralManager
from oslo_messaging import RemoteError

LOG = log.getLogger(__name__)


class VRFController(base.BaseRestController):
    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(VRFController, self).__init__()

    def create(self, req, *args, **kwargs):
        try:
            context = req.context
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'name',
                                'vrfInterface']
            values = tools.validat_values(body_values, valid_attributes)
            # input the staticnat values with dic format
            LOG.info(_LI("input the vrf values with dic format"
                         " is %(json)s"), {"json": body_values})
            response = self.manager.create_vrf(context, values)
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
        try:
            context = req.context
            key_values = {}
            key_values.update(kwargs)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'id']
            values = tools.validat_values(key_values, valid_attributes)
            # input the vrf values with dic format
            LOG.info(_LI("delete the vrf values with dic format"
                         " is %(json)s"), {"json": key_values})
            self.manager.del_vrf(context, values)
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

    def list(self, req, *args, **kwargs):
        try:
            context = req.context
            key_values = {}
            key_values.update(kwargs)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(key_values, valid_attributes)
            # input the staticnat values with dic format
            LOG.info(_LI("get_all the vrf values with dic format"
                         " is %(json)s"), {"json": key_values})
            response = self.manager.get_vrfs(context, values)
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

    def show(self, req, id, *args, **kwargs):
        try:
            context = req.context
            response = self.manager.get_vrf(context, id)
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
