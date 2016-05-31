from nca47.api.controllers.v1 import base
from nca47.common.i18n import _

from nca47.api.controllers.v1.firewall import dnat
from nca47.api.controllers.v1.firewall import packetfilter
from nca47.api.controllers.v1.firewall import vfw
from nca47.api.controllers.v1.firewall import vlan
from nca47.api.controllers.v1.firewall import fw_addrobj
from nca47.api.controllers.v1.firewall import fw_snat_addr_pool
from nca47.api.controllers.v1.firewall import vrf
from nca47.api.controllers.v1.firewall import snat
from nca47.api.controllers.v1.firewall import staticnat
from nca47.api.controllers.v1.firewall import securityZone
from nca47.api.controllers.v1.firewall import net_service
import pecan


class FirewallController(object):
    def __init__(self):
        return

    @pecan.expose('json')
    def index(self):
        return {"Information": "The url is for firewall base RestApi "
                "interface"}

    @pecan.expose()
    def _lookup(self, kind, *remainder):
        if kind == 'vfw':
            return vfw.VFWController(), remainder
        elif kind == 'dnat':
            return dnat.DnatController(), remainder
        elif kind == 'packetfilter':
            return packetfilter.PacketFilterController(), remainder
        elif kind == 'vlan':
            return vlan.VLANController(), remainder
        elif kind == 'addrobj':
            return fw_addrobj.AddrObjController(), remainder
        elif kind == 'snataddrpool':
            return fw_snat_addr_pool.SnatAddrPoolController(), remainder
        elif kind == 'vrf':
            return vrf.VRFController(), remainder
        elif kind == 'snat':
            return snat.SNATController(), remainder
        elif kind == 'staticnat':
            return staticnat.StaticnatController(), remainder
        elif kind == 'securityzone':
            return securityZone.SecurityZoneController(), remainder
        elif kind == 'netservice':
            return net_service.NetServiceController(), remainder
        else:
            pecan.abort(404)
