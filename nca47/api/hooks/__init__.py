from pecan import hooks

from nca47.common import context
from nca47.common import policy

class ContextHook(hooks.PecanHook):
    """Configures a request context and attaches it to the request.

    The following HTTP request headers are used:

    X-User-Id or X-User:
        Used for context.user_id.

    X-Tenant-Id or X-Tenant:
        Used for context.tenant.

    X-Auth-Token:
        Used for context.auth_token.

    X-Roles:
        Used for setting context.is_admin flag to either True or False.
        The flag is set to True, if X-Roles contains either an administrator
        or admin substring. Otherwise it is set to False.

    """

    def __init__(self, public_api_routes):
        self.public_api_routes = public_api_routes
        super(ContextHook, self).__init__()

    def before(self, state):
        headers = state.request.headers
        token_info = headers.environ['keystone.token_info']['access']
        tenant_info = token_info['token']['tenant']
        user_info = token_info['user']

        # Do not pass any token with context for noauth mode
        auth_token = headers.get('X-Auth-Token')

        creds = {
            'user': headers.get('X-User') or headers.get('X-User-Id'),
            'tenant': headers.get('X-Tenant') or headers.get('X-Tenant-Id'),
            'domain_id': headers.get('X-User-Domain-Id'),
            'domain_name': headers.get('X-User-Domain-Name'),
            'auth_token': auth_token,
            'roles': headers.get('X-Roles', '').split(','),
            'tenant_id': tenant_info['id'],
            'user_id': user_info['id']
        }

        is_admin = policy.enforce('admin_api', creds, creds)
        # is_public_api = state.request.environ.get('is_public_api', False)
        # show_password = policy.enforce('show_password', creds, creds)

        state.request.context = context.RequestContext(
            is_admin=is_admin,
            # is_public_api=is_public_api,
            # show_password=show_password,
            **creds)

    def after(self, state):
        if state.request.context == {}:
            # An incorrect url path will not create RequestContext
            return
        # NOTE(lintan): RequestContext will generate a request_id if no one
        # passing outside, so it always contain a request_id.
        request_id = state.request.context.request_id
        state.response.headers['Openstack-Request-Id'] = request_id
