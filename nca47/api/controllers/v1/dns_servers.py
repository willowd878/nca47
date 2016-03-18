from oslo_log import log as logging
from oslo_serialization import jsonutils as json
from nca47.api.controllers.v1 import base
from nca47.common.i18n import _
from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import DnsServer
from nca47.manager import rpcapi

LOG = logging.getLogger(__name__)


class DnsServersController(base.BaseRestController):
    def __init__(self):
        self.db_api = db_api.get_instance()
        
        self.rpcapi = rpcapi.DNSManagerAPI.get_instance()
        super(DnsServersController, self).__init__()

    def create(self, req, *args, **kwargs):
        LOG.debug(
            _("server is %(server)s, args is %(args)s, kwargs is %(kwargs)s"),
            {"server": 'server', "args": args, "kwargs": kwargs})

        dns_server = self.db_api.create(DnsServer, json.loads(req.body))
        return dns_server

    def _put(self, req, id, *args, **kwargs):
        values = kwargs['server']
        return self.db_api.update_object(DnsServer, id, values)

    def _delete(self, req, id, *args, **kwargs):
        self.db_api.delete_object(DnsServer, id=id)

    def _get_all(self, req, *args, **kwargs):
        dns_servers = self.db_api.get_objects(DnsServer, **kwargs)
        return {'servers': dns_servers}

    def _get_one(self, req, id, *args, **kwargs):
        dns_server = self.db_api.get_object(DnsServer, id=id, **kwargs)
        return {'server': dns_server}
