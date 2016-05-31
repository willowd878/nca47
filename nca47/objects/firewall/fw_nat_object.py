from nca47.db import api as db_api
from nca47.db.sqlalchemy.models import FW_SecurityZone as scurityZone
from nca47.db.sqlalchemy.models import FW_Staticnat as staticnat
from nca47.db.sqlalchemy.models import FW_vrf as vrf
from nca47.db.sqlalchemy.models import FW_snat as snat
from nca47.objects import base
from nca47.objects import fields as object_fields
from nca47.common.exception import HaveSameObject
from nca47.common.exception import IsNotExistError


class FW_SecurityZone_Object(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'id': object_fields.StringField(),
        'name': object_fields.StringField(),
        'ifnames': object_fields.ListOfStringsField(),
        'priority': object_fields.StringField(),
        'vfwname': object_fields.StringField(),
        'vfw_id': object_fields.StringField(),
        'operation_fro': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(FW_SecurityZone_Object, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(fw_object, db_fw_object):
        """Converts a database entity to a formal :class:`FW_SecurityZone` object.

        :param fw_object: An object of :class:`FW_SecurityZone`.
        :param db_fw_object: A DB model of a FW_SecurityZone.
        :return: a :class:`FW_SecurityZone` object.
        """
        for field in fw_object.fields:
            fw_object[field] = db_fw_object[field]

        fw_object.obj_reset_changes()
        return fw_object

    def create(self, context, values):
        value = {}
        value["name"] = values["name"]
        value["vfw_id"] = values["vfw_id"]
        value["deleted"] = False
        obj_old = self.get_objects(context, **value)
        if len(obj_old) != 0:
            raise HaveSameObject(param_name=value["name"])
        obj = self.db_api.create(scurityZone, values)
        return obj

    def update(self, context, id, values):
        obj = self.db_api.update_object(scurityZone, id, values)
        return obj

    def get_object(self, context, **values):
        obj = self.db_api.get_object(scurityZone, **values)
        return obj

    def delete(self, context, id):
        value = {}
        value["id"] = id
        value["deleted"] = False
        obj_old = self.get_objects(context, **value)
        if len(obj_old) == 0:
            raise IsNotExistError(param_name="id:" +
                                  value["id"])
        obj = self.db_api.delete_object(scurityZone, id)
        return obj

    def get_objects(self, context, **values):
        obj = self.db_api.get_objects(scurityZone, **values)
        return obj


class FW_Staticnat_Object(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'id': object_fields.StringField(),
        'name': object_fields.StringField(),
        'ifname': object_fields.StringField(),
        'lanip': object_fields.StringField(),
        'wanip': object_fields.StringField(),
        'slot': object_fields.StringField(),
        'vfwname': object_fields.StringField(),
        'vfw_id': object_fields.StringField(),
        'operation_fro': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(FW_Staticnat_Object, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(fw_object, db_fw_object):
        """Converts a database entity to a formal :class:`FW_Staticnat` object.

        :param fw_object: An object of :class:`FW_Staticnat_Object`.
        :param db_fw_object: A DB model of a FW_Staticnat_Object.
        :return: a :class:`FW_Staticnat` object.
        """
        for field in fw_object.fields:
            fw_object[field] = db_fw_object[field]

        fw_object.obj_reset_changes()
        return fw_object

    def create(self, context, values):
        value = {}
        value["name"] = values["name"]
        value["vfw_id"] = values["vfw_id"]
        value["deleted"] = False
        obj_old = self.get_objects(context, **value)
        if len(obj_old) != 0:
            raise HaveSameObject(param_name=value["name"])
        objec = self.db_api.create(staticnat, values)
        return objec

    def update(self, context, id, values):
        obj = self.db_api.update_object(staticnat, id, values)
        return obj

    def get_object(self, context, **values):
        obj = self.db_api.get_object(staticnat, **values)
        return obj

    def delete(self, context, id):
        value = {}
        value["id"] = id
        value["deleted"] = False
        obj_old = self.get_objects(context, **value)
        if len(obj_old) == 0:
            raise IsNotExistError(param_name="id:" +
                                  value["id"])
        obj = self.db_api.delete_object(staticnat, id)
        return obj

    def get_objects(self, context, **values):
        obj = self.db_api.get_objects(staticnat, **values)
        return obj

    def get_all_objects(self, context, str_sql):
        obj = self.db_api.get_all_objects(staticnat, str_sql)
        return obj

    def get_all_objects_by_conditions(self, context, like_dic, search_dic):
        staticnats = self.db_api.get_all_objects_by_conditions(staticnat,
                                                                like_dic,
                                                                search_dic)
        return staticnats


class FW_Vrf_Object(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'id': object_fields.StringField(),
        'name': object_fields.StringField(),
        'vrfInterface': object_fields.ListOfStringsField(),
        'vfwname': object_fields.StringField(),
        'vfw_id': object_fields.StringField(),
        'vres_id': object_fields.StringField(),
        'operation_fro': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(FW_Vrf_Object, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(fw_object, db_fw_object):
        """Converts a database entity to a formal :class:`FW_Staticnat` object.

        :param fw_object: An object of :class:`FW_Staticnat_Object`.
        :param db_fw_object: A DB model of a FW_Staticnat_Object.
        :return: a :class:`FW_Staticnat` object.
        """
        for field in fw_object.fields:
            fw_object[field] = db_fw_object[field]

        fw_object.obj_reset_changes()
        return fw_object

    def create(self, context, values):
        value = {}
        value["name"] = values["name"]
        value["vres_id"] = values["vres_id"]
        value["deleted"] = False
        obj_old = self.get_objects(context, **value)
        if len(obj_old) != 0:
            raise HaveSameObject(param_name=value["name"])
        obj = self.db_api.create(vrf, values)
        return obj

    def update(self, context, id, values):
        obj = self.db_api.update_object(vrf, id, values)
        return obj

    def get_object(self, context, **values):
        obj = self.db_api.get_object(vrf, **values)
        return obj

    def delete(self, context, id):
        value = {}
        value["id"] = id
        value["deleted"] = False
        obj_old = self.get_objects(context, **value)
        if len(obj_old) == 0:
            raise IsNotExistError(param_name="id:" +
                                  value["id"])
        obj = self.db_api.delete_object(vrf, id)
        return obj

    def get_objects(self, context, **values):
        obj = self.db_api.get_objects(vrf, **values)
        return obj


class FW_Snat_Object(base.Nca47Object):
    VERSION = '1.0'

    fields = {
        'id': object_fields.StringField(),
        'name': object_fields.StringField(),
        'outifname': object_fields.StringField(),
        'srcipobjname': object_fields.ListOfStringsField(),
        'dstipobjname': object_fields.ListOfStringsField(),
        'wanippoolname': object_fields.StringField(),
        'vfwname': object_fields.StringField(),
        'vfw_id': object_fields.StringField(),
        'operation_fro': object_fields.StringField(),
    }

    def __init__(self, context=None, **kwarg):
        self.db_api = db_api.get_instance()
        super(FW_Snat_Object, self).__init__(context=None, **kwarg)

    @staticmethod
    def _from_db_object(fw_object, db_fw_object):
        """Converts a database entity to a formal :class:`FW_Staticnat` object.

        :param fw_object: An object of :class:`FW_Staticnat_Object`.
        :param db_fw_object: A DB model of a FW_Staticnat_Object.
        :return: a :class:`FW_Staticnat` object.
        """
        for field in fw_object.fields:
            fw_object[field] = db_fw_object[field]

        fw_object.obj_reset_changes()
        return fw_object

    def create(self, context, values):
        value = {}
        value["name"] = values["name"]
        value["vfw_id"] = values["vfw_id"]
        value["deleted"] = False
        obj_old = self.get_objects(context, **value)
        if len(obj_old) != 0:
            raise HaveSameObject(param_name=value["name"])
        obj = self.db_api.create(snat, values)
        return obj

    def get_object(self, context, **values):
        obj = self.db_api.get_object(snat, **values)
        return obj

    def delete(self, context, id):
        value = {}
        value["id"] = id
        value["deleted"] = False
        obj_old = self.get_objects(context, **value)
        if len(obj_old) == 0:
            raise IsNotExistError(param_name="id:" +
                                  value["id"])
        obj = self.db_api.delete_object(snat, id)
        return obj

    def get_objects(self, context, **values):
        obj = self.db_api.get_objects(snat, **values)
        return obj

    def get_all_objects_by_conditions(self, context, like_dic, search_dic):
        snats = self.db_api.get_all_objects_by_conditions(snat,
                                                                like_dic,
                                                                search_dic)
        return snats
