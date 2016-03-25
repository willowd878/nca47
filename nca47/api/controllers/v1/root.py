import pecan

from nca47.api.controllers.v1 import dns_records, cache_clean
from nca47.api.controllers.v1 import dns_zones
from nca47.api.controllers.v1 import dns_servers


class V1Controller(object):
    def __init__(self):
        return

    @pecan.expose('json')
    def index(self):
        return {"key": "value"}

    @pecan.expose()
    def _lookup(self, kind, *remainder):
        if kind == 'record':
            return dns_records.DnsRecordsController(), remainder
        elif kind == 'zones':
            return dns_zones.DnsZones(), remainder
        elif kind == 'cache':
            return cache_clean.CacheCleanController(), remainder
        elif kind == "dns_servers":
            return dns_servers.DnsServersController(), remainder
        else:
            pecan.abort(404)
