from oslo_log import log as logging

from nca47.api.controllers.v1 import base
from nca47.common.i18n import _

LOG = logging.getLogger(__name__)


class DnsServersController(base.BaseRestController):
    def _post(self, req, server, *args, **kwargs):
        LOG.debug(
            _("server is %(server)s, args is %(args)s, kwargs is %(kwargs)s"),
            {"server": server, "args": args, "kwargs": kwargs})
        return None

    def _put(self, req, id, *args, **kwargs):
        return None
