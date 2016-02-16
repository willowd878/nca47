import signal
import socket

from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_context import context
from oslo_log import log
import oslo_messaging as messaging
from oslo_service import service
from oslo_service import wsgi
from oslo_utils import importutils

from nca47.api import app
from nca47.common import config
from nca47.common import exception
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.common.i18n import _LI
from nca47.common import rpc

service_opts = [
    cfg.IntOpt('periodic_interval',
               default=60,
               help=_('Seconds between running periodic tasks.')),
    cfg.StrOpt('host',
               default=socket.getfqdn(),
               help=_('Name of this node. This can be an opaque identifier. '
                      'It is not necessarily a hostname, FQDN, or IP address. '
                      'However, the node name must be valid within '
                      'an AMQP key, and if using ZeroMQ, a valid '
                      'hostname, FQDN, or IP address.')),
]

CONF = cfg.CONF
LOG = log.getLogger(__name__)

CONF.register_opts(service_opts)


class RPCService(service.Service):
    def __init__(self, host, manager_module, manager_class):
        super(RPCService, self).__init__()
        self.host = host
        manager_module = importutils.try_import(manager_module)
        manager_class = getattr(manager_module, manager_class)
        self.manager = manager_class(host, manager_module.MANAGER_TOPIC)
        self.topic = self.manager.topic
        self.rpcserver = None
        self.deregister = True

    def start(self):
        super(RPCService, self).start()
        admin_context = context.RequestContext('admin', 'admin', is_admin=True)

        target = messaging.Target(topic=self.topic, server=self.host)
        endpoints = [self.manager]
        self.rpcserver = rpc.get_server(target, endpoints)
        self.rpcserver.start()

        self.handle_signal()
        self.manager.init_host()
        self.tg.add_dynamic_timer(
            self.manager.periodic_tasks,
            periodic_interval_max=CONF.periodic_interval,
            context=admin_context)

        LOG.info(_LI('Created RPC server for service %(service)s on host '
                     '%(host)s.'),
                 {'service': self.topic, 'host': self.host})

    def stop(self):
        try:
            self.rpcserver.stop()
            self.rpcserver.wait()
        except Exception as e:
            LOG.exception(_LE('Service error occurred when stopping the '
                              'RPC server. Error: %s'), e)
        try:
            self.manager.del_host(deregister=self.deregister)
        except Exception as e:
            LOG.exception(_LE('Service error occurred when cleaning up '
                              'the RPC manager. Error: %s'), e)

        super(RPCService, self).stop(graceful=True)
        LOG.info(_LI('Stopped RPC server for service %(service)s on host '
                     '%(host)s.'),
                 {'service': self.topic, 'host': self.host})

    def _handle_signal(self, signo, frame):
        LOG.info(_LI('Got signal SIGUSR1. Not deregistering on next shutdown '
                     'of service %(service)s on host %(host)s.'),
                 {'service': self.topic, 'host': self.host})
        self.deregister = False

    def handle_signal(self):
        """Add a signal handler for SIGUSR1.

        The handler ensures that the manager is not deregistered when it is
        shutdown.
        """
        signal.signal(signal.SIGUSR1, self._handle_signal)


def prepare_service(argv=[]):
    log.register_options(CONF)
    log.set_defaults(default_log_levels=['amqp=WARNING',
                                         'amqplib=WARNING',
                                         'qpid.messaging=INFO',
                                         'oslo_messaging=INFO',
                                         'sqlalchemy=WARNING',
                                         'keystoneclient=INFO',
                                         'stevedore=INFO',
                                         'eventlet.wsgi.server=WARNING',
                                         'iso8601=WARNING',
                                         'paramiko=WARNING',
                                         'requests=WARNING',
                                         'neutronclient=WARNING',
                                         'glanceclient=WARNING',
                                         'urllib3.connectionpool=WARNING',
                                         ])
    config.parse_args(argv)
    log.setup(CONF, 'nca47')


def process_launcher():
    return service.ProcessLauncher(CONF)


class WSGIService(service.ServiceBase):
    """Provides ability to launch ironic API from WSGi app."""

    def __init__(self, name, use_ssl=False):
        """Initialize, but do not start the WSGi server.

        :param name: The name of the WSGi server given to the loader.
        :param use_ssl: Wraps the socket in an SSL context if True.
        :returns: None
        """
        self.name = name
        self.app = app.setup_app()
        self.workers = (CONF.api.api_workers or
                        processutils.get_worker_count())
        if self.workers and self.workers < 1:
            raise exception.ConfigInvalid(
                _("api_workers value of %d is invalid, "
                  "must be greater than 0.") % self.workers)

        self.server = wsgi.Server(CONF, name, self.app,
                                  host=CONF.api.host_ip,
                                  port=CONF.api.port,
                                  use_ssl=use_ssl,
                                  logger_name=name)

    def start(self):
        """Start serving this service using loaded configuration.

        :returns: None
        """
        self.server.start()

    def stop(self):
        """Stop serving this API.

        :returns: None
        """
        self.server.stop()

    def wait(self):
        """Wait for the service to stop serving this API.

        :returns: None
        """
        self.server.wait()

    def reset(self):
        """Reset server greenpool size to default.

        :returns: None
        """
        self.server.reset()
