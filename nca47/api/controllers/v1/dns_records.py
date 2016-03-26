from nca47.api.controllers.v1 import base
from nca47.common.i18n import _
from nca47.api.controllers.v1 import tools as tool
from oslo_log import log as logging
from nca47.manager import central
from nca47.common.exception import Nca47Exception
from oslo_serialization import jsonutils as json
from nca47.common.i18n import _LE
from six.moves import http_client

LOG = logging.getLogger(__name__)


class DnsRecordsController(base.BaseRestController):
    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(DnsRecordsController, self).__init__()

    def create(self, req, *args, **kwargs):
        """create the dns zone_record"""
        record = None
        try:
            list_ = ['name', 'type', 'ttl', 'rdata', 'current_user', "klass"]
            # get the body
            dic = json.loads(req.body)
            # validate the in values of the zone_record
            dic_body = tool.validat_parms(dic, list_)
            context = req.context
            LOG.info(_("req is %(json)s, args is %(args)s,"
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            # from rpc server create the zone_record
            record = self.manager.create_record(context, dic_body, args[0])
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = http_client.INTERNAL_SERVER_ERROR
            message = "the values of the body format error"
            return tool.ret_info(self.response.status, message)
        LOG.info(_("Return of create_zone_record JSON is %(record)s !"),
                 {"record": record})
        return record

    def update(self, req, *args, **kwargs):
        """update the dns zone_record"""
        record = None
        try:
            list_ = ['ttl', 'rdata', 'current_user']
            # get the body
            dic = json.loads(req.body)
            # validate the in values of the zone_record
            dic_body = tool.validat_parms(dic, list_)
            ctx = req.context
            LOG.info(_("req is %(json)s, args is %(args)s, "
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            # from rpc server update the zone_record
            record = self.manager.update_record(ctx, dic_body, args[0],
                                                args[1])
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = http_client.INTERNAL_SERVER_ERROR
            message = "the values of the body format error"
            return tool.ret_info(self.response.status, message)
        LOG.info(_("Return of update_record JSON  is %(record)s !"),
                 {"record": record})
        return record

    def remove(self, req, *args, **kwargs):
        """delete the dns zone_record"""
        record = None
        try:
            list_ = ['current_user']
            # get the body
            dic = json.loads(req.body)
            # validate the in values of the zone_record
            dic_body = tool.validat_parms(dic, list_)
            ctx = req.context
            LOG.info(_("server is %(json)s, args is %(args)s, "
                       "kwargs is %(kwargs)s"),
                     {"json": req.body, "args": args, "kwargs": kwargs})
            """from rpc server delete the zone_record"""
            record = self.manager.delete_record(ctx, dic_body, args[0],
                                                args[1])
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = http_client.INTERNAL_SERVER_ERROR
            message = "the values of the body format error"
            return tool.ret_info(self.response.status, message)
        LOG.info(_("Return of remove_record JSON  is %(record)s !"),
                 {"record": record})
        return record

    def show(self, req, *args, **kwargs):
        """get the one of the dns zone_record"""
        record = None
        try:
            context = req.context
            if 'device' in args:
                LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                         {"args": args, "kwargs": kwargs})
                # from rpc server show the zone_record
                record = self.manager.get_dev_records(context,
                                                      args[1])
            else:
                LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                         {"args": args, "kwargs": kwargs})
                # from db server show the zone_record
                record = self.manager.get_db_records(context, args[0])
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tool.ret_info(e.code, e.message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = http_client.INTERNAL_SERVER_ERROR
            message = "the values of the body format error"
            return tool.ret_info(self.response.status, message)
        LOG.info(_("Return of show_record JSON  is %(record)s !"),
                 {"record": record})
        return record
