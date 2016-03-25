from oslo_log import log as logging

from nca47.api.controllers.v1 import base
from nca47.api.controllers.v1 import tools
from nca47.common.exception import ParamValueError
from nca47.common.exception import Nca47Exception
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.manager import central
from oslo_serialization import jsonutils as json
from six.moves import http_client

LOG = logging.getLogger(__name__)


class DnsZones(base.BaseRestController):
    """
    nca47 dnsZones class, using for add/delete/update/query the zones info,
    validate parameters whether is legal, handling DB operations and calling
    rpc client's corresponding method to send messaging to agent endpoints
    """
    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(DnsZones, self).__init__()

    def create(self, req, *args, **kwargs):
        """create the dns zones"""
        # get the context
        context = req.context
        try:
            # get the body
            values = json.loads(req.body)
            if values['renewal'] == 'no':
                # check the in values
                valid_attributes = ['name', 'owners', 'default_ttl', 'renewal',
                                    'current_user']
            else:
                # check the in values
                valid_attributes = ['name', 'owners', 'default_ttl', 'renewal',
                                    'zone_content', 'slaves', 'current_user']
            # check the in values
            recom_msg = tools.validat_parms(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server create the zones in db and device
            zones = self.manager.create_zone(context, recom_msg)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = http_client.INTERNAL_SERVER_ERROR
            message = "the values of the body format error"
            return tools.ret_info(self.response.status, message)
        return zones

    def update(self, req, *args, **kwargs):
        """update the dns zones by currentUser/owners"""
        # get the context
        context = req.context
        try:
            # get the body
            values = json.loads(req.body)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            LOG.info(_("the id is %(id)s"), {"id": args[0]})
            if len(args) is 2:
                if args[1] == 'owners':
                    # check the in values
                    valid_attributes = ['owners', 'current_user']
                    recom_msg = tools.validat_parms(values, valid_attributes)
                    # from rpc server update the zones in db and device
                    zones = self.manager.update_zone_owners(context, recom_msg,
                                                            args[0])
                else:
                    # return the wrong message
                    raise ParamValueError(param_name="no owners")
            else:
                # check the in values
                valid_attributes = ['default_ttl', 'current_user']
                recom_msg = tools.validat_parms(values, valid_attributes)
                # from rpc server update the zones in db and device
                zones = self.manager.update_zone(context, recom_msg, args[0])
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = http_client.INTERNAL_SERVER_ERROR
            message = "the values of the body format error"
            return tools.ret_info(self.response.status, message)
        return zones

    def remove(self, req, *args, **kwargs):
        """delete the dns zones"""
        # get the context
        context = req.context
        # check the in values
        valid_attributes = ['current_user']
        try:
            # get the body
            values = json.loads(req.body)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            LOG.info(_("the id is %(id)s"), {"id": args[0]})
            # check the in values
            recom_msg = tools.validat_parms(values, valid_attributes)
            # from rpc server delete the zones in db and device
            zones = self.manager.delete_zone(context, recom_msg, args[0])
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = http_client.INTERNAL_SERVER_ERROR
            message = "the values of the body format error"
            return tools.ret_info(self.response.status, message)
        return zones

    def list(self, req, *args, **kwargs):
        """get the list of the dns zones"""
        # get the context
        context = req.context
        try:
            if 'device' in args:
                LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                         {"args": args, "kwargs": kwargs})
                # from rpc server get the zones in device
                zones = self.manager.get_zones(context)
            else:
                LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                         {"args": args, "kwargs": kwargs})
                # from rpc server get the zones in db
                zones = self.manager.get_all_db_zone(context)
                LOG.info(_("Return of get_all_db_zone JSON is %(zones)s !"),
                         {"zones": zones})
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        LOG.info(_("Return of get_zones json is %(zones)s"), {"zones": zones})
        return zones

    def show(self, req, *args, **kwargs):
        """get one dns zone info"""
        # get the context
        context = req.context
        try:
            if 'device' in args:
                LOG.info(_(" args is %(args)s"), {"args": args})
                # from rpc server get the zone in device
                zones = self.manager.get_zones(context)
            else:
                LOG.info(_(" args is %(args)s"), {"args": args})
                # from rpc server get the zone in db
                zones = self.manager.get_zone_db_details(context, args[0])
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        LOG.info(_("Return of get_zones json is %(zones)s"), {"zones": zones})
        return zones
