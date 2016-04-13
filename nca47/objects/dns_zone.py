from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import Zone as ZoneModel
from nca47.objects import base
from nca47.objects import fields as object_fields


class DnsZone(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'zone_id': object_fields.StringField(),
        'tenant_id': object_fields.StringField(),
        'zone_name': object_fields.StringField(),
        'vres_id': object_fields.StringField(),
        'masters': object_fields.ListOfStringsField(),
        'slaves': object_fields.ListOfStringsField(),
        'owners': object_fields.ListOfStringsField(),
        'ad_controller': object_fields.ListOfStringsField(),
        'default_ttl': object_fields.StringField(),
        'renewal': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(DnsZone, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(dns_zone, db_dns_zone):
        """Converts a database entity to a formal :class:`DnsZone` object.

        :param dns_zone: An object of :class:`DnsZone`.
        :param db_dns_zone: A DB model of a DnsZone.
        :return: a :class:`DnsZone` object.
        """
        for field in dns_zone.fields:
            dns_zone[field] = db_dns_zone[field]

        dns_zone.obj_reset_changes()
        return dns_zone

    def create(self, context, values):
        zone = self.db_api.create(ZoneModel, values)
        return zone

    def update(self, context, id, values):
        zone = self.db_api.update_object(ZoneModel, id, values)
        return zone

    def get_object(self, context, **values):
        zone = self.db_api.get_object(ZoneModel, **values)
        return zone

    def delete(self, context, id):
        zone = self.db_api.delete_object(ZoneModel, id)
        return zone

    def get_objects(self, context, **values):
        zone = self.db_api.get_objects(ZoneModel, **values)
        return zone
