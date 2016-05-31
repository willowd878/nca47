from oslo_log import log as logging
from oslo_messaging import RemoteError
from nca47.api.controllers.v1 import base
from nca47.api.controllers.v1 import tools
from nca47.common.exception import ParamFormatError
from nca47.common.exception import ParamValueError
from nca47.common.exception import Nca47Exception
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.manager import central
from oslo_serialization import jsonutils as json

LOG = logging.getLogger(__name__)


class SP_PolicyController(base.BaseRestController):

    """
    nca47 sp_policy api class, using for add/delete/update/query the sp_poliy
    info, validate parameters whether is legal, handling DB operations and
    calling rpc client's corresponding method to send messaging to agent
    endpoints
    """

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(SP_PolicyController, self).__init__()

    def create(self, req, *args, **kwargs):
        """create one sp_policy(static_proximity policy)"""
        # get the context
        context = req.context
        try:
            values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'priority', 'src_type',
                                'src_logic', 'src_data1', 'dst_type',
                                'dst_logic', 'dst_data1']
            # check the in values
            recom_msg = self.validat_parms(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server create the proximitys in db and device
            proximitys = self.manager.create_sp_policy(context, recom_msg)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as e:
            self.response.status = 500
            message = e.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', proximitys)

    def update(self, req, id, *args, **kwargs):
        """update the target sp_policy"""
        # get the context
        context = req.context
        try:
            # get the body
            values = json.loads(req.body)
            values['id'] = id
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # check the in values
            valid_attributes = ['new_priority', 'tenant_id', 'id']
            recom_msg = self.validat_parms(values, valid_attributes)
            # from rpc server update the proximitys in db and device
            proximitys = self.manager.update_sp_policy(context, recom_msg,
                                                       recom_msg['id'])
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', proximitys)

    def remove(self, req, id, *args, **kwargs):
        """delete the target static proximitys policy"""
        # get the context
        context = req.context
        try:
            # get the body
            values = {}
            values.update(kwargs)
            values['id'] = id
            valid_attributes = ['tenant_id', 'id']
            # check the in values
            recom_msg = self.validat_parms(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server delete the proximitys in db and device
            self.manager.delete_sp_policy(context, recom_msg['id'])
        except Nca47Exception as e:
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', "success")

    def list(self, req, *args, **kwargs):
        """get all of the required sp_policy"""
        # get the context
        context = req.context
        try:
            # get the body
            values = {}
            values.update(req.GET)
            LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
            # from rpc server get the proximitys in device
            proximitys = self.manager.get_db_proximitys(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', proximitys)

    def show(self, req, id, *args, **kwargs):
        """get the target sp_policy info"""
        # get the context
        context = req.context
        try:
            LOG.info(_(" args is %(args)s"), {"args": args})
            # from rpc server get the proximity in device
            proximitys = self.manager.get_sp_policy(context, id)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', proximitys)

    def validat_parms(self, values, valid_keys):
        """check the in value is null and nums"""
        recom_msg = tools.validat_values(values, valid_keys)
        for value in recom_msg:
            if value == "src_logic":
                if not ((values['src_logic'] == "0") or
                        (values['src_logic'] == "1")):
                    raise ParamValueError(param_name=value)
            elif value == "dst_logic":
                if not ((values['dst_logic'] == "0") or
                        (values['dst_logic'] == "1")):
                    raise ParamValueError(param_name=value)
            elif value == "priority":
                try:
                    int_priority = int(values['priority'])
                except Exception:
                    raise ParamFormatError(param_name=value)
                if (int_priority < 1) or (int_priority > 65535):
                    raise ParamValueError(param_name=value)
            elif value == "src_type":
                src_type_array = ['ip_subnet', 'region', 'ISP', 'country',
                                  'province']
                if values['src_type'] not in src_type_array:
                    raise ParamValueError(param_name=value)
                if values['src_type'] == "ip_subnet":
                    ser_str = '/'
                    try:
                        values['src_data1'].index(ser_str)
                    except Exception:
                        raise ParamFormatError(param_name="src_data1")
            elif value == "dst_type":
                dst_type_array = ['ip_subnet', 'region', 'ISP', 'country',
                                  'province']
                if values['dst_type'] not in dst_type_array:
                    raise ParamValueError(param_name=value)
                if values['dst_type'] == "ip_subnet":
                    ser_str = '/'
                    try:
                        values['dst_data1'].index(ser_str)
                    except Exception:
                        raise ParamFormatError(param_name="dst_data1")
        return recom_msg
