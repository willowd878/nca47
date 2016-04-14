from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import PacketFilter as PacketFilterModel
from nca47.objects import base
from nca47.objects import fields as object_fields


class PacketFilter(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'name': object_fields.StringField(),
        'srczonename': object_fields.StringField(),
        'dstzonename': object_fields.StringField(),
        'srcipobjnames': object_fields.ListOfStringsField(),
        'dstipobjnames': object_fields.ListOfStringsField(),
        'servicenames': object_fields.ListOfStringsField(),
        'action': object_fields.StringField(),
        'vfwname': object_fields.StringField(),
        'vfw_id': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(PacketFilter, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(filter, db_filter):
        """Converts a database entity to a formal:class:`PacketFilter` object.

        :param dns_zone: An object of :class:`PacketFilter`.
        :param db_dns_zone: A DB model of a PacketFilter.
        :return: a :class:`PacketFilter` object.
        """
        for field in filter.fields:
            filter[field] = db_filter[field]

        filter.obj_reset_changes()
        return filter

    def create(self, context, values):
        packetfilter = self.db_api.create(PacketFilterModel, values)
        return packetfilter

    def update(self, context, id, values):
        packetfilter = self.db_api.update_object(PacketFilterModel, id,
                                                 values)
        return packetfilter

    def get_object(self, context, **values):
        packetfilter = self.db_api.get_object(PacketFilterModel, **values)
        return packetfilter

    def delete(self, context, id):
        packetfilter = self.db_api.delete_object(PacketFilterModel, id)
        return packetfilter

    def get_objects(self, context, **values):
        packetfilter = self.db_api.get_objects(PacketFilterModel, **values)
        return packetfilter
