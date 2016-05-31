import sqlalchemy as sa
from nca47.db.sqlalchemy.models import base as model_base
from nca47.objects import attributes as attr

HasTenant = model_base.HasTenant
HasId = model_base.HasId
HasStatus = model_base.HasStatus
HasOperationMode = model_base.HasOperationMode
JsonEncodedList = model_base.JsonEncodedList


class realserver(model_base.BASE, HasId, HasOperationMode):
    """Represents a dns zone."""

    __tablename__ = 'lb_realserver_info'

    tenant_id = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vnetwork_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    environment_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    application = sa.Column(sa.String(attr.NAME_MAX_LEN))
    node = sa.Column(sa.String(attr.NAME_MAX_LEN))
    realservername = sa.Column(sa.String(attr.NAME_MAX_LEN))
    rip = sa.Column(sa.String(attr.IP_LEN))
    batch = sa.Column(sa.String(attr.TENANT_ID_MAX_LEN))
    command_input = sa.Column(JsonEncodedList, default=[])


class lb_group(model_base.BASE, HasId, HasOperationMode):
    """Represents a dns zone."""

    __tablename__ = 'lb_group_info'

    tenant_id = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vnetwork_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    environment_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    application = sa.Column(sa.String(attr.NAME_MAX_LEN))
    node = sa.Column(sa.String(attr.NAME_MAX_LEN))
    batch = sa.Column(sa.String(attr.TENANT_ID_MAX_LEN))
    command_input = sa.Column(JsonEncodedList, default=[])
    realservername = sa.Column(JsonEncodedList, default=[])
    groupname = sa.Column(sa.String(attr.NAME_MAX_LEN))


class lb_vip(model_base.BASE, HasId, HasOperationMode):
    """Represents a dns zone."""

    __tablename__ = 'lb_vip_info'
    tenant_id = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vnetwork_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    environment_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    application = sa.Column(sa.String(attr.NAME_MAX_LEN))
    node = sa.Column(sa.String(attr.NAME_MAX_LEN))
    batch = sa.Column(sa.String(attr.TENANT_ID_MAX_LEN))
    command_input = sa.Column(JsonEncodedList, default=[])
    virtualservername = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vip = sa.Column(sa.String(attr.TYPES_LEN))
    virtualname = sa.Column(sa.String(attr.NAME_MAX_LEN))


class lb_service(model_base.BASE, HasId, HasOperationMode):
    """Represents a dns zone."""

    __tablename__ = 'lb_service_info'
    virtualservername = sa.Column(sa.String(attr.NAME_MAX_LEN))
    groupname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vport = sa.Column(sa.String(attr.TTL_LEN))
    rport = sa.Column(sa.String(attr.TTL_LEN))
    pbindtype = sa.Column(sa.String(attr.NAME_MAX_LEN))
    dbindtype = sa.Column(sa.String(attr.NAME_MAX_LEN))
    ptmouttime = sa.Column(sa.String(attr.NAME_MAX_LEN))
    metrictype = sa.Column(sa.String(attr.NAME_MAX_LEN))
    command_input = sa.Column(JsonEncodedList, default=[])
    batch = sa.Column(sa.String(attr.TENANT_ID_MAX_LEN))
