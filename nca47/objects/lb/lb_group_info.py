from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import lb_group as group
from nca47.objects import base
from nca47.objects import fields as object_fields


class lb_group_object(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'tenant_id': object_fields.StringField(),
        'vnetwork_name': object_fields.StringField(),
        'environment_name':  object_fields.StringField(),
        'application': object_fields.StringField(),
        'node': object_fields.StringField(),
        'batch': object_fields.StringField(),
        'command_input': object_fields.ListOfStringsField(),
        'realservername': object_fields.ListOfStringsField(),
        'groupname': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(lb_group_object, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(group, db_group):
        """Converts a database entity to a formal :class:`lb_group_object` object.

        :param group: An object of :class:`lb_group_object`.
        :param db_group: A DB model of a lb_group_object.
        :return: a :class:`lb_group_object` object.
        """
        for field in group.fields:
            group[field] = db_group[field]

        group.obj_reset_changes()
        return group

    def create(self, context, values):
        group_obj = self.db_api.create(group, values)
        return group_obj

    def get_objects(self, context, **values):
        group_obj = self.db_api.get_objects(group, **values)
        return group_obj

    def get_all_objects(self, context, **values):
        sql = values["sql"]
        group_obj = self.db_api.get_all_objects(group, sql)
        return group_obj
