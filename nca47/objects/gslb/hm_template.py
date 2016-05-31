from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import HmTemplateInfo
from nca47.objects import base
from nca47.objects import fields as object_fields


class HmTemplate(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'name': object_fields.StringField(),
        'types': object_fields.StringField(),
        'check_interval': object_fields.StringField(),
        'timeout': object_fields.StringField(),
        'max_retries': object_fields.StringField(),
        'sendstring': object_fields.StringField(),
        'recvstring': object_fields.StringField(),
        'hm_template_id': object_fields.StringField(),
        'refcnt': object_fields.StringField(),
        'username': object_fields.StringField(),
        'password': object_fields.StringField(),
        'tenant_id': object_fields.StringField()
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(HmTemplate, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(dns_hm_template, db_dns_hm_template):
        """Converts a database entity to a formal :class:`HmTemplate` object.

        :param dns_hm_template: An object of :class:`HmTemplate`.
        :param db_dns_hm_template: A DB model of a HmTemplate.
        :return: a :class:`HmTemplate` object.
        """
        for field in dns_hm_template.fields:
            dns_hm_template[field] = db_dns_hm_template[field]

        dns_hm_template.obj_reset_changes()
        return dns_hm_template

    def create(self, context, values):
        hm_template = self.db_api.create(HmTemplateInfo, values)
        return hm_template

    def update(self, context, id, values):
        hm_template = self.db_api.update_object(HmTemplateInfo, id, values)
        return hm_template

    def delete(self, context, id):
        hm_template = self.db_api.delete_object(HmTemplateInfo, id)
        return hm_template

    def get_objects(self, context, **values):
        hm_template = self.db_api.get_objects(HmTemplateInfo, **values)
        return hm_template

    def get_object(self, context, **values):
        hm_template = self.db_api.get_object(HmTemplateInfo, **values)
        return hm_template

    def get_all_objects(self, str_sql):
        hm_template = self.db_api.get_all_objects(HmTemplateInfo, str_sql)
        return hm_template

    def get_all_objects_by_conditions(self, context, like_dic, search_dic):
        hm_template = self.db_api.get_all_objects_by_conditions(
                                    HmTemplateInfo, like_dic, search_dic)
        return hm_template
