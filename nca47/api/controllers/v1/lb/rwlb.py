from oslo_log import log as logging
from oslo_serialization import jsonutils as json
from oslo_messaging import RemoteError
from nca47.api.controllers.v1 import base
from nca47.common.i18n import _LE
from nca47.manager import central
from nca47.api.controllers.v1 import tools
from nca47.common.exception import Nca47Exception
from nca47.common.exception import ParamValueError
import time


LOG = logging.getLogger(__name__)


class RDLBController(base.BaseRestController):
    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(RDLBController, self).__init__()

    def create(self, req, *args, **kwargs):
        context = req.context
        valid_attributes = ['tenant_id', 'vnetwork_name', 'environment_name',
                            'application', 'node', 'rip', 'vip', 'virtualname',
                            'vport', 'rport', 'pbindtype',
                            'ptmouttime', 'metrictype', "protocol"]
        try:
            command_list = []
            body_values = json.loads(req.body)
            values = tools.validat_values(body_values, valid_attributes)
            if not tools.is_no_empty_list(values["rip"]):
                raise ParamValueError(param_name="rip")
            if not tools.is_no_empty_list(values["vport"]):
                raise ParamValueError(param_name="vport")
            if not tools.is_no_empty_list(values["rport"]):
                raise ParamValueError(param_name="rport")
            if "dbindtype" in values.keys():
                if len(values["dbindtype"]) == 0:
                    values["dbindtype"] = ""
            else:
                values["dbindtype"] = ""
            batch = time.time()
            values["batch"] = batch
            # create pool
            realserver_list = self.manager.create_pool(context, values)
            commant_apply = "apply"
            for key in realserver_list:
                command_input = key["command_input"]
                for outp in command_input:
                    command_list.append(outp)
            command_list.append(commant_apply)
            values["realservername"] = realserver_list
            # create member
            member = self.manager.create_lb_member(context, values)
            command_input = member["command_input"]
            for key in command_input:
                command_list.append(key)
            command_list.append(commant_apply)
            # create vip
            vip_list = self.manager.create_vip(context, values)
            for key in vip_list["command_input"]:
                command_list.append(key)
            command_list.append(commant_apply)
            # create server
            values["virtualservername"] = vip_list
            values["groupname"] = member
            server_list = self.manager.create_server(context, values)
            for key in server_list:
                for outp in key["command_input"]:
                    command_list.append(outp)
            command_list.append(commant_apply)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", command_list)

    def remove(self, req, id, *args, **kwargs):
        context = req.context
        try:
            realservername = id
            real_dic = {}
            real_dic['realservername'] = realservername
            real_list = self.manager.delete_real_service(context, real_dic)
            command_list = []
            for key in real_list:
                for outp in key:
                    command_list.append(outp)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            self.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            self.response.status = 500
            message = exception.value
            return tools.ret_info(self.response.status, message)
        except Exception as e:
            LOG.exception(e)
            self.response.status = 500
            return tools.ret_info(self.response.status, e.message)
        return tools.ret_info("200", command_list)

    def list(self, req, *args, **kwargs):
        return None
