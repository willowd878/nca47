from oslo_log import log as logging

from nca47.api.controllers.v1 import base
from nca47.common.i18n import _
from nca47.db import api as db_api

LOG = logging.getLogger(__name__)


class DnsServersController(base.BaseRestController):
    def __init__(self):
        self.db_api = db_api.get_instance()
        super(DnsServersController, self).__init__()

    def _post(self, req, server, *args, **kwargs):
        LOG.debug(
            _("server is %(server)s, args is %(args)s, kwargs is %(kwargs)s"),
            {"server": server, "args": args, "kwargs": kwargs})
        dns_server = self.db_api.create_dns_server(server)
        return dns_server

    def _put(self, req, id, *args, **kwargs):
        values = kwargs['server']
        self.db_api.update_dns_server(id, values)

    def _delete(self, req, id, *args, **kwargs):
        self.db_api.delete_dns_server(id)

    def _get_all(self, req, *args, **kwargs):
        dns_servers = self.db_api.list_dns_servers()
        return {'servers': dns_servers}

    def _get_one(self, req, id, *args, **kwargs):
        dns_server = self.db_api.get_dns_server(id)
        return {'server': dns_server}
