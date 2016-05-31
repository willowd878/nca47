"""
This module is for operate gslb's functions, such as CRUD the related
resource via RestAPI interface.
"""
import pecan
from nca47.api.controllers.v1 import base
from nca47.api.controllers.v1.gslb.gmap import GMapController
from nca47.api.controllers.v1.gslb.gmember import GmemberController
from nca47.api.controllers.v1.gslb.gpool import GPoolController
from nca47.api.controllers.v1.gslb.gslb_zone import GlsbZoneController
from nca47.api.controllers.v1.gslb.hm_template import HmTemplateController
from nca47.api.controllers.v1.gslb.sp_policy import SP_PolicyController
from nca47.api.controllers.v1.gslb.syncgroup import SyngroupController
from nca47.api.controllers.v1.gslb.user_region_member import \
    RegionMemberController
from nca47.api.controllers.v1.gslb.user_region import RegionController
from nca47.common.i18n import _


class GSLBController(object):
    """Global Server Load Balance's base restApi interface"""

    def __init__(self):
        return

    @pecan.expose('json')
    def index(self):
        return {"Information": "The url is for GSLB base RestApi "
                "interface"}

    @pecan.expose()
    def _lookup(self, kind, *remainder):
        if kind == "sp_policy":
            return SP_PolicyController(), remainder
        elif kind == "member":
            return RegionMemberController(), remainder
        elif kind == "region":
            return RegionController(), remainder
        elif kind == "gmember":
            return GmemberController(), remainder
        elif kind == "hm_template":
            return HmTemplateController(), remainder
        elif kind == "gslb_zone":
            return GlsbZoneController(), remainder
        elif kind == 'syngroup':
            return SyngroupController(), remainder
        elif kind == "gpool":
            return GPoolController(), remainder
        elif kind == "gmap":
            return GMapController(), remainder
        else:
            pecan.abort(404)
