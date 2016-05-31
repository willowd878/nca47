from oslo_config import cfg

from nca47.common import rpc


def parse_args(argv, default_config_files=None):
    rpc.set_defaults(control_exchange='nca47')
    cfg.CONF(argv[1:],
             project='nca47',
             # version=version.version_info.release_string(),
             default_config_files=default_config_files)
    rpc.init(cfg.CONF)
