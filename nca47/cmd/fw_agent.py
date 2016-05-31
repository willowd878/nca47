import sys
sys.path.append('/vagrant/nca47')

from nca47.agent.agentFlag import agent_config
from nca47.common import service as nca47_service
from nca47.manager import service


def main():
    nca47_service.prepare_service(sys.argv)
    launcher = nca47_service.process_launcher()
    agentinfo = agent_config.getAgent_config()
    server = service.FWService(topic='firewall_manager', agentinfo=agentinfo)
    launcher.launch_service(server)
    launcher.wait()

if __name__ == '__main__':
    sys.exit(main())
