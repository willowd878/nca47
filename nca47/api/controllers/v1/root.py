import pecan

from nca47.api.controllers.v1 import firewall
from nca47.api.controllers.v1 import dns
from nca47.api.controllers.v1 import routerSwitch
from nca47.api.controllers.v1.agent import agent
from nca47.api.controllers.v1 import lb
from nca47.api.controllers.v1 import gslb


class V1Controller(object):
    def __init__(self):
        return

    @pecan.expose('json')
    def index(self):
        return {"key": "value"}

    @pecan.expose()
    def _lookup(self, kind, *remainder):
        if kind == 'dns':
            return dns.DNSController(), remainder
        elif kind == "firewall":
            return firewall.FirewallController(), remainder
        elif kind == "routerswitch":
            return routerSwitch.RouterSwitchController(), remainder
        elif kind == "agent":
            return agent.AgentController(), remainder
        elif kind == "lb":
            return lb.LBController(), remainder
        elif kind == "gslb":
            return gslb.GSLBController(), remainder
        else:
            pecan.abort(404)
