import sqlalchemy as sa

from nca47.db.sqlalchemy.models import base as model_base
from nca47.objects import attributes as attr


HasTenant = model_base.HasTenant
HasId = model_base.HasId
HasStatus = model_base.HasStatus
HasOperationMode = model_base.HasOperationMode


class OperationHistory(model_base.BASE, HasId, HasOperationMode):
    """Represents a dns zone."""

    __tablename__ = 'nca_operation_history'

    config_id = sa.Column(sa.String(attr.NAME_MAX_LEN))
    input = sa.Column(sa.String(attr.INPUT_MAX_LEN))
    operation_type = sa.Column(sa.String(attr.NAME_MAX_LEN))
    operation_time = sa.Column(sa.DateTime())
    operation_status = sa.Column(sa.String(attr.NAME_MAX_LEN))
