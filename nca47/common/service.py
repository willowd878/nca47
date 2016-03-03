import socket
import abc
import six

from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log
import oslo_messaging as messaging
from oslo_service import service
from oslo_service import wsgi

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


@six.add_metaclass(abc.ABCMeta)
class Service(service.Service):
    """
    Service class to be shared among the diverse service inside of Designate.
    """
    def __init__(self, threads=None):
        threads = threads or 1000

        super(Service, self).__init__(threads)

        self._host = CONF.host
        # self._service_config = CONF['service:%s' % self.service_name]

        # NOTE(kiall): All services need RPC initialized, as this is used
        #              for clients AND servers. Hence, this is common to
        #              all Designate services.
        if not rpc.initialized():
            rpc.init(CONF)

    @abc.abstractproperty
    def service_name(self):
        pass

    def start(self):
        super(Service, self).start()

        LOG.info(_('Starting %(name)s service (version: %(version)s)'),
                 {'name': self.service_name,
                  'version': 'nca47 v1.0'})

    def stop(self):
        LOG.info(_('Stopping %(name)s service'), {'name': self.service_name})

        super(Service, self).stop()


class RPCService(object):
    """
    RPC Service mixin used by all Designate RPC Services
    """
    def __init__(self, *args, **kwargs):
        super(RPCService, self).__init__(*args, **kwargs)

        LOG.debug("Creating RPC Server on topic '%s'" % self._rpc_topic)
        self._rpc_server = rpc.get_server(
            messaging.Target(topic=self._rpc_topic, server=self._host),
            self._rpc_endpoints)

    @property
    def _rpc_endpoints(self):
        return [self]

    @property
    def _rpc_topic(self):
        return self.service_name

    def start(self):
        super(RPCService, self).start()

        LOG.debug("Starting RPC server on topic '%s'" % self._rpc_topic)
        self._rpc_server.start()

        # TODO(kiall): This probably belongs somewhere else, maybe the base
        #              Service class?
        self.notifier = rpc.get_notifier(self.service_name)

        for e in self._rpc_endpoints:
            if e != self and hasattr(e, 'start'):
                e.start()

    def stop(self):
        LOG.debug("Stopping RPC server on topic '%s'" % self._rpc_topic)

        for e in self._rpc_endpoints:
            if e != self and hasattr(e, 'stop'):
                e.stop()

        # Try to shut the connection down, but if we get any sort of
        # errors, go ahead and ignore them.. as we're shutting down anyway
        try:
            self._rpc_server.stop()
        except Exception:
            pass

        super(RPCService, self).stop()

    def wait(self):
        for e in self._rpc_endpoints:
            if e != self and hasattr(e, 'wait'):
                e.wait()

        super(RPCService, self).wait()


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
