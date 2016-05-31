"""
Represent router-switch api interface
"""
import pecan
from oslo_log import log as logging
from oslo_messaging import RemoteError
from oslo_serialization import jsonutils as json
from pecan import expose
from pecan.rest import RestController
from nca47.manager import central
from nca47.common.i18n import _LE
from nca47.common.exception import ParamNull
from nca47.common.exception import ParamFormatError
from nca47.common.exception import Nca47Exception
from nca47.api.controllers.v1 import tools

LOG = logging.getLogger(__name__)


class RouterSwitchController(RestController):

    def __init__(self):
        self.manager = central.CentralManager.get_instance()
        super(RouterSwitchController, self).__init__()

    @expose('json')
    def index(self):
        return {"Information": "The url is for router-switch base RestApi "
                "interface"}

    _custom_actions = {
        'execute': ['POST']
    }

    @expose('json')
    def execute(self, *args, **kwargs):
        context = pecan.request.context
        body = pecan.request.body
        try:
            body_json = json.loads(body)
            not_null_keys = ['dc_name', 'network_zone', 'agent_type',
                             'commands']
            tools.validat_values(body_json, not_null_keys)
            if not isinstance(body_json['commands'], list):
                raise ParamFormatError(param_name="commands")
            response = self.manager.execute_commands(context, body_json)
        except Nca47Exception as e:
            self.response.status = e.code
            LOG.error(_LE('Error exception! error info: ' + e.message))
            LOG.exception(e)
            pecan.response.status = e.code
            return tools.ret_info(e.code, e.message)
        except RemoteError as exception:
            pecan.response.status = 500
            message = exception.value
            return tools.ret_info(pecan.response.status, message)
        except Exception as e:
            LOG.exception(e)
            pecan.response.status = 500
            return tools.ret_info(pecan.response.status, e.message)
        return response
