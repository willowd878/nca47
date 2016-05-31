from nca47.common.i18n import _
from oslo_log import log as logging
from oslo_messaging import RemoteError
from pecan import rest
from pecan import expose
from nca47.manager.central import CentralManager
from nca47.api.controllers.v1 import tools as tool, tools
from oslo_serialization import jsonutils as json
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamFormatError
from nca47.common.exception import ParamNull
from nca47.common.i18n import _LE
from nca47.api.controllers.v1.tools import validat_values
from nca47.api.controllers.v1.tools import is_not_nil

import pecan
LOG = logging.getLogger(__name__)


class CacheCleanController(rest.RestController):
    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(CacheCleanController, self).__init__()

    @expose('json')
    def post(self, *args, **kwargs):
        return self.clean_cache(*args, **kwargs)

    """the method clean the cache"""
    def clean_cache(self, *args, **kwargs):
        list_ = ['owners', 'domain_name', 'view_name']
        req = pecan.request
        context = req.context
        try:
            # get the body
            values = json.loads(req.body)

            LOG.info(_("req is %(json)s, args is %(args)s,"
                       " kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            self.validat_parms(values, list_)
            caches = self.manager.del_cache(context, values)
            LOG.info(_("Return of delete cache JSON is %(zones)s !"),
                     {"zones": caches})
            return tools.ret_info("200", caches)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)

    def validat_parms(self, values, valid_keys):
        """The Check been the parameter is null or an array"""
        recom_msg = validat_values(values, valid_keys)
        for value in recom_msg:
            if value == "owners":
                if isinstance(values['owners'], list):
                    if not values['owners']:
                        raise ParamNull(param_name=value)
                else:
                    raise ParamFormatError(param_name=value)
            elif value == "domain_name":
                if not is_not_nil(values['domain_name']):
                    raise ParamNull(param_name=value)
            elif value == "view_name":
                if not is_not_nil(values['view_name']):
                    raise ParamNull(param_name=value)
        return recom_msg
