from oslo_log import log as logging
import json
# from oslo_serialization import jsonutils as json
from nca47.common import exception
from nca47.common.i18n import _LI
from nca47.common.i18n import _LW
from nca47.common.i18n import _LE

from nca47.db import api as db_api
from nca47.manager import rpcapi
from nca47.manager import db_common

LOG = logging.getLogger(__name__)

CLI_MANAGER = None


class CLIManager(object):
    """
    Run commands in command line interface operation handler class, using
    for handle client requests,  validate parameters whether is legal,
    handling DB operations and calling rpc client's corresponding method
    to send messaging to agent endpoints
    """

    def __init__(self):
        self.db_common = db_common.DBCommon.get_instance()
        self.db_api = db_api.get_instance()
        self.rpc_api = rpcapi.CLIManagerAPI.get_instance()

    @classmethod
    def get_instance(cls):
        global CLI_MANAGER
        if not CLI_MANAGER:
            CLI_MANAGER = cls()
        return CLI_MANAGER

    def execute_commands(self, context, commands):
        tenant_id = commands['tenant_id']
        net_zone = commands['network_zone']
        dc_name = commands['dc_name']
        agent_type = commands['agent_type']
        view_obj = self.db_common.get_vres_agent_view(context,
                                                      tenant_id=tenant_id,
                                                      agent_type=agent_type,
                                                      network_zone=net_zone,
                                                      dc_name=dc_name)
        vres_id = view_obj['vres_id']
        agent_ip = view_obj['agent_ip']
        # insert operation history
        commands_str = json.dumps(commands)
        # to do work-- when run command faild, but early commands have been
        # executed how to record the corresponding history info
        history = self.db_common.insert_operation_history(context,
                                                          vres_id=vres_id,
                                                          input=commands_str,
                                                          method='EXECUTE',
                                                          status='FAILED')
        self.rpc_api.reload_topic(agent_ip)

        response = self.rpc_api.execute_commands(context, commands)
        return response
