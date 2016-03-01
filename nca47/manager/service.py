from oslo_config import cfg
from oslo_log import log as logging
from nca47.common import service
# from nca47.common import coordination
from nca47.common.i18n import _LI

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

RPC_API_VERSION = '1.0'


class Service(service.RPCService, service.Service):
    RPC_API_VERSION = '1.0'

    # Since the RPC Service class will be use for handle/reply all message
    # for every RPC client, so will initialize some keys
    def __init__(self, topic='', threads=None):
        self.rpc_topic = topic
        super(Service, self).__init__(threads=threads)

    @property
    def service_name(self):
        return self.rpc_topic

    def start(self):
        super(Service, self).start()

    # Zone Methods
    def create_zone(self, context, zone):
        LOG.info(_LI("create_zone: Replying rpc client's create_zone."))
        print 'create_zone'
        return 'create_zone'

    def get_zone(self, context, zone_id):
        LOG.info(_LI("get_zone: Replying rpc client's get_zone."))
        print 'get_zone'
        return 'get_zone'

    def update_zone(self, context, zone):
        LOG.info(_LI("update_zone: Replying rpc client's update_zone."))
        return 'update_zone'
        return 'update_zone'

    def delete_zone(self, context, zone_id):
        LOG.info(_LI("delete_zone: Replying rpc client's delete_zone."))
        return 'delete_zone'
        return 'delete_zone'
