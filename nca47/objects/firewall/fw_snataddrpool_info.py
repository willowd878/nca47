from nca47.db import api as db_api
from nca47.objects import base
from nca47.objects import fields as object_fields
from nca47.db.sqlalchemy.models.firewall import FwSnatAddrPool


class FwSnatAddrPoolInfo(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'id': object_fields.StringField(),
        'name': object_fields.StringField(),
        'ipstart': object_fields.StringField(),
        'ipend': object_fields.StringField(),
        'slotip': object_fields.StringField(),
        'vfwname': object_fields.StringField(),
        'vfw_id': object_fields.StringField(),
        'operation_fro': object_fields.StringField()
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(FwSnatAddrPoolInfo, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(fw_snataddrpool_info, db_fw_snataddrpool_info):
        """Converts a database entity to a formal :class:`FwSnatAddrPool`
        object.
        :param fw_snataddrpool_info: An object of :class:`FwSnatAddrPool`.
        :param fw_snataddrpool_info: A DB model of a FwSnatAddrPool.
        :return: a :class:`FwSnatAddrPool` object.
        """
        for field in fw_snataddrpool_info.fields:
            fw_snataddrpool_info[field] = db_fw_snataddrpool_info[field]

        fw_snataddrpool_info.obj_reset_changes()
        return fw_snataddrpool_info

    def create(self, context, values):
        snataddrpool = self.db_api.create(FwSnatAddrPool, values)
        return snataddrpool

    def delete(self, context, id_):
        snataddrpool = self.db_api.delete_object(FwSnatAddrPool, id_)
        return snataddrpool

    def get_object(self, context, **values):
        snataddrpool = self.db_api.get_object(FwSnatAddrPool, **values)
        return snataddrpool

    def get_objects(self, context, **values):
        snataddrpool = self.db_api.get_objects(FwSnatAddrPool, **values)
        return snataddrpool

    def update(self, context, id, values):
        snataddrpool = self.db_api.update_object(FwSnatAddrPool, id, values)
        return snataddrpool
