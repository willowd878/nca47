from nca47.common.i18n import _
from oslo_log import log as logging
from pecan import rest
from pecan import expose
from nca47.manager.central import CentralManager
from nca47.api.controllers.v1 import tools as tool
from oslo_serialization import jsonutils as json
from nca47.common.exception import Nca47Exception
from nca47.common.i18n import _LE
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
        list_ = ['owners', 'domain_name', 'view_name', 'current_user']
        req = pecan.request
        context = req.context
        try:
            # get the body
            values = json.loads(req.body)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)

        LOG.info(_("req is %(json)s, args is %(args)s,"
                   " kwargs is %(kwargs)s"),
                 {"json": req.body, "args": args, "kwargs": kwargs})
        tool.validat_parms(values, list_)
        zones = self.manager.del_cache(context, values)
        LOG.info(_("Return of delete cache JSON is %(zones)s !"),
                 {"zones": zones})
        return zones
