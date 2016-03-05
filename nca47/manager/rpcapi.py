from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from nca47.common import rpc

from nca47.common.i18n import _LI

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

DNS_MANAGER_API = None


class DNSManagerAPI(object):
    """
    Client side of the DNS manager RPC API.

    API version history:

        1.0 - Initial version
    """
    RPC_API_VERSION = '1.0'

    def __init__(self, topic='dns_manager'):
        rpc.init(CONF)

        target = messaging.Target(topic=topic,  version=self.RPC_API_VERSION)
        self.client = rpc.get_client(target, version_cap=self.RPC_API_VERSION)

    @classmethod
    def get_instance(cls):
        """
        The rpc.get_client() which is called upon the API object initialization
        will cause a assertion error if the designate.rpc.TRANSPORT isn't setup
        by rpc.init() before.

        This fixes that by creating the rpcapi when demanded.
        """
        global DNS_MANAGER_API
        if not DNS_MANAGER_API:
            DNS_MANAGER_API = cls()
        return DNS_MANAGER_API

    # Zone Methods
    def create_zone(self, context, zone):
        LOG.info(_LI("create_zone: Calling central's create_zone."))
        return self.client.call(context, 'create_zone', zone=zone)

    def get_zone(self, context, zone_id):
        LOG.info(_LI("get_zone: Calling central's get_zone."))
        return self.client.call(context, 'get_zone', zone_id=zone_id)

    def update_zone(self, context, zone):
        LOG.info(_LI("update_zone: Calling central's update_zone."))
        return self.client.call(context, 'update_zone', zone=zone)

    def delete_zone(self, context, zone_id):
        LOG.info(_LI("delete_zone: Calling central's delete_zone."))
        return self.client.call(context, 'delete_zone', zone_id=zone_id)
