import pecan
from oslo_log import log as logging
from pecan import expose
from pecan.rest import RestController
from nca47.manager.central import CentralManager


LOG = logging.getLogger(__name__)


class AgentController(RestController):

    def __init__(self):
        self.manager = CentralManager.get_instance()
        super(AgentController, self).__init__()

    @expose('json')
    def index(self):
        return {"Information": "The url is for nca's agent RestApi "
                "interface"}

    _custom_actions = {
        'listagent': ['GET']
    }

    @expose('json')
    def listagent(self, *args, **kwargs):
        context = pecan.request.context
        return self.manager.get_agent_list(context)
