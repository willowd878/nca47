from nca47.common.i18n import _
from oslo_log import log as logging
from pecan import rest
from pecan import expose
from nca47.manager.central import CentralManager
from nca47.api.controllers.v1 import tools as tool
from nca47.common.exception import checkParam, checkBody
import pecan
LOG = logging.getLogger(__name__)


class CacheCleanController(rest.RestController):
    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(CacheCleanController, self).__init__()

    @expose('json')
    def post(self, *args, **kwargs):
        return self.clean_cache(*args, **kwargs)

    def clean_cache(self, *args, **kwargs):
        zones = None
        try:
            req = pecan.request
            json_str = req.body
            if json_str:
                context = req.context
                LOG.info(_("req is %(json)s, args is %(args)s,"
                           " kwargs is %(kwargs)s"),
                         {"json": json_str, "args": args, "kwargs": kwargs})
                dic = tool.valit_del_cache(json_str)
                zones = self.manager.del_cache(context, dic)
                LOG.info(_("Return of delete cache JSON is %(zones)s !"),
                         {"zones": zones})
            else:
                return tool.ret_info(checkBody.code, checkBody._msg_fmt)
        except checkParam:
                return tool.ret_info(checkParam.code, checkParam._msg_fmt)
        return zones
