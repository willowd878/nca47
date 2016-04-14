from nca47.db import api as db_api
from nca47.objects import base
from nca47.objects import fields as object_fields
from nca47.db.sqlalchemy.models.firewall import ADDROBJ


class FwAddrObjInfo(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'id': object_fields.StringField(),
        'name': object_fields.StringField(),
        'ip': object_fields.StringField(),
        'expip': object_fields.StringField(),
        'vfwname': object_fields.StringField(),
        'vfw_id': object_fields.StringField(),
        'operation_fro': object_fields.StringField()
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(FwAddrObjInfo, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(fw_addrobj_info, db_fw_addrobj_info):
        """Converts a database entity to a formal :class:`ADDROBJ` object.

        :param fw_addrobj_info: An object of :class:`ADDROBJ`.
        :param fw_addrobj_info: A DB model of a ADDROBJ.
        :return: a :class:`ADDROBJ` object.
        """
        for field in fw_addrobj_info.fields:
            fw_addrobj_info[field] = db_fw_addrobj_info[field]

        fw_addrobj_info.obj_reset_changes()
        return fw_addrobj_info

    def create(self, context, values):
        addrobj = self.db_api.create(ADDROBJ, values)
        return addrobj

    def delete(self, context, id_):
        addrobj = self.db_api.delete_object(ADDROBJ, id_)
        return addrobj

    def get_object(self, context, **values):
        addrobj = self.db_api.get_object(ADDROBJ, **values)
        return addrobj

    def get_objects(self, context, **values):
        addrobj = self.db_api.get_objects(ADDROBJ, **values)
        return addrobj
