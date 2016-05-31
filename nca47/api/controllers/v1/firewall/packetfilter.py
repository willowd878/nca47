from oslo_log import log as logging
from oslo_serialization import jsonutils as json
from oslo_messaging import RemoteError
from nca47.api.controllers.v1 import tools
from nca47.api.controllers.v1 import base
from nca47.common.i18n import _LE
from nca47.common.exception import Nca47Exception
from nca47.common.exception import NonExistParam
from nca47.common.exception import ParamNull
from nca47.common.exception import ParamValueError
from nca47.manager import central

LOG = logging.getLogger(__name__)


class PacketFilterController(base.BaseRestController):

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(PacketFilterController, self).__init__()

    def create(self, req, *args, **kwargs):
        context = req.context
        try:
            body_values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'name', 'srczonename', 'dstzonename',
                                'vfwname']
            self.check_create(body_values, valid_attributes)
            values = self.check_value(body_values)
            packetfilter_info = self.manager.create_packetfilter(context,
                                                                 values)
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
        return tools.ret_info("200", packetfilter_info)

    def remove(self, req, id, *args, **kwargs):
        context = req.context
        try:
            key_values = {}
            key_values.update(kwargs)
            key_values['id'] = id
            valid_attributes = ['id', 'tenant_id', 'dc_name', 'network_zone']
            values = tools.validat_values(key_values, valid_attributes)
            self.manager.delete_packetfilter(context, values)
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
        return tools.ret_info('200', 'success')

    def list(self, req, *args, **kwargs):
        context = req.context
        try:
            key_values = {}
            key_values.update(kwargs)
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'vfwname']
            values = tools.validat_values(key_values, valid_attributes)
            packetfilter_infos = self.manager.get_all_packetfilters(context,
                                                                    values)
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
        return tools.ret_info("200", packetfilter_infos)

    def show(self, req, id, *args, **kwargs):
        context = req.context
        try:
            packetfilter_info = self.manager.get_packetfilter(context, id)
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
        return tools.ret_info("200", packetfilter_info)

    def check_value(self, values):
        if 'srcipobjips' in values.keys() and isinstance(
                values['srcipobjips'], list):
            for ipinfo in values['srcipobjips']:
                if not tools._is_valid_ipv4_addr(ipinfo):
                    raise ParamValueError(param_name=ipinfo)
            values['srcipobjips'] = values['srcipobjips']
        if 'dstipobjips' in values.keys() and isinstance(
                values['srcipobjips'], list):
            for ipinfo in values['dstipobjips']:
                if not tools._is_valid_ipv4_addr(ipinfo):
                    raise ParamValueError(param_name=ipinfo)
            values['dstipobjips'] = values['dstipobjips']
        if 'servicenames' in values.keys():
            values['servicenames'] = values['servicenames']
        else:
            values['servicenames'] = []
        valid_range = (0, 1)
        if 'action' in values.keys():
            if values['action'] not in valid_range:
                raise ParamValueError(param_name='action')
            values['action'] = values['action']
        else:
            values['action'] = 0
        if 'log' in values.keys():
            if values['log'] not in valid_range:
                raise ParamValueError(param_name='log')
            values['log'] = values['log']
        else:
            values['log'] = 0
        if "srczonename" in values.keys():
            values["srczonename"] = (values["tenant_id"] + "_" +
                                     values["network_zone"] +
                                     "_" + values["srczonename"])
        if "dstzonename" in values.keys():
            values["dstzonename"] = (values["tenant_id"] + "_" +
                                     values["network_zone"] +
                                     "_" + values["dstzonename"])
        return values

    def check_create(self, values, valid_keys):
        for key in valid_keys:
            if key not in values.keys():
                raise NonExistParam(param_name=key)
            else:
                if isinstance(values[key], basestring):
                    if (values[key].isspace()) or (len(values[key]) == 0):
                        raise ParamNull(param_name=key)
                elif isinstance(values[key], list):
                    if len(values[key]) == 0:
                        raise ParamNull(param_name=key)
