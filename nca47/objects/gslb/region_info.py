from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import Region as RegionModel
from nca47.objects import base
from nca47.objects import fields as object_fields


class RegionInfo(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'tenant_id': object_fields.StringField(),
        'name': object_fields.StringField(),
        'region_id': object_fields.StringField(),
        'refcnt': object_fields.StringField(),
        'region_user': object_fields.ListOfStringsField,
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(RegionInfo, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(dns_region, db_dns_region):
        """Converts a database entity to a formal :class:`RegionInfo` object.

        :param dns_region: An object of :class:`RegionInfo`.
        :param db_dns_region: A DB model of a RegionInfo.
        :return: a :class:`RegionInfo` object.
        """
        for field in dns_region.fields:
            dns_region[field] = db_dns_region[field]

        dns_region.obj_reset_changes()
        return dns_region

    def create(self, context, values):
        region = self.db_api.create(RegionModel, values)
        return region

    def update(self, context, id, values):
        region = self.db_api.update_object(RegionModel, id, values)
        return region

    def get_object(self, context, **values):
        region = self.db_api.get_object(RegionModel, **values)
        return region

    def delete(self, context, id):
        region = self.db_api.delete_object(RegionModel, id)
        return region

    def get_objects(self, context, **values):
        regions = self.db_api.get_objects(RegionModel, **values)
        return regions

    def get_all_objects(self, context, values):
        regions = self.db_api.get_all_objects(RegionModel, values)
        return regions

    def get_all_objects_by_conditions(self, context, like_dic, search_dic):
        regions = self.db_api.get_all_objects_by_conditions(RegionModel,
                                                            like_dic,
                                                            search_dic)
        return regions
