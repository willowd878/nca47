from oslo_log import log as logging
from nca47.common.exception import NonExistParam
from nca47.common.exception import ParamNull
from nca47.common.exception import ParamValueError
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.manager import central
from oslo_messaging import RemoteError
from nca47.common.exception import Nca47Exception
from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1 import tools
from nca47.api.controllers.v1 import base

LOG = logging.getLogger(__name__)


class SnatAddrPoolController(base.BaseRestController):

    """
    nca47 snataddrpool class, using for add/delete/query/queryallname the
    snataddrpool info, validate parameters whether is legal, handling DB
    operations and calling rpc client's corresponding method to send
    messaging to agent endpoints
    """

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(SnatAddrPoolController, self).__init__()

    def create(self, req, *args, **kwargs):
        """create the snataddrpool"""
        try:
            # get the body
            json_body = req.body
            # get the context
            context = req.context
            values = json.loads(json_body)
            # check the in values
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone', 'name',
                                'ipstart', 'ipend', 'slotip', 'vfwname']
            # check the in values
            recom_msg = self.validat_values(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server create the snataddrpool in db and device
            snataddrpool = self.manager.add_snataddrpool(context, recom_msg)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", snataddrpool)

    def remove(self, req, id, *args, **kwargs):
        """del the snataddrpool"""
        try:
            # get the context
            context = req.context
            # check the in values
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'vfwname', 'id']
            key_values = {}
            key_values.update(kwargs)
            key_values['id'] = id
            # check the in values
            recom_msg = self.validat_values(key_values, valid_attributes)
            # from rpc server delete the snataddrpool in db and device
            self.manager.del_snataddrpool(context, recom_msg)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
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

    def show(self, req, id, *args, **kwargs):
        """get the one snataddrpool"""
        try:
            # get the context
            context = req.context
            snataddrpool = self.manager.get_snataddrpool(context, id)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", snataddrpool)

    def list(self, req, *args, **kwargs):
        """get the all snataddrpool"""
        try:
            # get the context
            context = req.context
            # check the in values
            key_values = {}
            key_values.update(kwargs)
            valid_attributes = ['vfwname', 'tenant_id', 'dc_name',
                                'network_zone']
            # check the in values
            recom_msg = self.validat_values(key_values, valid_attributes)
            # from rpc server get the snataddrpool in db and device
            snataddrpools = self.manager.get_snataddrpools(context, recom_msg)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", snataddrpools)

    def validat_values(self, values, valid_keys):
        """Non null input parameters"""
        recom_msg = {}
        for key in valid_keys:
            if key == 'ipstart':
                if not tools._is_valid_ipv4_addr(values[key]):
                    raise ParamValueError(param_name=key)
            if key == 'ipend':
                if not tools._is_valid_ipv4_addr(values[key]):
                    raise ParamValueError(param_name=key)
            if key == 'slotip':
                if not tools._is_valid_slotip(values[key]):
                    raise ParamValueError(param_name=key)
            if key not in values.keys():
                raise NonExistParam(param_name=key)
            else:
                recom_msg[key] = values[key]
            if values[key] is None:
                raise ParamNull(param_name=key)
        return recom_msg
