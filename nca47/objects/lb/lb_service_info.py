from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import lb_service as lb_ser_obj
from nca47.objects import base
from nca47.objects import fields as object_fields


class lb_server_object(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'virtualservername': object_fields.StringField(),
        'groupname': object_fields.StringField(),
        'vport': object_fields.StringField(),
        'rport': object_fields.StringField(),
        'command_input': object_fields.ListOfStringsField(),
        'pbindtype': object_fields.StringField(),
        'dbindtype': object_fields.StringField(),
        'ptmouttime': object_fields.StringField(),
        'metrictype': object_fields.StringField(),
        'batch': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(lb_server_object, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(lb_ser, db_lb_ser):
        """Converts a database entity to a formal :class:`lb_server_object` object.

        :param lb_ser: An object of :class:`lb_server_object`.
        :param db_lb_ser: A DB model of a lb_server_object.
        :return: a :class:`lb_server_object` object.
        """
        for field in lb_ser.fields:
            lb_ser[field] = db_lb_ser[field]

        lb_ser.obj_reset_changes()
        return lb_ser

    def create(self, context, values):
        lb_server = self.db_api.create(lb_ser_obj, values)
        return lb_server

    def get_objects(self, context, **values):
        lb_server = self.db_api.get_objects(lb_ser_obj, **values)
        return lb_server
