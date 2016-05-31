from nca47.api.controllers.v1 import base
from nca47.common.i18n import _

from nca47.api.controllers.v1.lb import rwlb

import pecan


class LBController(object):
    def __init__(self):
        return

    @pecan.expose('json')
    def index(self):
        return {"Information": "The url is for lb base RestApi "
                "interface"}

    @pecan.expose()
    def _lookup(self, kind, *remainder):
        if kind == 'business':
            return rwlb.RDLBController(), remainder
        else:
            pecan.abort(404)
