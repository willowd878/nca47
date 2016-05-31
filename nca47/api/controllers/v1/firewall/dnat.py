from oslo_log import log as logging
from oslo_serialization import jsonutils as json
from oslo_messaging import RemoteError

from nca47.api.controllers.v1 import tools
from nca47.api.controllers.v1 import base
from nca47.common.i18n import _LE
from nca47.manager import central
from nca47.common.exception import BadRequest
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamValueError
from nca47.common.i18n import _LI

LOG = logging.getLogger(__name__)


class DnatController(base.BaseRestController):
    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(DnatController, self).__init__()

    def create(self, req, *args, **kwargs):
        context = req.context
        try:
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'name', 'inifname', 'wanip', 'lanipstart',
                                'lanipend', 'lanport', 'slot', 'vfwname']
            values = tools.validat_values(body_values, valid_attributes)
            keys = body_values.keys()
            if not tools._is_valid_ipv4_addr(values['wanip']):
                raise ParamValueError(param_name='wanip')
            if not tools._is_valid_ipv4_addr(values['lanipstart']):
                raise ParamValueError(param_name='lanipstart')
            if not tools._is_valid_ipv4_addr(values['lanipend']):
                raise ParamValueError(param_name='lanipend')
            if values['lanport'] != "0":
                if not tools._is_valid_port(values['lanport']):
                    raise ParamValueError(param_name='lanport')
                if 'wantcpports' in keys and 'wanudpports' in keys:
                    raise BadRequest(resource="dnat", msg="Only have one"
                                     " between wantcpports and wanudpport")
            if 'wantcpports' in keys:
                for port_range in body_values['wantcpports']:
                    if not tools._is_valid_port_range(port_range):
                        raise BadRequest(resource="wantcpports",
                                         msg=port_range)
                values['wantcpports'] = body_values['wantcpports']
            if 'wanudpports' in keys:
                for port_range in body_values['wanudpports']:
                    if not tools._is_valid_port_range(port_range):
                        raise BadRequest(resource="wantcpports",
                                         msg=port_range)
                values['wanudpports'] = body_values['wanudpports']
            dnat_info = self.manager.create_dnat(context, values)
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
        return tools.ret_info("200", dnat_info)

    def remove(self, req, id, *args, **kwargs):
        context = req.context
        try:
            key_values = {}
            key_values.update(kwargs)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(key_values, valid_attributes)
            values["id"] = id
            self.manager.delete_dnat(context, values)
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
        context = req.context
        try:
            key_values = {}
            key_values.update(kwargs)
            LOG.info(_LI("get_all the staticnat values with dic format"
                         " is %(json)s"), {"json": key_values})
            list_ = ['tenant_id', 'dc_name', 'network_zone']
            tools.validat_values(key_values, list_)
            dnat_infos = self.manager.get_dnats_by_fuzzy_query(context,
                                                               key_values)
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
        return tools.ret_info("200", dnat_infos)

    def show(self, req, id, *args, **kwargs):
        context = req.context
        try:
            dnat_info = self.manager.get_dnat(context, id)
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
        return tools.ret_info("200", dnat_info)
