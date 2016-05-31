import sqlalchemy as sa

from nca47.db.sqlalchemy.models import base as model_base
from nca47.objects import attributes as attr

HasTenant = model_base.HasTenant
HasId = model_base.HasId
HasStatus = model_base.HasStatus
HasOperationMode = model_base.HasOperationMode
JsonEncodedList = model_base.JsonEncodedList


class DnsServer(model_base.BASE, HasId, HasOperationMode):
    """Represents a dns server."""

    name = sa.Column(sa.String(attr.NAME_MAX_LEN))


class Zone(model_base.BASE, HasId, HasOperationMode):
    """Represents a dns zone."""

    __tablename__ = 'dns_zone_info'

    zone_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    tenant_id = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vres_id = sa.Column(sa.String(attr.NAME_MAX_LEN))
    masters = sa.Column(JsonEncodedList, default=[])
    slaves = sa.Column(JsonEncodedList, default=[])
    renewal = sa.Column(sa.String(attr.NAME_MAX_LEN))
    default_ttl = sa.Column(sa.String(attr.NAME_MAX_LEN))
    owners = sa.Column(JsonEncodedList, default=[])
    ad_controller = sa.Column(sa.String(attr.NAME_MAX_LEN))
    comment = sa.Column(sa.String(attr.NAME_MAX_LEN))


class ZoneRecord(model_base.BASE, HasId, HasOperationMode):
    """Represents a dns zone record."""

    __tablename__ = 'dns_rrs_info'
    zone_id = sa.Column(sa.String(attr.UUID_LEN))
    rrs_id = sa.Column(sa.String(attr.NAME_MAX_LEN))
    rrs_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    type = sa.Column(sa.String(attr.NAME_MAX_LEN))
    klass = sa.Column(sa.String(attr.NAME_MAX_LEN))
    ttl = sa.Column(sa.String(attr.NAME_MAX_LEN))
    rdata = sa.Column(sa.String(attr.NAME_MAX_LEN))
    tenant_id = sa.Column(sa.String(attr.NAME_MAX_LEN))
