from oslo_log import log as logging
from oslo_serialization import jsonutils as json
from oslo_messaging import RemoteError
from nca47.api.controllers.v1 import base
from nca47.common.i18n import _LE
from nca47.common.i18n import _LI
from nca47.manager import central
from nca47.api.controllers.v1 import tools
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamValueError

LOG = logging.getLogger(__name__)


class VFWController(base.BaseRestController):
    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(VFWController, self).__init__()

    def create(self, req, *args, **kwargs):
        LOG.info("create vfw")
        context = req.context
        valid_attributes = ['name', 'type', 'resource', 'tenant_id',
                            'dc_name', 'network_zone',
                            'network_zone_class']
        try:
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
        return tools.ret_info("200", vfw_info)

    def remove(self, req, id, *args, **kwargs):
        LOG.info("delete vfw")
        context = req.context
        try:
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone']
            key_values = {}
            key_values.update(kwargs)
            values = tools.validat_values(key_values, valid_attributes)
            values["id"] = id
            self.manager.delete_vfw(context, values)
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
        LOG.info(_LI("vfw list method"))
        context = req.context
        try:
            # valid_attributes = ['tenant_id', 'dc_name', \
            # 'network_zone']
            # key_values = {}
            # key_values.update(kwargs)
            # values = tools.validat_values(key_values, valid_attributes)
            # if 'protection_class' in key_values.keys():
                # values['protection_class'] = key_values['protection_class']
            dic = {}
            dic.update(kwargs)
            list_ = ['tenant_id', 'dc_name', 'network_zone']
            tools.validat_values(dic, list_)
            vfw_info = self.manager.get_vfws_by_fuzzy_query(context, dic)
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
        return tools.ret_info("200", vfw_info)

    def show(self, req, id, *args, **kwargs):
        context = req.context
        try:
            vfw_info = self.manager.get_vfw(context, id)
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
        return tools.ret_info("200", vfw_info)
