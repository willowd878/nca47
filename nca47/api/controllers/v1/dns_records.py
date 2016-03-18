from nca47.api.controllers.v1 import base
from nca47.common.i18n import _
from nca47.api.controllers.v1 import tools as tool
from oslo_log import log as logging
from nca47.common.exception import checkParam, checkBody
from nca47.manager import central
LOG = logging.getLogger(__name__)


class DnsRecordsController(base.BaseRestController):
    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(DnsRecordsController, self).__init__()

    def create(self, req, *args, **kwargs):
        zones = None
        try:
            json_str = req.body
            if json_str:
                context = req.context
                LOG.info(_("req is %(json)s, args is %(args)s,"
                           " kwargs is %(kwargs)s"),
                         {"json": json_str, "args": args, "kwargs": kwargs})
                dic = tool.validation_create_authority_records(json_str)
                zones = self.manager.create_record(context, dic, args[0])
                LOG.info(_("Return of create_zone_record JSON is %(zones)s !"),
                         {"zones": zones})
            else:
                return tool.ret_info(checkBody.code, checkBody._msg_fmt)
        except checkParam:
                return tool.ret_info(checkParam.code, checkParam._msg_fmt)
        return zones

    def update(self, req, *args, **kwargs):
        zones = None
        try:
            json_str = req.body
            if json_str:
                ctx = req.context
                LOG.info(_("req is %(json)s, args is %(args)s, "
                           "kwargs is %(kwargs)s"),
                         {"json": json_str, "args": args, "kwargs": kwargs})
                dic = tool.validation_update_authority_records(json_str)
                zones = self.manager.update_record(ctx, dic, args[0], args[2])
                LOG.info(_("Return of update_record JSON  is %(zones)s !"),
                         {"zones": zones})
            else:
                return tool.ret_info(checkBody.code, checkBody._msg_fmt)
        except checkParam:
                return tool.ret_info(checkParam.code, checkParam._msg_fmt)
        return zones

    def remove(self, req, *args, **kwargs):
        zones = None
        try:
            json_str = req.body
            if json_str:
                ctx = req.context
                LOG.info(_("server is %(json)s, args is %(args)s, "
                           "kwargs is %(kwargs)s"),
                         {"json": json_str, "args": args, "kwargs": kwargs})
                dic = tool.validation_remove_authority_records(json_str)
                zones = self.manager.delete_record(ctx, dic, args[0], args[2])
                LOG.info(_("Return of delete_record JSON is %(zones)s !"),
                         {"zones": zones})
            else:
                return tool.ret_info(checkBody.code, checkBody._msg_fmt)
        except checkParam:
                return tool.ret_info(checkParam.code, checkParam._msg_fmt)
        return zones

    def show(self, req, *args, **kwargs):
        zones = None
        try:
            if len(args) == 3 and (args[0] == 'object' or
                                   args[0] == 'device') and args[2] == 'rrs':
                context = req.context
                if 'object' in args:
                    LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                             {"args": args, "kwargs": kwargs})
                    zones = self.manager.get_records(context, req.body,
                                                     args[1])
                    LOG.info(_("Return of get_obj_record JSON is %(zones)s !"),
                             {"zones": zones})

                elif 'device' in args:
                    LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                             {"args": args, "kwargs": kwargs})
                    zones = self.manager.get_dev_records(context, req.body,
                                                         args[1])
                    LOG.info(_("Return of get_dev_record JSON is %(zones)s !"),
                             {"zones": zones})
                else:
                    raise checkParam
            else:
                raise checkParam
        except checkParam:
                return tool.ret_info(checkParam.code, checkParam._msg_fmt)
        return zones
