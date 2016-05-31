from oslo_config import cfg
from oslo_log import log as logging
from nca47.common.i18n import _

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

AGENT_OPTS = [
    cfg.StrOpt('agent_net_ip',
               default='0.0.0.0',
               help=_('The public ip address of agent host '
                      'on which run agent service.')),
    cfg.StrOpt('agent_ip',
               default='0.0.0.0',
               help=_('The internal ip address of agent host '
                      'on which run agent service')),
    cfg.StrOpt('dc_name',
               default='PDC',
               help=_('The DataCenter name which the agent belongs to')),
    cfg.StrOpt('network_zone',
               default='BIZ',
               help=_('The network zone name which the agent belongs to')),
    cfg.StrOpt('agent_type',
               default='zdns',
               help=_('The device type which agent would be connect'))
]

opt_group = cfg.OptGroup(name='agent',
                         title='Options for nca47 agent node info')
CONF.register_group(opt_group)
CONF.register_opts(AGENT_OPTS, opt_group)


def getAgent_config():
    host = CONF.agent.agent_ip
    nat_ip = CONF.agent.agent_net_ip
    dc_name = CONF.agent.dc_name
    network_zone = CONF.agent.network_zone
    agent_type = CONF.agent.agent_type
    agent = {"agent_ip": host, "agent_nat_ip": nat_ip, "dc_name": dc_name,
             "network_zone": network_zone, "agent_type": agent_type
             }
    return agent
