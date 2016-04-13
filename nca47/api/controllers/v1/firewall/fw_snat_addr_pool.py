from oslo_log import log as logging
from nca47.common.exception import NonExistParam, ParamNull, ParamValueError
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.manager import central
from oslo_messaging.exceptions import MessagingException
from nca47.common.exception import BadRequest
from nca47.common.exception import Nca47Exception
from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1 import tools
from nca47.api.controllers.v1.firewall import fw_base

LOG = logging.getLogger(__name__)


class SnatAddrPoolController(fw_base.BaseRestController):

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
        url = req.url
        try:
            # get the right url
            if len(args) != 1:
                raise BadRequest(resource="AddrPool operation", msg=url)
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
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
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
        return snataddrpool

    def remove(self, req, *args, **kwargs):
        """del the snataddrpool"""
        url = req.url
        try:
            # get the right url
            if len(args) != 1:
                raise BadRequest(resource="AddrPool operation", msg=url)
            # get the body
            json_body = req.body
            # get the context
            context = req.context
            values = json.loads(json_body)
            # check the in values
            valid_attributes = ['tenant_id', 'dc_name', 'id', 'network_zone',
                                'vfwname']
            # check the in values
            recom_msg = self.validat_values(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server delete the snataddrpool in db and device
            snataddrpool = self.manager.del_snataddrpool(context, recom_msg)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
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
        return snataddrpool

    def show(self, req, *args, **kwargs):
        """get the one snataddrpool"""
        url = req.url
        try:
            # get the right url
            if len(args) != 1:
                raise BadRequest(resource="AddrPool operation", msg=url)
            # get the body
            json_body = req.body
            # get the context
            context = req.context
            values = json.loads(json_body)
            # check the in values
            valid_attributes = ['id']
            # check the in values
            recom_msg = self.validat_values(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server get the snataddrpool in db and device
            snataddrpool = self.manager.get_snataddrpool(context, recom_msg)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
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
        return snataddrpool

    def list(self, req, *args, **kwargs):
        """get the all snataddrpool"""
        url = req.url
        try:
            # get the right url
            if len(args) != 1:
                raise BadRequest(resource="AddrPool operation", msg=url)
            # get the body
            json_body = req.body
            # get the context
            context = req.context
            values = json.loads(json_body)
            # check the in values
            valid_attributes = ['vfwname', 'tenant_id', 'dc_name',
                                'network_zone']
            # check the in values
            recom_msg = self.validat_values(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server get the snataddrpool in db and device
            snataddrpools = self.manager.get_snataddrpools(context, recom_msg)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
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
        return snataddrpools

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
