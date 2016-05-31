from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import Vres_Agent_Vfw_View as vfwView
from nca47.objects import base
from nca47.objects import fields as object_fields


class Vres_Agent_Vfw_View(base.Nca47Object):
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
        'vfw_id': object_fields.StringField(),
        'vfw_name': object_fields.StringField(),
        'vfw_info': object_fields.ListOfStringsField(),
        'vfw_type': object_fields.StringField(),
        'network_zone_name': object_fields.StringField(),
        'network_zone_class': object_fields.StringField(),
        'protection_class': object_fields.StringField()
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(Vres_Agent_Vfw_View, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(agent_vfw_zone, db_agent_vfw_zone):
        """Converts a database entity to a formal
        :class:`Vres_Agent_Vfw_View` object.
        :param agent_vfw_zone: An object of
        class:`Vres_Agent_Vfw_View`.
        :param db_agent_vfw_zone: A DB model of a
        vres_Vres_Agent_Vfw_Viewagent_view.
        :return: a :class:`NCA_agent` object.
        """
        for field in agent_vfw_zone.fields:
            agent_vfw_zone[field] = db_agent_vfw_zone[field]

        agent_vfw_zone.obj_reset_changes()
        return agent_vfw_zone

    def get_objects(self, context, **values):
        objects = self.db_api.get_objects(vfwView, **values)
        return objects
