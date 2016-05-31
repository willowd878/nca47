from oslo_log import log as logging
from oslo_messaging import RemoteError
from nca47.api.controllers.v1 import base
from nca47.api.controllers.v1 import tools
from nca47.common.exception import Nca47Exception
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.manager import central
from oslo_serialization import jsonutils as json

LOG = logging.getLogger(__name__)


class RegionController(base.BaseRestController):

    """
    nca47 Region class, using for add/delete/query the regions info,
    validate parameters whether is legal, handling DB operations and calling
    rpc client's corresponding method to send messaging to agent endpoints
    """

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(RegionController, self).__init__()

    def create(self, req, *args, **kwargs):
        """create the user regions"""
        # get the context
        context = req.context
        try:
            # get the body
            values = json.loads(req.body)
            valid_attributes = ['tenant_id', 'name']
            # check the in values
            recom_msg = self.validat_parms(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server create the regions in db and device
            regions = self.manager.create_region(context, recom_msg)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as e:
            self.response.status = 500
            message = e.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', regions)

    def remove(self, req, id, *args, **kwargs):
        """delete the dns regions"""
        # get the context
        context = req.context
        try:
            # get the body
            values = {}
            values.update(kwargs)
            values['id'] = id
            valid_attributes = ['tenant_id', 'id']
            # check the in values
            recom_msg = self.validat_parms(values, valid_attributes)
            LOG.info(_("the in value body is %(body)s"), {"body": values})
            # from rpc server delete the regions in db and device
            self.manager.delete_region(context, recom_msg['id'])
        except Nca47Exception as e:
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', "success")

    def list(self, req, *args, **kwargs):
        """get the list of the dns regions"""
        # get the context
        context = req.context
        try:
            # get the body
            values = {}
            values.update(kwargs)
            if kwargs.get('device'):
                LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                         {"args": args, "kwargs": kwargs})
                # from rpc server get the regions in device
                regions = self.manager.get_regions(context)
            else:
                LOG.info(_(" args is %(args)s, kwargs is %(kwargs)s"),
                         {"args": args, "kwargs": kwargs})
                # from db server get the regions in db
                regions = self.manager.get_db_regions(context, values)
                LOG.info(_("Return get_db_regions JSON is %(regions)s !"),
                         {"regions": regions})
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', regions)

    def show(self, req, id, *args, **kwargs):
        """get one dns region info"""
        # get the context
        context = req.context
        try:
            if kwargs.get('device'):
                LOG.info(_(" args is %(args)s"), {"args": args})
                # from rpc server get the region in device
                regions = self.manager.get_region(context)
            else:
                LOG.info(_(" args is %(args)s"), {"args": args})
                # from rpc server get the region in db
                regions = self.manager.get_region_db_detail(context, id)
                regions_user = self.manager.get_members(context)
                region_users = []
                for key in regions_user:
                    region_users.append(dict(key))
                regions.region_user = region_users
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', regions)

    def validat_parms(self, values, valid_keys):
        """check the in value is null and nums"""
        recom_msg = tools.validat_values(values, valid_keys)
        return recom_msg
