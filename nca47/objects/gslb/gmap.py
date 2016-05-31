from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import GMapInfo as GMapModel
from nca47.objects import base
from nca47.objects import fields as object_fields


class GMap(base.Nca47Object):
    VERSION = '1.0'
    fields = {
        'gmap_id': object_fields.StringField(),
        'tenant_id': object_fields.StringField(),
        'name': object_fields.StringField(),
        'enable': object_fields.StringField(),
        'algorithm': object_fields.StringField(),
        'last_resort_pool': object_fields.StringField(),
        'gpool_list': object_fields.ListOfStringsField(),
    }

    def __init__(self, context=None, **kwargs):
        self.db_api = db_api.get_instance()
        super(GMap, self).__init__(context=None, **kwargs)

    @staticmethod
    def __from_db_object(dns_gmap, db_dns_gmap):
        """
        :param dns_syngroup:
        :param db_dns_syngroup:
        :return:
        """
        for field in dns_gmap.fields:
            dns_gmap[field] = db_dns_gmap
        dns_gmap.obj_reset_changes()
        return dns_gmap

    def create(self, context, values):
        gmap = self.db_api.create(GMapModel, values)
        return gmap

    def update(self, context, id, values):
        gmap = self.db_api.update_object(GMapModel, id, values)
        return gmap

    def get_object(self, context, **values):
        gmap = self.db_api.get_object(GMapModel, **values)
        return gmap

    def get_objects(self, context, **values):
        gmap = self.db_api.get_objects(GMapModel, **values)
        return gmap

    def delete(self, context, id):
        gmap = self.db_api.delete_object(GMapModel, id)
        return gmap

    def get_all_objects(self, context, str_sql):
        gmap = self.db_api.get_all_objects(GMapModel, str_sql)
        return gmap

    def get_all_objects_by_conditions(self, context, like_dic, search_dic):
        gmap = self.db_api.get_all_objects_by_conditions(GMapModel, like_dic,
                                                         search_dic)
        return gmap
