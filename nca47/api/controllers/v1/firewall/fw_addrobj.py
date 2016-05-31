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


class AddrObjController(base.BaseRestController):
    """
    nca47 addrobj class, using for add/delete/update/query the addrobj info,
    validate parameters whether is legal, handling DB operations and calling
    rpc client's corresponding method to send messaging to agent endpoints
    """

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(AddrObjController, self).__init__()

    def create(self, req, *args, **kwargs):
        """create the addrobj"""
        try:
            # get the body
            json_body = req.body
            # get the context
            context = req.context
            values = json.loads(json_body)
            # check the in values
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'ip', 'name', 'vfwname']
            # check the in values
            recom_msg = self.validat_values(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server create the addrobj in db and device
            addrobj = self.manager.add_addrobj(context, recom_msg)
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
        return tools.ret_info("200", addrobj)

    def remove(self, req, id, *args, **kwargs):
        """del the addrobj"""
        try:
            # get the context
            context = req.context
            # check the in values
            valid_attributes = ['tenant_id', 'dc_name', 'network_zone',
                                'vfwname', 'id']
            # check the in values
            key_values = {}
            key_values.update(kwargs)
            key_values['id'] = id
            recom_msg = self.validat_values(key_values, valid_attributes)
            # from rpc server delete the addrobj in db and device
            self.manager.delete_addrobj(context, recom_msg)
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
        return tools.ret_info('200', 'success')

    def show(self, req, id, *args, **kwargs):
        """get the one addrobj"""
        try:
            # get the context
            context = req.context
            addrobj = self.manager.get_addrobj(context, id)
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
        return tools.ret_info("200", addrobj)

    def list(self, req, *args, **kwargs):
        """get the all addrobj"""
        try:
            # get the context
            context = req.context
            # check the in values
            # ADTEC_request:  should be vfwname, not vfw_id
            valid_attributes = ['vfwname', 'tenant_id', 'dc_name',
                                'network_zone']
            # check the in values
            key_values = {}
            key_values.update(kwargs)
            recom_msg = self.validat_values(key_values, valid_attributes)
            # from rpc server get the addrobj in db and device
            addrobjs = self.manager.get_addrobjs(context, recom_msg)
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
        return tools.ret_info("200", addrobjs)

    def validat_values(self, values, valid_keys):
        """Non null input parameters"""
        recom_msg = {}
        for key in valid_keys:
            # check the IP get
            if key == 'ip':
                if not tools._is_valid_ipv4_addr(values[key]):
                    raise ParamValueError(param_name=key)
            # if key == 'expip':
            #     if tools.is_valid_ip_list_with_netmask(values[key]) == False:
            #         raise ParamValueError(param_name=key)
            if key not in values.keys():
                raise NonExistParam(param_name=key)
            else:
                recom_msg[key] = values[key]
            if values[key] is None:
                raise ParamNull(param_name=key)
        return recom_msg
