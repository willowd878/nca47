'''
Created on Feb 24, 2016

@author: yudazhao
'''
from oslo_config import cfg
from nca47.common import service as nca47_service
from nca47.manager import service
import sys
sys.path.append('/vagrant/nca47-svn')

CONF = cfg.CONF


def main():
    nca47_service.prepare_service(sys.argv)
    # Build and start the WSGi app
    launcher = nca47_service.process_launcher()

    server = service.DNSService(topic='dns_manager')
    launcher.launch_service(server)
    launcher.wait()

if __name__ == '__main__':
    sys.exit(main())
