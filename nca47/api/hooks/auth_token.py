import re

from keystonemiddleware import auth_token
from oslo_log import log

from nca47.common import exception
from nca47.common.i18n import _
from nca47.common import utils

LOG = log.getLogger(__name__)


class AuthTokenMiddleware(auth_token.AuthProtocol):
    """A wrapper on Keystone auth_token middleware.

    Does not perform verification of authentication tokens
    for public routes in the API.

    """
    def __init__(self, app, conf, public_api_routes=[]):
        self._nca_app = app
        # TODO(mrda): Remove .xml and ensure that doesn't result in a
        # 401 Authentication Required instead of 404 Not Found
        route_pattern_tpl = '%s(\.json|\.xml)?$'

        try:
            self.public_api_routes = [re.compile(route_pattern_tpl % route_tpl)
                                      for route_tpl in public_api_routes]
        except re.error as e:
            msg = _('Cannot compile public API routes: %s') % e

            LOG.error(msg)
            raise exception.ConfigInvalid(error_msg=msg)

        super(AuthTokenMiddleware, self).__init__(app, conf)

    def __call__(self, env, start_response):
        path = utils.safe_rstrip(env.get('PATH_INFO'), '/')

        # The information whether the API call is being performed against the
        # public API is required for some other components. Saving it to the
        # WSGI environment is reasonable thereby.
        env['is_public_api'] = any(map(lambda pattern: re.match(pattern, path),
                                       self.public_api_routes))

        if env['is_public_api']:
            return self._nca_app(env, start_response)

        return super(AuthTokenMiddleware, self).__call__(env, start_response)
