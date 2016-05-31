import oslo_messaging as messaging
from oslo_config import cfg
from oslo_log import log as logging
from nca47.common import rpc
from nca47.common.i18n import _LI

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

AGENT_API = None


class AgentAPI(object):
    """
    Client side of the agent manager RPC API.

    API version history:

        1.0 - Initial version
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='check_agent_heartbeat'):
        rpc.init(CONF)
        target = messaging.Target(topic=topic, version=self.RPC_API_VERSION)
        self.client = rpc.get_client(target, version_cap=self.RPC_API_VERSION)

    @classmethod
    def get_instance(cls):
        """
        The rpc.get_client() which is called upon the API object initialization
        will cause a assertion error if the designate.rpc.TRANSPORT isn't setup
        by rpc.init() before.

        This fixes that by creating the rpcapi when demanded.
        """
        global AGENT_API
        if not AGENT_API:
            AGENT_API = cls()
        return AGENT_API

    def report_agent_state(self, agentinfo):
        LOG.info(_LI("Checking agent heartbeat: Calling service's "
                     "report_agent_state."))
        context = {}
        return self.client.call(context, 'report_agent_state',
                                agent_info=agentinfo)
