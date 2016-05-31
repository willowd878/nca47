from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import Vres_Agent_View as vresView
from nca47.objects import base
from nca47.objects import fields as object_fields


class Vres_Agent_View(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'agent_id': object_fields.StringField(),
        'agent_ip': object_fields.StringField(),
        'agent_nat_ip': object_fields.StringField(),
        'dc_name': object_fields.StringField(),
        'network_zone': object_fields.StringField(),
        'agent_type': object_fields.StringField(),
        'vres_id': object_fields.StringField(),
        'vres_name': object_fields.StringField(),
        'tenant_id': object_fields.StringField(),

    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(Vres_Agent_View, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(agent_zone, db_agent_zone):
        """Converts a database entity to a formal :class:`vres_agent_view` object.

        :param agent_zone: An object of :class:`vres_agent_view`.
        :param db_agent_zone: A DB model of a vres_agent_view.
        :return: a :class:`NCA_agent` object.
        """
        for field in agent_zone.fields:
            agent_zone[field] = db_agent_zone[field]

        agent_zone.obj_reset_changes()
        return agent_zone

    def get_objects(self, context, **values):
        objects = self.db_api.get_objects(vresView, **values)
        return objects

    def get_object(self, context, **values):
        object = self.db_api.get_object(vresView, **values)
        return object
