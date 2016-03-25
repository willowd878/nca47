from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import OperationHistory as HistoryModel
from nca47.objects import base
from nca47.objects import fields as object_fields


class OperationHistory(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'config_id': object_fields.StringField(),
        'input': object_fields.StringField(),
        'operation_type': object_fields.ListOfStringsField(),
        'operation_time': object_fields.StringField(),
        'operation_status': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        self.obj_set_defaults()
        super(OperationHistory, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(opt_history, db_opt_history):
        """Converts a database entity to a formal :class:`DnsZone` object.

        :param dns_zone: An object of :class:`DnsZone`.
        :param db_dns_zone: A DB model of a DnsZone.
        :return: a :class:`DnsZone` object.
        """
        for field in opt_history.fields:
            opt_history[field] = db_opt_history[field]

        opt_history.obj_reset_changes()
        return opt_history

    def get_by_id(self, context, id):
        history = self.db_api._safe_get_object(HistoryModel, id)
        return history

    def create(self, context, values):
        zone = self.db_api.create(HistoryModel, values)
        return zone

    def update(self, context, id, values):
        zone = self.db_api.update_object(HistoryModel, id, values)
        return zone

    def update_byid(self, context, id, values):
        zone = self.db_api.update_object(HistoryModel, id, values)
        return zone

    def get_object(self, context, **values):
        zone = self.db_api.get_object(HistoryModel, **values)
        return zone
