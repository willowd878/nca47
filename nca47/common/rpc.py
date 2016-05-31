from oslo_config import cfg
import oslo_messaging as messaging

from nca47.common import context as nca47_context
from nca47.common import exception
from oslo_messaging.rpc import dispatcher as rpc_dispatcher

CONF = cfg.CONF
TRANSPORT = None
NOTIFIER = None

ALLOWED_EXMODS = [
    exception.__name__,
]
EXTRA_EXMODS = []

TRANSPORT_ALIASES = {
    'nca47.common.rpc.impl_kombu': 'rabbit',
    'nca47.common.rpc.impl_qpid': 'qpid',
    'nca47.common.rpc.impl_zmq': 'zmq',
    'nca47.rpc.impl_kombu': 'rabbit',
    'nca47.rpc.impl_qpid': 'qpid',
    'nca47.rpc.impl_zmq': 'zmq',
}


def init(conf):
    global TRANSPORT, NOTIFIER
    exmods = get_allowed_exmods()
    TRANSPORT = messaging.get_transport(conf, allowed_remote_exmods=exmods,
                                        aliases=TRANSPORT_ALIASES)

    serializer = RequestContextSerializer(messaging.JsonPayloadSerializer())
    NOTIFIER = messaging.Notifier(TRANSPORT, serializer=serializer)


def cleanup():
    global TRANSPORT, NOTIFIER
    assert TRANSPORT is not None
    assert NOTIFIER is not None
    TRANSPORT.cleanup()
    TRANSPORT = NOTIFIER = None


def initialized():
    return None not in [TRANSPORT, NOTIFIER]


def set_defaults(control_exchange):
    messaging.set_transport_defaults(control_exchange)


def add_extra_exmods(*args):
    EXTRA_EXMODS.extend(args)


def clear_extra_exmods():
    del EXTRA_EXMODS[:]


def get_allowed_exmods():
    return ALLOWED_EXMODS + EXTRA_EXMODS


class RequestContextSerializer(messaging.Serializer):
    def __init__(self, base):
        self._base = base

    def serialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.serialize_entity(context, entity)

    def deserialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.deserialize_entity(context, entity)

    def serialize_context(self, context):
        return context

    def deserialize_context(self, context):
        return nca47_context.RequestContext.from_dict(context)


class RPCDispatcher(rpc_dispatcher.RPCDispatcher):
    def _dispatch(self, *args, **kwds):
        try:
            return super(RPCDispatcher, self)._dispatch(*args, **kwds)
        except Exception as e:
            if getattr(e, 'expected', False):
                raise rpc_dispatcher.ExpectedException()
            else:
                raise


def get_transport_url(url_str=None):
    return messaging.TransportURL.parse(CONF, url_str, TRANSPORT_ALIASES)


def get_client(target, version_cap=None, serializer=None):
    assert TRANSPORT is not None
    serializer = RequestContextSerializer(serializer)
    return messaging.RPCClient(TRANSPORT,
                               target,
                               version_cap=version_cap,
                               serializer=serializer)


def get_server(target, endpoints, serializer=None):
    assert TRANSPORT is not None
    serializer = RequestContextSerializer(serializer)
    return messaging.get_rpc_server(TRANSPORT,
                                    target,
                                    endpoints,
                                    executor='threading',
                                    serializer=serializer)


def get_notifier(service=None, host=None, publisher_id=None):
    assert NOTIFIER is not None
    if not publisher_id:
        publisher_id = "%s.%s" % (service, host or CONF.host)
    return NOTIFIER.prepare(publisher_id=publisher_id)
