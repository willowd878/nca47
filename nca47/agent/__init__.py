from oslo_config import cfg

import oslo_messaging as messaging

from oslo_log import log as logging
from nca47.agent import dns_driver
from nca47.agent import firewall_driver
from nca47.common import exception
from nca47.common import rpc
from nca47.common.i18n import _

LOG = logging.getLogger(__name__)

DRIVER_OPTS = [
    cfg.StrOpt('dns_driver', default='zdns',
               help=_('The dns driver for nca47 calling.')),
    cfg.StrOpt('firewall_driver', default='fake',
               help=_('The firewall driver for nca47 calling.')),
]

AGENT_OPTS = [
    cfg.StrOpt('agent_ip', default='127.0.0.1',
               help=_("The agent host's ip address, use for connection with"
                      "nca47 project")),
    cfg.StrOpt('agent_nat_ip', default='127.0.0.1',
               help=_("The agent host's ip address, use for connection with"
                      "target devices")),
    cfg.StrOpt('dc_name', default='localhost',
               help=_("The target data center's name")),
    cfg.StrOpt('network_zone', default='core',
               help=_("The network zone which the agent host running on")),
    cfg.StrOpt('agent_type', default='fake',
               help=_("the agent use for connection which type device")),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='backend_driver',
                         title='Options for the nca47-zdns_driver service')

agent_opts_group = cfg.OptGroup(name='agent',
                                title='Options for the agent information')
CONF.register_group(opt_group)
CONF.register_group(agent_opts_group)

CONF.register_opts(DRIVER_OPTS, opt_group)
CONF.register_opts(AGENT_OPTS, agent_opts_group)

AGENT_MANAGER_API = None

def get_dns_backend():
    LOG.debug("Loading dns backend driver by conf file")
    driver_name = CONF.backend_driver.dns_driver
    if driver_name == 'zdns':
        return dns_driver.zdns_driver.dns_zone_driver.get_instance()
    else:
        raise exception.DriverNotFound(driver_name=driver_name)


def get_firewall_backend():
    LOG.debug("Loading firewall backend driver by conf file")
    return None


class Agent_Service(object):
    
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='agent_manager'):
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
        global AGENT_MANAGER_API
        if not AGENT_MANAGER_API:
            AGENT_MANAGER_API = cls()
        return AGENT_MANAGER_API

    def agent_db_create(self, context=None, **kwargs):
        LOG.info(_("agent_db_create: Calling central's agent_db_create."))
        return self.client.cast(context, 'agent_db_create', **kwargs)