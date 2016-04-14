from nca47.db import api as db_api
from nca47.objects import base
from nca47.objects import fields as object_fields
from nca47.db.sqlalchemy.models import VLAN


class FwVlanInfo(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'vlan_id': object_fields.StringField(),
        'ipaddr': object_fields.StringField(),
        'ifnames': object_fields.ListOfStringsField(),
        'vres_id': object_fields.StringField()
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(FwVlanInfo, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(fw_vlan_info, db_fw_vlan_info):
        """Converts a database entity to a formal :class:`VLAN` object.

        :param fw_vlan_info: An object of :class:`VLAN`.
        :param db_fw_vlan_info: A DB model of a VLAN.
        :return: a :class:`VLAN` object.
        """
        for field in fw_vlan_info.fields:
            fw_vlan_info[field] = db_fw_vlan_info[field]

        fw_vlan_info.obj_reset_changes()
        return fw_vlan_info

    def create(self, context, values):
        zone = self.db_api.create(VLAN, values)
        return zone

    def update(self, context, id, values):
        record = self.db_api.update_object(VLAN, id, values)
        return record

    def delete(self, context, id):
        record = self.db_api.delete_object(VLAN, id)
        return record

    def get_objects(self, context, **values):
        record = self.db_api.get_objects(VLAN, **values)
        return record

    def get_object(self, context, **values):
        record = self.db_api.get_object(VLAN, **values)
        return record
