from oslo_log import log as logging

from nca47.api.controllers.v1 import base
from nca47.api.controllers.v1 import tools
from nca47.common.exception import checkParam
from nca47.common.i18n import _
from nca47.manager import central
from nca47 import objects
from oslo_serialization import jsonutils as json

LOG = logging.getLogger(__name__)


class DnsZones(base.BaseRestController):
    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(DnsZones, self).__init__()

    def create(self, req, *args, **kwargs):
        """get the body"""
        context = req.context
        """check the in values"""
        valid_attributes = ['name', 'owners', 'default_ttl', 'renewal',
                            'current_user']
        try:
            """check the in values nums"""
            values = tools.load_values(req, valid_attributes)
            LOG.info(_("body is %(body)s"), {"body": values})
            """check the renewal value is yes or no"""
            tools.validat_renewal(values)
            target_values = self.make_dns_zone_object(values)
            dns_zone = objects.DnsZone(context, **target_values)
            """from rpc server create the zones"""
            zones = self.manager.create_zone(context, dns_zone)
            LOG.info(_("zones is %(zones)s"), {"zones": zones})
        except checkParam:
            """return the wrong message"""
            return tools.ret_info(checkParam.code, checkParam._msg_fmt)
        return zones

    def update(self, req, *args, **kwargs):
        print args
        if len(args) == 2:
            if args[1] == "owners":
                """get the body"""
                context = req.context
                """check the in values"""
                valid_attributes = ['owners', 'current_user']
                try:
                    """check the in values nums"""
                    values = tools.load_values(req, valid_attributes)
                    """trying to rpc update the zones"""
                    zones = self.manager.update_zone_owners(context, values,
                                                            args[0])
                    LOG.info(_("zones is %(zones)s"), {"zones": zones})
                    LOG.info(_("zone_id is %(zone_id)s"), {"zone_id": args[0]})
                except checkParam:
                    """return the wrong message"""
                    return tools.ret_info(checkParam.code, checkParam._msg_fmt)
            else:
                """return the wrong message"""
                checkParam._msg_fmt = 'the key is not owners'
                return tools.ret_info(checkParam.code, checkParam._msg_fmt)
        else:
            """get the body"""
            context = req.context
            """check the in values"""
            valid_attributes = ['default_ttl', 'current_user']
            try:
                """check the in values nums"""
                values = tools.load_values(req, valid_attributes)
                """trying to rpc update the zones"""
                zones = self.manager.update_zone(context, values, args[0])
                LOG.info(_("zones is %(zones)s"), {"zones": zones})
                LOG.info(_("zone_id is %(zone_id)s"), {"zone_id": args[0]})
            except checkParam:
                """return the wrong message"""
                return tools.ret_info(checkParam.code, checkParam._msg_fmt)
        return zones

    def remove(self, req, *args, **kwargs):
        """get the body"""
        context = req.context
        """check the in values"""
        valid_attributes = ['current_user']
        try:
            """check the in values nums"""
            values = tools.load_values(req, valid_attributes)
            """trying to rpc delete the zone"""
            zones = self.manager.delete_zone(context, values, args[0])
            LOG.info(_("zones is %(zones)s"), {"zones": zones})
            LOG.info(_("zone_id is %(zone_id)s"), {"zone_id": args[0]})
        except checkParam:
            """return the wrong message"""
            return tools.ret_info(checkParam.code, checkParam._msg_fmt)
        return zones

    def list(self, req, *args, **kwargs):
        context = req.context
        """check the in values"""
        valid_attributes = ['current_user']
        if 'object' in args:
            LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
            values = tools.load_values(req, valid_attributes)
            zones = self.manager.get_all_db_zone(context)
            LOG.info(_("Return of get_all_db_zone JSON is %(zones)s !"),
                     {"zones": zones})
        elif 'device' in args:
            LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                     {"args": args, "kwargs": kwargs})
#             values = tools.load_values(req, valid_attributes)
            zones = self.manager.get_zones(context)
            LOG.info(_("Return of get_zones JSON is %(zones)s !"),
                     {"zones": zones})
        else:
            """return the wrong message"""
            return tools.ret_info(checkParam.code, "url error")
        return zones

    def show(self, req, *args, **kwargs):
        context = req.context
        if 'object' in args:
            LOG.info(_(" args is %(args)s"), {"args": args})
            zones = self.manager.get_zone_db_details(context)
            LOG.info(_("Return of get_zone_db_details JSON is %(zones)s !"),
                     {"zones": zones})
        elif 'device' in args:
            LOG.info(_(" args is %(args)s"), {"args": args})
            """trying to rpc get the zones"""
            zones = self.manager.get_zones(context)
            LOG.info(_("Return of get_zones JSON is %(zones)s !"),
                     {"zones": zones})
        else:
            """return the wrong message"""
            return tools.ret_info(checkParam.code, "url error")
        return zones

    def make_dns_zone_object(self, values):
        target_values = {}
        for k in values:
            if k == "name":
                target_values['zone_name'] = values[k]
                target_values['zone_id'] = values[k]
            elif k == "current_user":
                pass
            else:
                target_values[k] = values[k]
        return target_values
