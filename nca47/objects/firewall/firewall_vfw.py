from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import VFW as VfwModel
from nca47.objects import base
from nca47.objects import fields as object_fields


class VFW(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'vfw_name': object_fields.StringField(),
        'vfw_type': object_fields.StringField(),
        'vfw_info':  object_fields.ListOfStringsField(),
        'dc_name': object_fields.StringField(),
        'network_zone_name': object_fields.StringField(),
        'network_zone_class': object_fields.StringField(),
        'protection_class': object_fields.StringField(),
        'vres_id': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(VFW, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(dns_zone, db_dns_zone):
        """Converts a database entity to a formal :class:`VFW` object.

        :param dns_zone: An object of :class:`VFW`.
        :param db_dns_zone: A DB model of a VFW.
        :return: a :class:`VFW` object.
        """
        for field in dns_zone.fields:
            dns_zone[field] = db_dns_zone[field]

        dns_zone.obj_reset_changes()
        return dns_zone

    def create(self, context, values):
        vfw = self.db_api.create(VfwModel, values)
        return vfw

    def update(self, context, id, values):
        vfw = self.db_api.update_object(VfwModel, id, values)
        return vfw

    def get_object(self, context, **values):
        vfw = self.db_api.get_object(VfwModel, **values)
        return vfw

    def delete(self, context, id):
        vfw = self.db_api.delete_object(VfwModel, id)
        return vfw

    def get_objects(self, context, **values):
        vfw = self.db_api.get_objects(VfwModel, **values)
        return vfw

    def get_all_objects(self, context, values):
        vfw = self.db_api.get_all_objects(VfwModel, values)
        return vfw

    def get_all_objects_by_conditions(self, context, like_dic, search_dic):
        vfws = self.db_api.get_all_objects_by_conditions(VfwModel,
                                                         like_dic, search_dic)
        return vfws
