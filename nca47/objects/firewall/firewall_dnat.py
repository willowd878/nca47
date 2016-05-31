from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import Dnat as DnatModel
from nca47.objects import base
from nca47.objects import fields as object_fields


class Dnat(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'name': object_fields.StringField(),
        'inifname': object_fields.StringField(),
        'wanip': object_fields.StringField(),
        'wantcpports': object_fields.ListOfStringsField(),
        'wanudpports': object_fields.ListOfStringsField(),
        'lanipstart': object_fields.StringField(),
        'lanipend': object_fields.StringField(),
        'lanport': object_fields.StringField(),
        'slot': object_fields.StringField(),
        'vfwname': object_fields.StringField(),
        'vfw_id': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(Dnat, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(dnat, db_dnat):
        """Converts a database entity to a formal :class:`Dnat` object.

        :param dns_zone: An object of :class:`Dnat`.
        :param db_dns_zone: A DB model of a Dnat.
        :return: a :class:`Dnat` object.
        """
        for field in dnat.fields:
            dnat[field] = db_dnat[field]

        dnat.obj_reset_changes()
        return dnat

    def create(self, context, values):
        dnat = self.db_api.create(DnatModel, values)
        return dnat

    def update(self, context, id, values):
        dnat = self.db_api.update_object(DnatModel, id, values)
        return dnat

    def get_object(self, context, **values):
        dnat = self.db_api.get_object(DnatModel, **values)
        return dnat

    def delete(self, context, id):
        dnat = self.db_api.delete_object(DnatModel, id)
        return dnat

    def get_objects(self, context, **values):
        dnat = self.db_api.get_objects(DnatModel, **values)
        return dnat

    def get_all_objects_by_conditions(self, context, like_dic, search_dic):
        dnats = self.db_api.get_all_objects_by_conditions(DnatModel,
                                                          like_dic,
                                                          search_dic)
        return dnats
