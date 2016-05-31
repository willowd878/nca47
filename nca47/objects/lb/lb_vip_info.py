from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import lb_vip as vip
from nca47.objects import base
from nca47.objects import fields as object_fields


class lb_vip_object(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'tenant_id': object_fields.StringField(),
        'vnetwork_name': object_fields.StringField(),
        'environment_name':  object_fields.StringField(),
        'application': object_fields.StringField(),
        'node': object_fields.StringField(),
        'batch': object_fields.StringField(),
        'command_input': object_fields.ListOfStringsField(),
        'virtualservername': object_fields.StringField(),
        'vip': object_fields.StringField(),
        'virtualname': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(lb_vip_object, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(lb_vip, db_lb_vip):
        """Converts a database entity to a formal :class:`lb_vip_object` object.

        :param lb_vip: An object of :class:`lb_vip_object`.
        :param db_lb_vip: A DB model of a lb_vip_object.
        :return: a :class:`lb_vip_object` object.
        """
        for field in lb_vip.fields:
            lb_vip[field] = db_lb_vip[field]

        lb_vip.obj_reset_changes()
        return lb_vip

    def create(self, context, values):
        vip_out = self.db_api.create(vip, values)
        return vip_out

    def get_objects(self, context, **values):
        vip_get = self.db_api.get_objects(vip, **values)
        return vip_get
