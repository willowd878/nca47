from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import GPoolInfo as GPoolModel
from nca47.objects import base
from nca47.objects import fields as object_fields


class GPool(base.Nca47Object):
    VERSION = '1.0'
    fields = {
        'tenant_id': object_fields.StringField(),
        'name': object_fields.StringField(),
        'enable': object_fields.StringField(),
        'pass_': object_fields.StringField(),
        'ttl': object_fields.StringField(),
        'max_addr_ret': object_fields.StringField(),
        'cname': object_fields.StringField(),
        'first_algorithm': object_fields.StringField(),
        'second_algorithm': object_fields.StringField(),
        'fallback_ip': object_fields.StringField(),
        'hms': object_fields.ListOfStringsField(),
        'gmember_list': object_fields.ListOfStringsField(),
        'warning': object_fields.StringField(),
        'gpool_id': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwargs):
        self.db_api = db_api.get_instance()
        super(GPool, self).__init__(context=None, **kwargs)

    @staticmethod
    def __from_db_object(dns_gpool, db_dns_gpool):
        """
        :param dns_syngroup:
        :param db_dns_syngroup:
        :return:
        """
        for field in dns_gpool.fields:
            dns_gpool[field] = db_dns_gpool
        dns_gpool.obj_reset_changes()
        return dns_gpool

    def create(self, context, values):
        gpool = self.db_api.create(GPoolModel, values)
        return gpool

    def update(self, context, id, values):
        gpool = self.db_api.update_object(GPoolModel, id, values)
        return gpool

    def get_object(self, context, **values):
        gpool = self.db_api.get_object(GPoolModel, **values)
        return gpool

    def delete(self, context, id):
        gpool = self.db_api.delete_object(GPoolModel, id)
        return gpool

    def get_objects(self, context, **values):
        gpool = self.db_api.get_objects(GPoolModel, **values)
        return gpool

    def get_all_objects(self, context, str_sql):
        gpool = self.db_api.get_all_objects(GPoolModel, str_sql)
        return gpool

    def get_all_objects_by_conditions(self, context, like_dic, search_dic):
        gpool = self.db_api.get_all_objects_by_conditions(GPoolModel, like_dic,
                                                          search_dic)
        return gpool
