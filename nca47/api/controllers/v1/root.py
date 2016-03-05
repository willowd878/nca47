import pecan

from nca47.api.controllers.v1 import dns_zones


class V1Controller(object):
    def __init__(self):
        return

    @pecan.expose('json')
    def index(self):
        return {"key": "value"}

    @pecan.expose()
    def _lookup(self, kind, *remainder):
        if kind == 'dns_zones':
            return dns_zones.DnsZones(), remainder
        else:
            pecan.abort(404)
