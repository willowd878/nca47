import sqlalchemy as sa

from nca47.db.sqlalchemy.models import base as model_base
from nca47.objects import attributes as attr


HasTenant = model_base.HasTenant
HasId = model_base.HasId
HasStatus = model_base.HasStatus
HasOperationMode = model_base.HasOperationMode


class Agent(model_base.BASE, HasId, HasOperationMode):
    """Represents a NCA_AGENT_INFO."""
    __tablename__ = 'nca_agent_info'
    agent_id = sa.Column(sa.String(attr.UUID_LEN))
    agent_ip = sa.Column(sa.String(attr.IP_LEN))
    agent_nat_ip = sa.Column(sa.String(attr.IP_LEN))
    dc_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    network_zone = sa.Column(sa.String(attr.NAME_MAX_LEN))
    agent_type = sa.Column(sa.String(attr.NAME_MAX_LEN))
    availiable = sa.Column(sa.Boolean())
    status = sa.Column(sa.Boolean())
    update_time = sa.Column(sa.DateTime())
    operation_fro = sa.Column(sa.String(attr.UUID_LEN))


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
