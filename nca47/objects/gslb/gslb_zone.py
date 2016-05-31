from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import GslbZoneInfo
from nca47.objects import base
from nca47.objects import fields as object_fields
from nca47.common.exception import HaveSameObject
from nca47.common.exception import IsNotExistError


class GslbZone(base.Nca47Object):
    VERSION = '1.0'
    fields = {
        'name': object_fields.StringField(),
        'devices': object_fields.ListOfStringsField(),
        'syn_server': object_fields.StringField(),
        'enable': object_fields.StringField(),
        'gslb_zone_id': object_fields.StringField(),
        'tenant_id': object_fields.StringField()
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(GslbZone, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(dns_gslb_zone, db_dns_gslb_zone):
        """Converts a database entity to a formal :class:`GslbZone` object.

        :param dns_zone: An object of :class:`GslbZone`.
        :param db_dns_zone: A DB model of a GslbZone.
        :return: a :class:`GslbZone` object.
        """
        for field in dns_gslb_zone.fields:
            dns_gslb_zone[field] = db_dns_gslb_zone[field]

        dns_gslb_zone.obj_reset_changes()
        return dns_gslb_zone

    def create(self, context, values):
        value = {}
        value["name"] = values["name"]
        value["tenant_id"] = values["tenant_id"]
        obj_old = self.get_objects(context, **value)
        if len(obj_old) != 0:
            raise HaveSameObject(param_name=value["name"])
        gslb_zone = self.db_api.create(GslbZoneInfo, values)
        return gslb_zone

    def update(self, context, zone_id, values):
        value = {}
        value["id"] = zone_id
        obj_old = self.get_objects(context, **value)
        if len(obj_old) == 0:
            raise IsNotExistError(param_name=zone_id)
        gslb_zone = self.db_api.update_object(GslbZoneInfo, zone_id, values)
        return gslb_zone

    def delete(self, context, zone_id):
        value = {}
        value["id"] = zone_id
        obj_old = self.get_objects(context, **value)
        if len(obj_old) == 0:
            raise IsNotExistError(param_name=value["id"])
        gslb_zone = self.db_api.delete_object(GslbZoneInfo, zone_id)
        return gslb_zone

    def get_objects(self, context, **values):
        values["deleted"] = False
        gslb_zone = self.db_api.get_objects(GslbZoneInfo, **values)
        return gslb_zone

    def get_object(self, context, **values):
        values["deleted"] = False
        try:
            gslb_zone = self.db_api.get_object(GslbZoneInfo, **values)
        except Exception:
            raise IsNotExistError(param_name=values["id"])
        return gslb_zone

    def get_object_one(self, context, **values):
        # get one information of gslb_zone
        gslb_zone = self.db_api.get_object(GslbZoneInfo, **values)
        return gslb_zone

    def get_all_objects_by_conditions(self, context, like_dic, search_dic):
        gslb_zone = self.db_api.get_all_objects(GslbZoneInfo, like_dic,
                                                search_dic)
        return gslb_zone
