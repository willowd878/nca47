from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import ZoneRecord
from nca47.objects import base
from nca47.objects import fields as object_fields


class DnsZoneRrs(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'rrs_id': object_fields.StringField(),
        'zone_id': object_fields.StringField(),
        'rrs_name': object_fields.StringField(),
        'type': object_fields.ListOfStringsField(),
        'klass': object_fields.StringField(),
        'ttl': object_fields.StringField(),
        'rdata': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(DnsZoneRrs, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(dns_zone_rrs, db_dns_zone_rrs):
        """Converts a database entity to a formal :class:`DnsZone` object.

        :param dns_zone: An object of :class:`DnsZone`.
        :param db_dns_zone: A DB model of a DnsZone.
        :return: a :class:`DnsZone` object.
        """
        for field in dns_zone_rrs.fields:
            dns_zone_rrs[field] = db_dns_zone_rrs[field]

        dns_zone_rrs.obj_reset_changes()
        return dns_zone_rrs

    def create(self, context, values):
        zone = self.db_api.create(ZoneRecord, values)
        return zone

    def update(self, context, id, values):
        record = self.db_api.update_object(ZoneRecord, id, values)
        return record

    def delete(self, context, id):
        record = self.db_api.delete_object(ZoneRecord, id)
        return record

    def get_objects(self, context, **values):
        record = self.db_api.get_objects(ZoneRecord, **values)
        return record

    def get_object(self, context, **values):
        record = self.db_api.get_object(ZoneRecord, **values)
        return record
