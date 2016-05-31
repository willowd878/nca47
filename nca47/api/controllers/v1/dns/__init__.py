import pecan

from nca47.api.controllers.v1.dns import dns_records
from nca47.api.controllers.v1.dns import cache_clean
from nca47.api.controllers.v1.dns import dns_zones


class DNSController(object):
    def __init__(self):
        return

    @pecan.expose('json')
    def index(self):
        return {"Information": "The url is for DNS base RestApi "
                "interface"}

    @pecan.expose()
    def _lookup(self, kind, *remainder):
        if kind == 'record':
            return dns_records.DnsRecordsController(), remainder
        elif kind == 'zones':
            return dns_zones.DnsZonesController(), remainder
        elif kind == 'cache':
            return cache_clean.CacheCleanController(), remainder
        else:
            pecan.abort(404)
