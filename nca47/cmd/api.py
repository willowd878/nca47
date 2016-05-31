import sys
sys.path.append('/vagrant/nca47/')
from oslo_config import cfg
from oslo_log import log
from nca47.common import service as nca47_service
from nca47.manager import service

CONF = cfg.CONF

LOG = log.getLogger(__name__)


def main():
    """The nca47 Service API."""
    # Parse config file and command line options, then start logging
    nca47_service.prepare_service(sys.argv)

    # Build and start the WSGi app
    launcher = nca47_service.process_launcher()
    server = nca47_service.WSGIService('nca47_api', CONF.api.enable_ssl_api)
    launcher.launch_service(server, workers=server.workers)

    rpc_server = service.AgentService(topic='check_agent_heartbeat')
    launcher.launch_service(rpc_server, workers=2)
    launcher.wait()


if __name__ == '__main__':
    sys.exit(main())
