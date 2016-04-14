from oslo_config import cfg
from oslo_utils import timeutils
from oslo_db import exception as db_exception
from oslo_log import log as logging
from nca47 import objects
from nca47.common.i18n import _
from nca47.common.i18n import _LI
from nca47.common.i18n import _LE
from nca47.common import exception
from nca47.db import api as db_api
from amqp.exceptions import NotFound

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

DB_COMMON = None

DNS_VRES_ID_OPT = cfg.StrOpt('dns_vres_id', default=None,
                             help=_('The dns virtual resource id in database'))

opt_group = cfg.OptGroup(name='zdns',
                         title='Options for the nca47-zdns_driver service')
CONF.register_group(opt_group)
CONF.register_opt(DNS_VRES_ID_OPT, opt_group)


class DBCommon(object):

    """operate db history table"""

    def __init__(self):
        self.db_api = db_api.get_instance()
        super(DBCommon, self).__init__()

    @classmethod
    def get_instance(cls):

        global DB_COMMON
        if not DB_COMMON:
            DB_COMMON = cls()
        return DB_COMMON

    def create_in_storage(self, context, obj):
        """create a data in DB"""
        try:
            # create the data in db
            obj = obj.create(context, obj.as_dict())
        except db_exception:
            LOG.error(_LE("Create/Insert db operation failed!"))
            raise db_exception
        return obj

    def get_vres_agent_view(self, context, **kwargs):
        vres_agent_view = {
            "tenant_id": kwargs['tenant_id'],
            "agent_type": kwargs['agent_type'],
            "network_zone": kwargs['network_zone'],
            "dc_name": kwargs['dc_name']
        }
        vres = objects.Vres_Agent_View(context, **vres_agent_view)
        try:
            obj = vres.get_object(context, **vres_agent_view)
        except Exception:
            LOG.error(_LE("Cannot get the corresponding vres and agent"
                          " information!"))
            raise exception.NoexistOrMultipleError(
                param_name="the vres_agent view object with tenant_id=%s, "
                           "dc_name=%s, network_zone=%s, agent_type=%s"
                           % (kwargs['tenant_id'], kwargs['dc_name'],
                              kwargs['network_zone'], kwargs['agent_type']))
        return obj

    def get_fw_vfw_id(self, context, **kwargs):
        # get the value vfw_id(fw_vfw_info_id)
        vfw_dic = {}
        vfw_dic['vfw_name'] = kwargs['vfw_name']
        vfw_dic['vres_id'] = kwargs['vres_id']
        vfw_dic['deleted'] = False
        fwvfw = objects.VFW(context, **vfw_dic)
        try:
            rstfwvfw = fwvfw.get_object(context, **vfw_dic)
        except Exception as e:
            LOG.error(_LE("Cannot get the corresponding vfw information!"))
            LOG.exception(e)
            raise exception.NoexistOrMultipleError(
                param_name="vfw with vres_id=" + vfw_dic['vres_id'])
        return rstfwvfw

    def get_addrobj_name(self, context, **kwargs):
        # IP address is converted to an address object
        vfw_dic = {}
        vfw_dic['ip'] = kwargs['ip']
        vfw_dic['vfw_id'] = kwargs['vfw_id']
        vfw_dic['deleted'] = False
        obj_addrobj = objects.FwAddrObjInfo(context, **vfw_dic)
        try:
            obj_addrobj = obj_addrobj.get_object(context, **vfw_dic)
        except Exception as e:
            LOG.error(_LE("Cannot get the corresponding addrobj information!"))
            LOG.exception(e)
            raise exception.NoexistOrMultipleError(
                param_name="addrobj with ip=" + vfw_dic['ip'])
        return obj_addrobj.name

    def insert_operation_history(self, context, **kwargs):
        current_time = timeutils.utcnow()
        opt_params = {}
        if 'vres_id' in kwargs:
            opt_params['config_id'] = kwargs['vres_id']
        elif CONF.zdns.dns_vres_id:
            opt_params['config_id'] = CONF.zdns.dns_vres_id
        else:
            LOG.error(_LE("The Resource(with target vres_id) "
                          "could not be found!"))
            raise NotFound()
        opt_params['input'] = kwargs['input']
        opt_params['operation_type'] = kwargs['method']
        opt_params['operation_time'] = current_time
        opt_params['operation_status'] = kwargs['status']
        opt_obj = objects.OperationHistory(context, **opt_params)
        LOG.info(_LI("Inserting operation history record in DB"))
        operation_history = self.create_in_storage(context, opt_obj)
        LOG.info(_LI("Insert operation history record in DB successful"))
        return operation_history

    def update_operation_history(self, context, id_, **kwargs):
        opt_params = {}
        opt_params['operation_status'] = kwargs['status']
        opt_obj = objects.OperationHistory(context, **opt_params)
        LOG.info(_LI("updating operation history record in DB"))
        opt_obj.update(context, id_, opt_obj.as_dict())
        LOG.info(_LI("update operation history record in DB successful!"))
        return None

    def is_exist_object(self, context, obj):
        is_exist = False
        target_dic = dict(obj.as_dict(), **{'deleted': False})
        db_obj = None
        try:
            # create the data in db
            db_obj = obj.get_object(context, **target_dic)
        except Exception:
            pass
        if db_obj:
            is_exist = True
        return is_exist

    def merge_dict_view(self, dic):
        kw = {}
        kw['tenant_id'] = dic['tenant_id']
        kw['agent_type'] = "FW"
        kw['network_zone'] = dic['network_zone']
        kw['dc_name'] = dic['dc_name']
        return kw
