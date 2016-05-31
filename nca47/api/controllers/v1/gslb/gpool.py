from oslo_log import log as logging
from oslo_messaging import RemoteError
from nca47.api.controllers.v1 import base
from nca47.api.controllers.v1 import tools
from nca47.common.exception import ParamNull
from nca47.common.exception import ParamValueError
from nca47.common.exception import Nca47Exception
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.manager import central
import json

LOG = logging.getLogger(__name__)


class GPoolController(base.BaseRestController):
    """
    nca47 GPool class ,using for add/put/delete/get/getall the GPool info,
    validate parameters whether is legal,handling DB operations and calling rpc
    client's corresponding method to send messaging to agent endpoint
    """

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(GPoolController, self).__init__(self)

    def create(self, req, *args, **kwargs):
        """
        create GPool method
        :param req:
        :param args:
        :param kwargs:
        :return: return http response
        """
        context = req.context
        try:
            values = json.loads(req.body)
            values = self.check_null(values)
            self.check_create(values)
            LOG.info(_('the in value body is %(body)s'), {'body': values})
            gpool = self.manager.create_gpool(context, values)
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
        return tools.ret_info('200', gpool)

    def update(self, req, id, *args, **kwargs):
        """
        update GPool method
        :param req:
        :param args:
        :param kwargs:
        :return:
        """
        context = req.context
        try:
            values = json.loads(req.body)
            values['id'] = id
            self.check_can_be_null(values)
            values = self.check_update(values)
            LOG.info(_('the in value body is %(body)s'), {'body': values})
            gpool = self.manager.update_gpool(context, values)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE("Error exception ! error info: " + e.message))
            LOG.exception(e)
            return tools.ret_info(self.response.status, e.message)
        except RemoteError as e:
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info('200', gpool)

    def remove(self, req, id, *args, **kwargs):
        """
        delete GPool method
        :param req:
        :param id:
        :param args:
        :param kwargs:
        :return: return http response
        """
        context = req.context
        try:
            values = {}
            values.update(kwargs)
            values['id'] = id
            self.check_remove(values)
            LOG.info(_('the in value body is %(body)s'), {'body': values})
            self.manager.delete_gpool(context, values)
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

    def list(self, req, *args, **kwargs):
        """
        get GPools method
        :param req:
        :param id:
        :param args:
        :param kwargs:
        :return: return http response
        """

        context = req.context
        try:
            search_opts = {}
            search_opts.update(req.GET)
            # self.check_search(values)
            LOG.info(
                _("args is %(args)s,kwargs is %(kwargs)s"), {
                    'args': args, "kwargs": kwargs})
            gpools = self.manager.get_gpools(context, search_opts)
            gpools = self.get_return_convert(gpools)
            LOG.info(_("Retrun of get_all_db_zone JSON is %(gpool)s !"),
                     {"gpool": gpools})
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
        return tools.ret_info('200', gpools)

    def show(self, req, id, *args, **kwargs):
        """
        get GPool method
        :param req:
        :param id:
        :param args:
        :param kwargs:
        :return: return http response
        """
        context = req.context
        try:
            LOG.info(_("args is %(args)s"), {"args": args})
            gpool = self.manager.get_gpool(context, id)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: %' + e.message))
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
        return tools.ret_info('200', gpool)

    def check_create(self, dic):
        self.check_is_list(dic)
        validate_list = ['tenant_id', 'name', 'enable', 'ttl', ]
        tools.validat_values(dic, validate_list)
        self.check_value(dic)

    def check_update(self, dic):
        if 'name' in dic.keys():
            del dic['name']
        self.check_value(dic)
        validate_list = ['id', 'tenant_id']
        tools.validat_values(dic, validate_list)
        self.check_is_list(dic)
        return dic

    def check_remove(self, dic):
        validate_list = ['id', 'tenant_id']
        tools.validat_values(dic, validate_list)

    def check_null(self, values):
        ret = {}
        for key in values:
            if len(str(values[key])) != 0:
                ret[key] = values[key]
        return ret

    def check_can_be_null(self, values):
        null_list = ['cname']
        for key in values.keys():
            if key not in null_list:
                if isinstance(
                        values[key],
                        basestring) and not tools.is_not_nil(
                        values[key]):
                    raise ParamNull(param_name=key)

    def check_is_list(self, dic):
        validate_list = ['hms', 'gmember_list']
        for key in validate_list:
            if key in dic.keys():
                if not isinstance(dic[key], list):
                    raise ParamValueError(param_name=key)

    def get_return_convert(self, gpool):
        for dic in gpool:
            if 'hms' in dic:
                if dic['hms'] == "":
                    dic['hms'] = []
                else:
                    try:
                        dic['hms'] = eval(dic['hms'])
                    except:
                        pass
            if 'gmember_list' in dic:
                if dic['gmember_list'] == "":
                    dic['gmember_list'] = []
                else:
                    try:
                        dic['gmember_list'] = eval(dic['gmember_list'])
                    except:
                        pass
        return gpool

    def check_value(self, dic):
        if 'ttl' in dic.keys():
            try:
                ttl = int(dic['ttl'])
                if not(ttl >= 0 and ttl <= 2147483647):
                    raise ParamValueError(param_name='ttl')
            except:
                raise ParamValueError(param_name='ttl')
        if 'enable' in dic.keys() and dic['enable'] not in ['yes', 'no']:
            raise ParamValueError(param_name="enable")
        if "warning" in dic.keys() and dic["warning"] not in ['yes', 'no']:
            raise ParamValueError(param_name="warning")
