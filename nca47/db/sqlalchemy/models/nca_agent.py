import sqlalchemy as sa

from nca47.db.sqlalchemy.models import base as model_base
from nca47.objects import attributes as attr


HasTenant = model_base.HasTenant
HasId = model_base.HasId
HasStatus = model_base.HasStatus
HasOperationMode = model_base.HasOperationMode
JsonEncodedList = model_base.JsonEncodedList


class Agent(model_base.BASE, HasId, HasOperationMode):
    """Represents a NCA_AGENT_INFO."""

    __tablename__ = 'nca_agent_info'
    agent_id = sa.Column(sa.String(attr.UUID_LEN))
    agent_ip = sa.Column(sa.String(attr.IP_LEN))
    agent_nat_ip = sa.Column(sa.String(attr.IP_LEN))
    dc_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    network_zone = sa.Column(sa.String(attr.NAME_MAX_LEN))
    agent_type = sa.Column(sa.String(attr.NAME_MAX_LEN))
    availiable = sa.Column(sa.String(attr.IP_LEN))
    update_time = sa.Column(sa.DateTime())


class VresInfo(model_base.BASE, HasId, HasOperationMode):
    """Represents a NCA_VRES_INFO."""

    __tablename__ = 'nca_vres_info'
    vres_id = sa.Column(sa.String(attr.UUID_LEN))
    vres_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    tenant_id = sa.Column(sa.String(attr.UUID_LEN))
    agent_id = sa.Column(sa.String(attr.IP_LEN))


class Vres_Agent_View(model_base.BASE, HasId):
    """Represents a vres_agent_view."""
    __tablename__ = 'vres_agent_view'
    agent_id = sa.Column(sa.String(attr.UUID_LEN))
    agent_ip = sa.Column(sa.String(attr.IP_LEN))
    agent_nat_ip = sa.Column(sa.String(attr.IP_LEN))
    dc_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    network_zone = sa.Column(sa.String(attr.NAME_MAX_LEN))
    agent_type = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vres_id = sa.Column(sa.String(attr.UUID_LEN))
    vres_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    tenant_id = sa.Column(sa.String(attr.UUID_LEN))


class Vres_Agent_Vfw_View(model_base.BASE, HasId):
    """Represents a view_vfw_vres_agent."""
    __tablename__ = 'view_vfw_vres_agent'
    agent_id = sa.Column(sa.String(attr.UUID_LEN))
    agent_ip = sa.Column(sa.String(attr.IP_LEN))
    agent_nat_ip = sa.Column(sa.String(attr.IP_LEN))
    dc_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    network_zone = sa.Column(sa.String(attr.NAME_MAX_LEN))
    agent_type = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vres_id = sa.Column(sa.String(attr.UUID_LEN))
    vres_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    tenant_id = sa.Column(sa.String(attr.UUID_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))
    vfw_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_info = sa.Column(JsonEncodedList, default=[])
    vfw_type = sa.Column(sa.String(attr.NAME_MAX_LEN))
    network_zone_name = sa.Column(sa.String(attr.INPUT_MAX_LEN))
    network_zone_class = sa.Column(sa.String(attr.INPUT_MAX_LEN))
    protection_class = sa.Column(sa.String(attr.INPUT_MAX_LEN))
