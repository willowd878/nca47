from oslo_log import log as logging
from oslo_messaging import RemoteError
from nca47.api.controllers.v1 import base
from nca47.api.controllers.v1 import tools
from nca47.common.exception import ParamNull
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamValueError
from nca47.common.exception import IllegalParam
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.manager import central
import json

LOG = logging.getLogger(__name__)


class SyngroupController(base.BaseRestController):
    """
    nca47 Syngroup class ,using for add/put/delete/get/getall the Syngroup
    info, validate parameters whether is legal,handling DB operations and
    calling rpc client's corresponding method to send messaging to agent
    endpoint.
    """

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(SyngroupController, self).__init__(self)

    def create(self, req, *args, **kwargs):
        """
        Create syngorup method
        :param req:
        :param args:
        :param kwargs:
        :return:
        """
        context = req.context
        try:
            values = json.loads(req.body)
            values = self.check_null(values)
            self.check_create(values)
            LOG.info(_('the in value body is %(body)s'), {'body': values})
            syngroups = self.manager.create_syngroup(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE("Error exception ! error info: " + e.message))
            LOG.exception(e)
            return tools.ret_info(self.response.status, e.message)
        except RemoteError as e:
            self.response.status = 500
            message = e.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info('200', syngroups)

    def update(self, req, id, *args, **kwargs):
        """
        update Syngroup method
        :param req:
        :param args:
        :param kwargs:
        :return:
        """
        context = req.context
        try:
            values = json.loads(req.body)
            values['id'] = id
            LOG.info(_("the in value body if %(body)s"), {'body': values})
            self.check_not_null(values)
            values = self.check_update(values)
            syngroups = self.manager.update_syngroup(context, values)
            # args[0] is id
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE("Error exception! error info: " + e.message))
            LOG.exception(e)
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.reponse.status = 500
            message = exception.value
            return tools.ret_info(self.reponse.status, message)
        except Exception as exception:
            LOG.exception(exception)
            self.response.status = 500
            return tools.ret_info(self.response.status, exception.message)
        return tools.ret_info('200', syngroups)

    def remove(self, req, id, *args, **kwargs):
        """
        delete the syngroup method
        :param req:
        :param id:
        :param args:
        :param kwargs:
        :return:
        """
        context = req.context
        try:
            values = {}
            values.update(kwargs)
            values['id'] = id
            self.check_remove(values)
            LOG.info(_('the in value body is %(body)s'), {'body': values})
            self.manager.delete_syngroup(context, values)
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
        return tools.ret_info('200', 'success')

    def get(self, req, *args, **kwargs):
        """
        not use
        # get info for one or more
        :param req:
        :param args:
        :param kwargs:
        :return:
        """
        context = req.context
        try:
            LOG.info(
                _("args is %(args)s,kwargs is %(kwargs)s"), {
                    'args': args, "kwargs": kwargs})
            syngroups = self.manager.get_syngroups(context)
            LOG.info(_("Retrun of get_all_db_zone JSON is %(syngroup)s !"),
                     {"syngroup": syngroups})
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
        return tools.ret_info('200', syngroups)

    def list(self, req, *args, **kwargs):
        """
        list all syngroup method
        :param req:
        :param id:
        :param args:
        :param kwargs:
        :return:
        """
        context = req.context
        try:
            search_opts = {}
            search_opts.update(req.GET)
            # values = json.loads(req.body)
            # if 'device' in args:
            #     LOG.info(_("args is %(args)s,kwargs is %(kwargs)s"),
            #              {'args': args, 'kwargs': kwargs})
            #     zones = self.manager.list_syngroup(context)
            # else:
            LOG.info(
                _("args is %(args)s,kwargs is %(kwargs)s"), {
                    'args': args, "kwargs": kwargs})
            # self.check_search(search_opts)
            syngroup = self.manager.get_syngroups(context, search_opts)
            self.get_return_convert(syngroup)
            LOG.info(_("Retrun of get_all_db_zone JSON is %(syngroup)s !"),
                     {"syngroup": syngroup})
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
        return tools.ret_info('200', syngroup)

    def show(self, req, id, *args, **kwargs):
        """
        get syngroup by id
        :param req:
        :param id:
        :param args:
        :param kwargs:
        :return: return http response
        """
        context = req.context
        try:
            LOG.info(_("args is %(args)s"), {"args": args})
            syngroups = self.manager.get_syngroup(context, id)
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
        return tools.ret_info('200', syngroups)

    def check_search(self, dic):
        validate_list = [
            'tenant_id',
            'name',
            'gslb_zone_names',
            'pass',
            'probe_range']
        for key in dic.keys():
            if key not in validate_list:
                raise IllegalParam(param_name=key)

    def check_update(self, dic):
        if 'name' in dic.keys():
            del dic['name']
        validate_list = ['id', 'tenant_id']
        tools.validat_values(dic, validate_list)
        self.check_is_list(dic)
        return dic

    def check_create(self, dic):
        self.check_is_list(dic)
        validate_list = ['tenant_id', 'name', ]
        tools.validat_values(dic, validate_list)

    def check_remove(self, dic):
        validate_list = ['id', 'tenant_id']
        dic = tools.validat_values(dic, validate_list)

    def check_not_null(self, values):
        null_list = []
        for key in values.keys():
            if key not in null_list:
                if isinstance(values[key], basestring) and not tools.\
                        is_not_nil(values[key]):
                    raise ParamNull(param_name=key)

    def get_return_convert(self, syngroup):
        for dic in syngroup:
            if 'gslb_zone_names' in dic:
                if dic['gslb_zone_names'] == "":
                    dic['gslb_zone_names'] = []
                else:
                    try:
                        dic['gslb_zone_names'] = eval(dic['gslb_zone_names'])
                    except:
                        pass
        return syngroup

    def check_null(self, values):
        ret = {}
        for key in values:
            if values[key] != '' and values[key] != []:
                ret[key] = values[key]
        return ret

    def check_is_list(self, dic):
        validate_list = ['gslb_zone_names']
        for key in validate_list:
            if key in dic.keys():
                if not isinstance(dic[key], list):
                    raise ParamValueError(param_name=key)
