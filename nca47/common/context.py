from oslo_context import context


class RequestContext(context.RequestContext):
    """Extends security contexts from the OpenStack common library."""

    def __init__(self, auth_token=None, domain_id=None, domain_name=None,
                 user=None, tenant=None, is_admin=False, is_public_api=False,
                 read_only=False, show_deleted=False, request_id=None,
                 roles=None, show_password=True,
                 tenant_id=None, user_id=None):
        """Stores several additional request parameters:

        :param domain_id: The ID of the domain.
        :param domain_name: The name of the domain.
        :param is_public_api: Specifies whether the request should be processed
                              without authentication.
        :param roles: List of user's roles if any.
        :param show_password: Specifies whether passwords should be masked
                              before sending back to API call.

        """
        self.is_public_api = is_public_api
        self.domain_id = domain_id
        self.domain_name = domain_name
        self.roles = roles or []
        self.show_password = show_password
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.is_admin = is_admin

        super(RequestContext, self).__init__(auth_token=auth_token,
                                             user=user, tenant=tenant,
                                             is_admin=is_admin,
                                             read_only=read_only,
                                             show_deleted=show_deleted,
                                             request_id=request_id)

    def to_dict(self):
        return {'auth_token': self.auth_token,
                'user': self.user,
                'tenant': self.tenant,
                'is_admin': self.is_admin,
                'read_only': self.read_only,
                'show_deleted': self.show_deleted,
                'request_id': self.request_id,
                'domain_id': self.domain_id,
                'roles': self.roles,
                'domain_name': self.domain_name,
                'show_password': self.show_password,
                'is_public_api': self.is_public_api}

    @classmethod
    def from_dict(cls, values):
        values.pop('user', None)
        values.pop('tenant', None)
        return cls(**values)
