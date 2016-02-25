import sqlalchemy as sa

from nca47.db.sqlalchemy.models import base as model_base
from nca47.objects import attributes as attr


HasTenant = model_base.HasTenant
HasId = model_base.HasId
HasStatus = model_base.HasStatus


class DnsServer(model_base.BASE, HasId):
    """Represents a dns server."""

    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
