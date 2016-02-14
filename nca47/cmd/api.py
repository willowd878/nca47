"""The nca47 Service API."""
import sys

from oslo_config import cfg
from oslo_log import log

from nca47.common import service as nca47_service

CONF = cfg.CONF

LOG = log.getLogger(__name__)


def main():
    # Parse config file and command line options, then start logging
    nca47_service.prepare_service(sys.argv)

    # Build and start the WSGi app
    launcher = nca47_service.process_launcher()
    server = nca47_service.WSGIService('nca47_api', CONF.api.enable_ssl_api)
    launcher.launch_service(server, workers=server.workers)
    launcher.wait()


if __name__ == '__main__':
    sys.exit(main())
