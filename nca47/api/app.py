from oslo_config import cfg
import oslo_middleware.cors as cors_middleware
import pecan

from nca47.api import acl
from nca47.api import config
from nca47.api import hooks
from nca47.common.i18n import _


api_opts = [
    cfg.StrOpt(
        'auth_strategy',
        default='keystone',
        choices=['noauth', 'keystone'],
        help=_('Authentication strategy used by nca-api. "noauth" should '
               'not be used in a production environment because all '
               'authentication will be disabled.')),
    cfg.BoolOpt('debug_tracebacks_in_api',
                default=False,
                help=_('Return server tracebacks in the API response for any '
                       'error responses. WARNING: this is insecure '
                       'and should not be used in a production environment.')),
    cfg.BoolOpt('pecan_debug',
                default=False,
                help=_('Enable pecan debug mode. WARNING: this is insecure '
                       'and should not be used in a production environment.')),
]

CONF = cfg.CONF
CONF.register_opts(api_opts)


def get_pecan_config():
    """
    Set up the pecan configuration.
    """
    filename = config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(pecan_config=None):

    if not pecan_config:
        pecan_config = get_pecan_config()

    app_hooks = [hooks.ContextHook(pecan_config.app.acl_public_routes)]
    pecan.configuration.set_config(dict(pecan_config), overwrite=True)

    app = pecan.make_app(
        pecan_config.app.root,
        hooks=app_hooks,
    )

    app = acl.install(app, cfg.CONF, pecan_config.app.acl_public_routes)

    app = cors_middleware.CORS(app, CONF)

    return app
