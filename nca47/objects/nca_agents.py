from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import Agent as agentZone
from nca47.objects import base
from nca47.objects import fields as object_fields


class AgentZone(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'agent_id': object_fields.StringField(),
        'agent_ip': object_fields.StringField(),
        'agent_nat_ip': object_fields.StringField(),
        'dc_name': object_fields.StringField(),
        'network_zone': object_fields.StringField(),
        'agent_type': object_fields.StringField(),
        'availiable': object_fields.BooleanField(),
        'status': object_fields.BooleanField(),
        'update_time': object_fields.DateTimeField(),
        'operation_fro': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(AgentZone, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(agent_zone, db_agent_zone):
        """Converts a database entity to a formal :class:`nca_agent` object.

        :param agent_zone: An object of :class:`AgentZone`.
        :param db_agent_zone: A DB model of a AgentZone.
        :return: a :class:`NCA_agent` object.
        """
        for field in agent_zone.fields:
            agent_zone[field] = db_agent_zone[field]

        agent_zone.obj_reset_changes()
        return agent_zone

    def create(self, context, values):
        zone = self.db_api.create(agentZone, values)
        return zone

    def update(self, context, id, values):
        zone = self.db_api.update_object(agentZone, id, values)
        return zone

    def get_object(self, context, **values):
        zone = self.db_api.get_object(agentZone, **values)
        return zone

    def delete(self, context, id):
        zone = self.db_api.delete_object(agentZone, id)
        return zone

    def get_objects(self, context, **values):
        zone = self.db_api.get_objects(agentZone, **values)
        return zone
