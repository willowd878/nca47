import pecan

from nca47.api import config
from nca47.api import hooks


def get_pecan_config():
    """
    Set up the pecan configuration.
    """
    filename = config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(pecan_config=None):
    app_hooks = [hooks.ContextHook(pecan_config.app.acl_public_routes)]

    if not pecan_config:
        pecan_config = get_pecan_config()

    pecan.configuration.set_config(dict(pecan_config), overwrite=True)

    app = pecan.make_app(
        pecan_config.app.root,
        hooks=app_hooks,
    )

    return app
