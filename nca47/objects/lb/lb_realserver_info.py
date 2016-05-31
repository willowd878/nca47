from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import realserver as rserver
from nca47.objects import base
from nca47.objects import fields as object_fields


class lb_realServer_object(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'tenant_id': object_fields.StringField(),
        'vnetwork_name': object_fields.StringField(),
        'environment_name':  object_fields.StringField(),
        'application': object_fields.StringField(),
        'node': object_fields.StringField(),
        'realservername': object_fields.StringField(),
        'rip': object_fields.StringField(),
        'batch': object_fields.StringField(),
        'command_input': object_fields.ListOfStringsField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(lb_realServer_object, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(real_server, db_real_server):
        """Converts a database entity to a formal :class:`lb_realServer_object` object.

        :param real_server: An object of :class:`lb_realServer_object`.
        :param db_real_server: A DB model of a lb_realServer_object.
        :return: a :class:`lb_realServer_object` object.
        """
        for field in real_server.fields:
            real_server[field] = db_real_server[field]

        real_server.obj_reset_changes()
        return real_server

    def create(self, context, values):
        realServer = self.db_api.create(rserver, values)
        return realServer

    def get_objects(self, context, **values):
        realServer = self.db_api.get_objects(rserver, **values)
        return realServer
