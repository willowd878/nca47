import sys
sys.path.append('/vagrant/nca47')

from nca47.common import service as nca47_service
from nca47.manager import service
from nca47.agent.agentFlag import agent_config


def main():
    nca47_service.prepare_service(sys.argv)
    # Build and start the WSGi app
    launcher = nca47_service.process_launcher()
    # register agent host informations to agent service
    agentinfo = agent_config.getAgent_config()
    server = service.DNSService(topic='dns_manager', agentinfo=agentinfo)
    launcher.launch_service(server, workers=2)
    launcher.wait()

if __name__ == '__main__':
    sys.exit(main())
