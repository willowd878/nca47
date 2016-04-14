from nca47.db import api as db_api
from nca47.objects import base
from nca47.objects import fields as object_fields
from nca47.db.sqlalchemy.models.firewall import NetService


class FwNetservicesInfo(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'name': object_fields.StringField(),
        'proto': object_fields.StringField(),
        'port': object_fields.StringField(),
        'vfwname': object_fields.StringField(),
        'vfw_id': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(FwNetservicesInfo, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(fw_netservices_info, db_fw_netservices_info):
        """Converts a database entity to a formal :class:`NetService` object.

        :param fw_netservices_info: An object of :class:`NetService`.
        :param db_fw_netservices_info: A DB model of a NetService.
        :return: a :class:`NetService` object.
        """
        for field in fw_netservices_info.fields:
            fw_netservices_info[field] = db_fw_netservices_info[field]

        fw_netservices_info.obj_reset_changes()
        return fw_netservices_info

    def create(self, context, values):
        zone = self.db_api.create(NetService, values)
        return zone

    def update(self, context, id_, values):
        record = self.db_api.update_object(NetService, id_, values)
        return record

    def delete(self, context, id_):
        record = self.db_api.delete_object(NetService, id_)
        return record

    def get_objects(self, context, **values):
        record = self.db_api.get_objects(NetService, **values)
        return record

    def get_object(self, context, **values):
        record = self.db_api.get_object(NetService, **values)
        return record
