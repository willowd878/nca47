import copy
from oslo_config import cfg
from oslo_serialization import jsonutils as json
from oslo_db import exception as db_exception
from oslo_log import log as logging
from oslo_messaging.exceptions import MessagingTimeout
from nca47 import objects
from nca47.common.i18n import _LI
from nca47.common.i18n import _LW
from nca47.common.i18n import _LE
from nca47.common import exception
from nca47.db import api as db_api
from nca47.manager import rpcapi
from nca47.manager import db_common
from nca47.api.controllers.v1 import tools

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

DNS_MANAGER = None


class DNSManager(object):
    """
    DNS operation handler class, using for handle client requests,
    validate parameters whether is legal,  handling DB operations and
    calling rpc client's corresponding method to send messaging to agent
    endpoints
    """

    def __init__(self):
        self.db_common = db_common.DBCommon.get_instance()
        self.db_api = db_api.get_instance()
        self.rpc_api = rpcapi.DNSManagerAPI.get_instance()

    @classmethod
    def get_instance(cls):

        global DNS_MANAGER
        if not DNS_MANAGER:
            DNS_MANAGER = cls()
        return DNS_MANAGER

    def create_zone(self, context, zone):
        """
        create zone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # change the zone values with dic format
        target_values = self._make_dns_zone_object(zone)
        # init the DB operations object
        zone_obj = objects.DnsZone(context, **target_values)
        # Check the zone which have same name if is exist in DB
        target_zone = self._valid_if_zone_exist(context, zone_obj)
        if target_zone is not None:
            LOG.warning(_LW("Have same zone id/name in DB"))
            raise exception.HaveSameObject(param_name=target_zone.zone_name)
        # insert operation history type with Creating in DB
        input_str = json.dumps(zone)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'CREATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # create the zone info in db
        db_zone_obj = self._create_in_storage(context, zone_obj)
        try:
            # get the default zone records
            zone_id = target_values['zone_name']
            # handling create zone method in RPC
            response = self.rpc_api.create_zone(context, zone)
            rrs_results = self.rpc_api.get_records(context, zone_id)
            for resourc in rrs_results['resources']:
                records = {}
                records['rrs_id'] = resourc['id']
                records['zone_id'] = db_zone_obj['id']
                records['tenant_id'] = zone['tenant_id']
                records['rrs_name'] = resourc['name']
                records['type'] = resourc['type']
                records['ttl'] = resourc['ttl']
                records['klass'] = resourc['klass']
                records['rdata'] = resourc['rdata']
                # init the DB operations objec with zone_record
                zone_rrs_obj = objects.DnsZoneRrs(context, **records)
                # create the zone info in db
                self._create_in_storage(context, zone_rrs_obj)
        except MessagingTimeout as e:
            # DB rollback since create zone failed in Device
            zone_obj.delete(context, db_zone_obj['id'])
            raise e
        except Exception as e:
            LOG.error(_LE("Create corresponding response on device failed"))
            # get the default zone records from db
            rrs_dic = {}
            rrs_dic['zone_id'] = db_zone_obj['id']
            rrs_dic['deleted'] = False
            rrs_obj = objects.DnsZoneRrs(context, **rrs_dic)
            zone_records = rrs_obj.get_objects(context, **rrs_dic)
            if zone_records is not None:
                # get the all id of the zone_records
                del_rrs_obj = objects.DnsZoneRrs(context)
                for record in zone_records:
                    # delete the DB operations objec with zone_record
                    del_rrs_obj.delete(context, record['id'])
            # DB rollback since create zone failed in Device
            zone_obj.delete(context, db_zone_obj['id'])
            raise e
        # update operation history type with Failed in DB

        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(context, history['id'],
                                                **input_operation_history)
        return db_zone_obj

    def update_zone(self, context, zone, id):
        """
        update zone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        org_db_zone_obj = self.get_zone_db_details(context, id)

        target_values = self._make_dns_zone_object(zone)
        # init the DB operations object
        zone_obj = objects.DnsZone(context, **target_values)

        # insert operation history type with Creating in DB
        input_str = json.dumps(zone)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'UPDATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # update the zone in db
        db_zone_obj = zone_obj.update(context, id, zone_obj.as_dict())
        try:
            # get the zone_id for device update
            zone_id = db_zone_obj['zone_name']
            # handling update zone method in RPC
            response = self.rpc_api.update_zone(context, zone, zone_id)
        except Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            # DB rollback since update failed in Device, to re-update back
            zone_obj.update(context, id, org_db_zone_obj)
            raise e
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(context, history['id'],
                                                **input_operation_history)
        return db_zone_obj

    def update_zone_owners(self, context, zone, id):
        """
        update zone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        org_db_zone_obj = self.get_zone_db_details(context, id)
        target_values = self._make_dns_zone_object(zone)
        # init the DB operations object
        zone_obj = objects.DnsZone(context, **target_values)
        # insert operation history type with Creating in DB
        input_str = json.dumps(zone)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'UPDATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # update the zone in db
        db_zone_obj = zone_obj.update(context, id, zone_obj.as_dict())
        try:
            # get the zone_id for device update
            zone_id = db_zone_obj['zone_name']
            # handling update zone by owaners method in RPC
            response = self.rpc_api.update_zone_owners(context, zone, zone_id)
        except Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            # DB rollback since update zone failed in Device
            zone_obj.update(context, id, org_db_zone_obj)
            # raise the exception for catch
            raise e
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(context, history['id'],
                                                **input_operation_history)
        return db_zone_obj

    def delete_zone(self, context, id):
        """
        delete zone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        org_db_zone_obj = self.get_zone_db_details(context, id)
        # init the DB operations object
        zone_obj = objects.DnsZone(context)
        # insert operation history type with Creating in DB
        input_str = "delete zone"
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # delete the zone in db
        db_zone_obj = zone_obj.delete(context, id)
        try:
            zone_id = db_zone_obj['zone_name']
            # handling delete zone method in RPC
            response = self.rpc_api.delete_zone(context, zone_id)
            # get the default zone records from db
            rrs_dic = {}
            rrs_dic['zone_id'] = id
            rrs_dic['deleted'] = False
            rrs_obj = objects.DnsZoneRrs(context, **rrs_dic)
            zone_records = rrs_obj.get_objects(context, **rrs_dic)
            # get the all id of the zone_records
            del_rrs_obj = objects.DnsZoneRrs(context)
            for record in zone_records:
                # delete the DB operations objec with zone_record
                del_rrs_obj.delete(context, record['id'])
        except Exception as e:
            LOG.error(_LE("Delete corresponding response on device failed"))
            # since delete failed in device, so re-update back object in DB
            zone_obj.update(context, id, org_db_zone_obj)
            # raise the exception for catch
            raise e
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(context, history['id'],
                                                **input_operation_history)
        return response

    def get_zone_one(self, context, zone_id):
        """getting target zone details from dns device"""
        try:
            # handling zone method in RPC
            response = self.rpc_api.get_zone_one(context, zone_id)
        except Exception as e:
            raise e
        return response

    def get_zones(self, context):
        """handling zones method in RPC"""
        try:
            # handling zones method in RPC
            response = self.rpc_api.get_zones(context)
        except Exception as e:
            raise e
        return response

    def get_zone_db_details(self, context, id):
        """Todo call DB to get one zone"""
        # init the DB operations object
        zone_obj = objects.DnsZone(context)
        zone_name_dic = {}
        zone_name_dic['id'] = id
        zone_name_dic['deleted'] = False
        # try/catch the no one get
        try:
            # Todo call DB to get one zone by id
            zone_obj = zone_obj.get_object(context, **zone_name_dic)
        except Exception:
            LOG.warning(_LW("No zone with id=%(id)s in DB"), {"id": id})
            raise exception.IsNotExistError(param_name="Zone with id=" + id)
        return zone_obj

    def get_all_db_zone(self, context):
        """Todo call DB to get all zones"""
        # init the DB operations object
        zone_obj = objects.DnsZone(context)
        # Filter the data that has been disabled
        zone_name_dic = {}
        zone_name_dic['deleted'] = False
        # Todo call DB to get all zones
        zone_objs = zone_obj.get_objects(context, **zone_name_dic)
        if zone_objs is None:
            LOG.warning(_LW("There is no data in the DNS_ZONE_INFO"))
            raise exception.IsNotExistError(param_name="Zone with id=" + id)
        return zone_objs

    def get_db_zones(self, context, zones):
        """Todo call DB to get all zones"""
        # init the DB operations object
        zone_obj = objects.DnsZone(context)
        # Filter the data that has been disabled
        zones['deleted'] = "0"
        # get the like values
        like_list = ['zone_name', 'owners', 'default_ttl', 'slaves', 'renewal']
        # get the union values
        search_list = ['tenant_id', 'deleted']
        # get the run sqlstr
        like_dic, search_dic = tools.classfiy_sql_keys(zones, like_list,
                                                       search_list)
        zone_objs = zone_obj.get_all_objects_by_conditions(context, like_dic,
                                                           search_dic)
        if zone_objs is None:
            LOG.warning(_LW("There is no data in the dns_zone_info"))
            raise exception.IsNotExistError(param_name="Zone with id=" + id)
        return zone_objs

    def get_dev_records(self, context, zone_id):
        try:
            response = self.rpc_api.get_records(context, zone_id)
        except MessagingTimeout as e:
            raise e
        return response

    def get_db_records(self, context, zone_id):
        # check zone if is not exsit
        target_zone = self.is_exist_zone(context, zone_id)
        # dev_zone_id is zone_id of device
        if target_zone is None:
            raise exception.IsNotExistError(param_name=zone_id)
        rrs_dic = {}
        rrs_dic['zone_id'] = zone_id
        rrs_dic['deleted'] = False
        rrs_obj = objects.DnsZoneRrs(context, **rrs_dic)
        target = None
        try:
            target = rrs_obj.get_objects(context, **rrs_dic)
        except db_exception as e:
            raise e
        return target

    def query_records(self, context, rrs):
        LOG.info(_LI("the query_records method of the dns_manager start"))
        key = rrs.keys()
        if "name" in key:
            if tools.is_not_nil(rrs['name']):
                rrs["rrs_name"] = rrs["name"]
        rrs['deleted'] = "0"
        like_list = ['rrs_name', 'ttl', "rdata"]
        search_list = ["type", "deleted", "tenant_id"]
        like_dic, search_dic = tools.classfiy_sql_keys(
            rrs, like_list, search_list)
        rrs_obj = objects.DnsZoneRrs(context, **rrs)
        query = rrs_obj.get_all_objects_by_conditions(context, like_dic,
                                                      search_dic)
        return query

    # TODO this is a test environment method,and it will
    # be deleted after deployment in a production environment
    # Begin
    def query_records_in_test_env(self, context, rrs):
        LOG.info(_LI("the query_records_in_test_env method"
                     "of the dns_manager start"))
        key = rrs.keys()
        if tools.is_not_nil(rrs['test_environment']):
            zone_name = rrs["test_environment"]
            zone_name_dic = {}
            zone_name_dic['zone_name'] = zone_name
            zone_name_dic['deleted'] = False
            zone_obj = objects.DnsZone(context, **zone_name_dic)
            try:
                target_zone = zone_obj.get_object(context, **zone_name_dic)
            except Exception:
                raise exception.IsNotExistError(
                                        param_name=rrs["test_environment"])
            zone_id = target_zone["id"]
            rrs["zone_id"] = zone_id
        search_list = ["type", "deleted", "zone_id", "tenant_id"]
        if "name" in key:
            if tools.is_not_nil(rrs['name']):
                rrs["rrs_name"] = rrs["name"]
        rrs['deleted'] = "0"
        like_list = ['rrs_name', 'ttl', "rdata"]
        like_dic, search_dic = tools.classfiy_sql_keys(
            rrs, like_list, search_list)
        rrs_obj = objects.DnsZoneRrs(context, **rrs)
        query = rrs_obj.get_all_objects_by_conditions(context, like_dic,
                                                      search_dic)
        return query

    def create_record_in_test_env(self, context, record):
        LOG.info(_LI("the create_record_in_test_env method"
                     "of the dns_manager start"))
        zone_name_env = {
            "hfadv": "hfadv",
            "hfdev": "hfdev",
            "hfpfm": "hfpfm",
            "hfpre": "hfpre",
            "hfsit": "hfsit",
            "hfsys": "hfsys",
            "hftest": "hftest",
            "hf": "hf",
            "hfuat": "hfuat",
            "test": "test",
            "pfm": "pfm",
            "uat": "uat"
        }
        # insert operation history type with Creating in DB
        input_str = json.dumps(record)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'CREATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # check zone_record  is or not exsit
        target_record = self.is_exist_zone_record(context, record)
        if target_record is not None:
            LOG.warning(_LW("the record object with name = %(record)s"
                            " already exists in DB"),
                        {"record": record['name']})
            raise exception.HaveSameObject(param_name=record['name'])
        json_name = record['name']
        zone_name = zone_name_env[record["environment_name"]]
        dev_zone_name = '%s%s' % ('.', zone_name)
        if not json_name.endswith(dev_zone_name):
            exception.ParamValueError(param_name="environment_name")
        zone_name_dic = {}
        zone_name_dic['zone_name'] = zone_name
        zone_name_dic['deleted'] = False
        zone_obj = objects.DnsZone(context, **zone_name_dic)
        try:
            target_zone = zone_obj.get_object(context, **zone_name_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="environment_name")
        zone_id = target_zone["id"]

        LOG.info(_LI("the zone object with id=%(zone_name)s is existed"),
                 {"zone_name": zone_name})
        record["zone_id"] = zone_id
        record_values = self._make_dns_record_object(record)
        record_obj = objects.DnsZoneRrs(context, **record_values)
        # return response from DB
        response = self._create_in_storage(context, record_obj)
        new_name = tools.clean_end_str(dev_zone_name, record['name'])
        record['name'] = new_name
        try:
            response_dev = self.rpc_api.create_record(context, record,
                                                      zone_name)
        except Exception as e:
            LOG.error(_LE("Create response on device failed"))
            # since create failed in device, so delete object in DB
            self.delete_rrs_info(context, response["id"])
            raise e
        # update dns_rrs_info table, since record id would be changed
        response = self.update_rrs_info(context, response["id"],
                                        None, response_dev)
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return response

    # End test environment

    def get_record_from_db(self, context, record_id):
        record_dic = {}
        record_dic['id'] = record_id
        record_dic['deleted'] = False
        rrs_obj = objects.DnsZoneRrs(context)
        target = None
        try:
            target = rrs_obj.get_object(context, **record_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="records with id = " +
                                                       record_id)
        return target

    def _valid_if_zone_exist(self, context, zone):
        """Check the zone which have same name if is exist in DB"""
        zone_name_dic = {}
        zone_name_dic['zone_name'] = zone.zone_name
        zone_name_dic['deleted'] = False
        target_zone = None
        try:
            # get the zone in db
            target_zone = zone.get_object(context, **zone_name_dic)
        except Exception:
            pass
        return target_zone

    def _valid_if_obj_exist(self, context, table_obj, query_obj_dic):
        """Check the data which have same name if is exist in DB"""
        query_obj_dic['deleted'] = False
        rst_qry_obj = None
        try:
            # get the result in db
            rst_qry_obj = table_obj.get_object(context, **query_obj_dic)
        except Exception:
            pass
        return rst_qry_obj

    def _create_in_storage(self, context, obj):
        """create the zone in DB"""
        try:
            # create the obj in db
            obj = obj.create(context, obj.as_dict())
        except db_exception:
            LOG.error(_LE("Create/Insert db operation failed!"))
            raise db_exception
        return obj

    def create_record(self, context, record):
        LOG.info(_LI("the create_record method of the dns_manager start"))
        # insert operation history type with Creating in DB
        input_str = json.dumps(record)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'CREATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # check zone_record  is or not exsit
        target_record = self.is_exist_zone_record(context, record)
        if target_record is not None:
            LOG.warning(_LW("the record object with name = %(record)s"
                            " already exists in DB"),
                        {"record": record['name']})
            raise exception.HaveSameObject(param_name=record['name'])
        json_name = record['name']

        zones = self.get_zone_name_bytenant_id(context, record['tenant_id'])
        if len(zones) == 0:
            raise exception.IsNotExistError(param_name="tenant_id")
        flag = True
        for zone in zones:
            zone_name = zone["zone_name"]
            dev_zone_name = '%s%s' % ('.', zone_name)
            if json_name.endswith(dev_zone_name):
                zone_id = zone["id"]
                flag = False
                break
        if flag:
            raise exception.ZoneOfRecordIsError(name=json_name,
                                                tenant=record['tenant_id'])

        LOG.info(_LI("the zone object with id=%(zone_name)s is existed"),
                 {"zone_name": zone_name})
        record["zone_id"] = zone_id
        record_values = self._make_dns_record_object(record)
        record_obj = objects.DnsZoneRrs(context, **record_values)
        # return response from DB
        response = self._create_in_storage(context, record_obj)
        new_name = tools.clean_end_str(dev_zone_name, record['name'])
        record['name'] = new_name
        try:
            response_dev = self.rpc_api.create_record(context, record,
                                                      zone_name)
        except Exception as e:
            LOG.error(_LE("Create response on device failed"))
            # since create failed in device, so delete object in DB
            self.delete_rrs_info(context, response["id"])
            raise e
        # update dns_rrs_info table, since record id would be changed
        response = self.update_rrs_info(context, response["id"],
                                        None, response_dev)
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return response

    def update_record(self, context, record):
        # insert operation history type with Creating in DB
        input_str = json.dumps(record)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'UPDATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        record_obj = self.get_record_from_db(context, record["id"])
        zone_id = record_obj["zone_id"]
        zone = self.is_exist_zone(context, zone_id)
        if zone is None:
            raise exception.IsNotExistError(param_name="record  zone")
        dev_zone_id = zone["zone_name"]
        LOG.info(_LI("%(zone_name)s is existed"), {"zone_name": dev_zone_id})
        # return response from DB
        response = self.update_rrs_info(context, record["id"], record, None)
        # dev_rrs_id is rrs_id of device
        dev_rrs_id = response["rrs_id"]
        try:
            # handling update zone record method in RPC
            # return response from Device
            response_dev = self.rpc_api.update_record(context, record,
                                                      dev_zone_id, dev_rrs_id)
        except Exception as e:
            LOG.error(_LE("Update response on device failed"))
            # DB rollback
            rrs_obj = objects.DnsZoneRrs(context)
            rrs_obj.update(context, record["id"], record_obj)
            # raise the exception for catch
            raise e
        response_upd = self.update_rrs_info(context, record["id"],
                                            None, response_dev)
        if ("ttl" in record.keys()) and (record_obj["ttl"] != record["ttl"]):
            self.update_rrs_info_byget_objs(context, dev_zone_id, response_dev)
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return response_upd

    def delete_record(self, context, rrs):
        # insert operation history type with Creating in DB
        input_str = "delete_record"
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        org_db_record_obj = self.get_record_from_db(context, rrs["id"])
        zone_id = org_db_record_obj["zone_id"]
        zone = self.is_exist_zone(context, zone_id)
        if zone is None:
            raise exception.IsNotExistError(param_name="record  zone")
        dev_zone_id = zone["zone_name"]
        LOG.info(_LI("%(dev_zone_id)s is existed"),
                 {"dev_zone_id": dev_zone_id})
        response = self.delete_rrs_info(context, rrs["id"])
        # dev_rrs_id is rrs_id of device
        dev_rrs_id = response["rrs_id"]
        try:
            # handling delete zone record method in RPC
            # delete a information of dns_rrs_info table from Device
            response_dev = self.rpc_api.delete_record(context,
                                                      dev_zone_id,
                                                      dev_rrs_id)
        except Exception as e:
            LOG.error(_LE("Delete response on device failed"))
            # Rollback DB
            rrs_obj = objects.DnsZoneRrs(context)
            rrs_obj.update(context, rrs["id"], org_db_record_obj)
            raise e
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return response_dev

    # The following is a method that cleaning the cache !
    def del_cache(self, context, domain):
        """Clear DNS cache"""
        # insert operation history type with Creating in DB
        input_str = json.dumps(domain)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        try:
            # delete the dns cache
            response = self.rpc_api.del_cache(context, domain)
        except Exception as e:
            LOG.error(_LE("Clear Cache response on device failed"))
            # raise the exception for catch
            raise e
        # update operation history type with Success in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return response

    def _make_dns_zone_object(self, zone_values):
        target_values = {}
        for k in zone_values.keys():
            if k == 'name':
                target_values['zone_name'] = zone_values[k]
            elif k == 'current_user':
                pass
            else:
                target_values[k] = zone_values[k]
        return target_values

    def _make_dns_record_object(self, record_values):
        target_values = {}
        target_values["zone_id"] = record_values["zone_id"]
        for k in record_values.keys():
            if k == 'name':
                target_values['rrs_name'] = record_values[k]
            else:
                target_values[k] = record_values[k]
        return target_values

    def is_exist_zone_record(self, context, dic):
        rrs_dic = {}
        rrs_dic['rrs_name'] = dic["name"]
        rrs_dic['rdata'] = dic["rdata"]
        rrs_dic['deleted'] = False
        rrs_obj = objects.DnsZoneRrs(context, **rrs_dic)
        target = None
        try:
            target = rrs_obj.get_object(context, **rrs_dic)
        except Exception:
            pass
        return target

    def is_exist_zone(self, context, zone_id):
        zone_name_dic = {}
        zone_name_dic['id'] = zone_id
        zone_name_dic['deleted'] = False
        zone_obj = objects.DnsZone(context, **zone_name_dic)
        target_zone = None
        try:
            target_zone = zone_obj.get_object(context, **zone_name_dic)
        except Exception:
            pass
        return target_zone

    def update_rrs_info(self, context, record_id, dic, response_dev):
        rrs_resp = {}
        if response_dev is not None:
            rrs_resp["rrs_id"] = response_dev["id"]
        else:
            if "ttl" in dic.keys():
                rrs_resp["ttl"] = dic["ttl"]
            if "rdata" in dic.keys():
                rrs_resp["rdata"] = dic["rdata"]
        rrs_obj = objects.DnsZoneRrs(context, **rrs_resp)
        try:
            record = rrs_obj.update(context, record_id, rrs_resp)
        except db_exception:
            LOG.error(_LE("update_rrs_info method operation failed!"))
            raise db_exception
        return record

    def update_rrs_info_byget_objs(self, context, zone_id, rps_dev):
        rrs_resp = {}
        rrs_resp["ttl"] = rps_dev["ttl"]
        get_objs = {}
        get_objs["rrs_name"] = rps_dev["name"]
        get_objs["type"] = rps_dev["type"]
        get_objs["zone_id"] = zone_id
        rrs_get_objs = objects.DnsZoneRrs(context, **get_objs)
        try:
            rrs_list = rrs_get_objs.get_objects(context, **get_objs)
            rrs_obj = objects.DnsZoneRrs(context, **rrs_resp)
            for rrs in rrs_list:
                rrs_info_id = rrs["id"]
                rrs_obj.update(context, rrs_info_id, rrs_resp)
        except db_exception:
            LOG.error(_LE("update_rrs_info_byid method operation failed!"))
            raise db_exception

    def delete_rrs_info(self, context, record_id):
        rrs_obj = objects.DnsZoneRrs(context)
        record = None
        try:
            record = rrs_obj.delete(context, record_id)
        except db_exception:
            LOG.error(_LE("delete_rrs_info method operation failed!"))
            raise db_exception
        return record

    def get_zone_name_bytenant_id(self, context, tenant_id):
        zone_name_dic = {}
        zone_name_dic['tenant_id'] = tenant_id
        zone_name_dic['deleted'] = False
        zone_obj = objects.DnsZone(context, **zone_name_dic)
        target_zone = None
        try:
            target_zone = zone_obj.get_objects(context, **zone_name_dic)
        except Exception:
            pass
        return target_zone

    def create_region(self, context, region):
        """
        create region handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        input_str = json.dumps(region)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'CREATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # init the DB operations object
        region_obj = objects.RegionInfo(context, **region)
        # Check the region which have same name if is exist in DB
        target_region = self._valid_if_obj_exist(context, region_obj, region)
        if target_region is not None:
            LOG.warning(_LW("Have same region name and tenant_id in DB"))
            raise exception.HaveSameObject(param_name=target_region.name)
        # create the region info in db
        db_region_obj = self._create_in_storage(context, region_obj)
        # the dic for modify
        update_region_dic = {}
        try:
            # handling create region method in RPC
            response = self.rpc_api.glsb_math(context, region, "create_region")
        except Exception:
            LOG.error(_LE("Create corresponding response on device failed"))
            # DB rollback since create region failed in Device
            region_obj.delete(context, db_region_obj['id'])
            raise
        # do update the data from device
        update_region_dic['region_id'] = response['id']
        update_region_dic['refcnt'] = response['refcnt']
        # modify the database for column(region_id refcnt)
        update_region_rst = region_obj.update(context, db_region_obj['id'],
                                              update_region_dic)
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(context, history['id'],
                                                **input_operation_history)
        return update_region_rst

    def create_member(self, context, member):
        """
        create region member handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        input_str = json.dumps(member)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'CREATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # if the member is already
        query_member_dic = {}
        query_member_dic['region_id'] = member['region_uuid']
        query_member_dic['type'] = member['type']
        query_member_dic['data1'] = member['data1']
        # init the DB operations object
        region_member_obj = objects.RegionUserInfo(context, **member)
        # Check the region which have same name if is exist in DB
        target_region_user = self._valid_if_obj_exist(context,
                                                      region_member_obj,
                                                      query_member_dic)
        if target_region_user is not None:
            LOG.warning(_LW("Have same region member name in DB"))
            raise exception.HaveSameObject(param_name=target_region_user.name)
        # query the region_info to get the value of name
        query_member_dic = {}
        query_member_dic['id'] = member['region_uuid']
        query_member_dic['tenant_id'] = member['tenant_id']
        region_obj = objects.RegionInfo(context)
        # Check the region which have same name if is exist in DB
        target_region = self._valid_if_obj_exist(context, region_obj,
                                                 query_member_dic)
        if target_region is None:
            LOG.warning(_LW("The object of %(param_name)s don't exist!") +
                        member['region_uuid'])
            raise exception.IsNotExistError(param_name=member['region_uuid'])
        # get the region name insert into region_user
        member['name'] = target_region.name
        member['region_id'] = member['region_uuid']
        # get the DB operations object
        region_member_obj = objects.RegionUserInfo(context, **member)
        # create the region member info in db
        db_region_member_obj = self._create_in_storage(context,
                                                       region_member_obj)
        # the dic for modify
        update_region_dic = {}
        try:
            # handling create region member method in RPC
            response = self.rpc_api.glsb_math(context, member, "create_member")
        except Exception:
            LOG.error(_LE("Create corresponding response on device failed"))
            # DB rollback since create region member failed
            region_member_obj.delete(context, db_region_member_obj.id)
            raise
        # do update the table from device
        update_region_dic['region_useruser_id'] = response['id']
        # modify the database for column(region_id refcnt)
        update_region_rst = region_member_obj.update(context,
                                                     db_region_member_obj.id,
                                                     update_region_dic)
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(context, history['id'],
                                                **input_operation_history)
        return update_region_rst

    def delete_member(self, context, id):
        """
        delete region member handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        input_str = "delete region member"
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # if the member is already
        query_member_dic = {}
        query_member_dic['id'] = id
        # init the DB operations object
        region_member_obj = objects.RegionUserInfo(context)
        # Check the region which have same name if is exist in DB
        target_region_user = self._valid_if_obj_exist(context,
                                                      region_member_obj,
                                                      query_member_dic)
        # delete the region in db
        rst_del_member = region_member_obj.delete(context, id)
        try:
            # get the region info by id
            result_region = self.get_region_db_detail(context,
                                                      rst_del_member.region_id)
            # get the new member dict
            del_member_dic = {}
            del_member_dic['name'] = result_region['region_id']
            del_member_dic['member_name'] = rst_del_member[
                'region_useruser_id']
            # handling delete member method in RPC
            response = self.rpc_api.glsb_math(context, del_member_dic,
                                              "delete_member")
        except Exception:
            LOG.error(_LE("Delete corresponding response on device failed"))
            # since delete failed in device, so re-update back object in DB
            region_member_obj.update(context, id, target_region_user)
            # raise the exception for catch
            raise
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(context, history['id'],
                                                **input_operation_history)
        return response

    def get_members(self, context):
        """Todo call DB to get all members"""
        # init the DB operations object
        region_obj = objects.RegionUserInfo(context)
        # Filter the data that has been disabled
        query_region_dic = {}
        query_region_dic['deleted'] = False
        # Todo call DB to get all regions
        region_objs = region_obj.get_objects(context, **query_region_dic)
        if region_objs is None:
            LOG.warning(_LW("There is no data in the dns_region_info"))
            raise exception.IsNotExistError(param_name="region with id=" + id)
        return region_objs

    def get_db_members(self, context, members):
        """Todo call DB to get all members"""
        # init the DB operations object
        region_obj = objects.RegionUserInfo(context)
        # Filter the data that has been disabled
        members['deleted'] = "0"
        # get the like values
        like_list = ['name', 'data1']
        # get the union values
        search_list = ['type', 'tenant_id', 'deleted']
        # get the run sqlstr
        like_dic, search_dic = tools.classfiy_sql_keys(members, like_list,
                                                       search_list)
        members_objs = region_obj.get_all_objects_by_conditions(context,
                                                                like_dic,
                                                                search_dic)
        if members_objs is None:
            LOG.warning(_LW("There is no data in the region_user_info"))
            raise exception.IsNotExistError(param_name="region with id=" + id)
        return members_objs

    def get_one_member(self, context, region_userid):
        """Todo call DB to get all members"""
        # init the DB operations object
        region_obj = objects.RegionUserInfo(context)
        # Filter the data that has been disabled
        query_region_dic = {}
        query_region_dic["id"] = region_userid
        query_region_dic['deleted'] = False
        # Todo call DB to get all regions
        try:
            region_objs = region_obj.get_object(context, **query_region_dic)
        except Exception:
            raise exception.IsNotExistError(param_name="region"
                                                       "with id=" +
                                                       region_userid)
        return region_objs

    def delete_region(self, context, id):
        """
        delete region handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        input_str = "delete region"
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # get the region info by id
        result_region = self.get_region_db_detail(context, id)
        # if the region used by sp_policy(src_data1)
        qry_policy_src_data1_dic = {}
        qry_policy_src_data1_dic['src_data1'] = result_region['name']
        # init the DB operations object
        proximity_obj = objects.SP_Policy(context)
        # Check the region which have same name(src_data1) in sp_policy
        target_sp_policy = self._valid_if_obj_exist(context, proximity_obj,
                                                    qry_policy_src_data1_dic)
        if target_sp_policy is not None:
            LOG.warning(_LW("The Object name=%(name)s is being used !") +
                        result_region['name'])
            raise exception.IsBeingUsedError(name=result_region['name'])
        else:
            # if the region used by sp_policy(dst_data1)
            qry_policy_dst_data1_dic = {}
            qry_policy_dst_data1_dic['dst_data1'] = result_region['name']
            # Check the region which have same name(dst_data1) in sp_policy
            target_sp_policy = self._valid_if_obj_exist(
                context, proximity_obj, qry_policy_dst_data1_dic)
            if target_sp_policy is not None:
                LOG.warning(_LW("The Object name=%(name)s is being used !") +
                            result_region['name'])
                raise exception.IsBeingUsedError(name=result_region['name'])
        # Check the if the region used by region_user
        qry_member_data1_dic = {}
        qry_member_data1_dic['data1'] = result_region['name']
        # init the DB operations object
        region_member_obj = objects.RegionUserInfo(context)
        # Check the region which have same name if is exist in DB
        target_member_data1 = self._valid_if_obj_exist(context,
                                                       region_member_obj,
                                                       qry_member_data1_dic)
        if target_member_data1 is not None:
            LOG.warning(_LW("The Object name=%(name)s is being used !") +
                        result_region['name'])
            raise exception.IsBeingUsedError(name=result_region['name'])
        # init the DB operations object
        region_obj = objects.RegionInfo(context)
        # delete the region in db
        db_region_obj = region_obj.delete(context, id)
        # get the region members to delete
        member_dic = {}
        member_dic['region_id'] = id
        get_member_obj = objects.RegionUserInfo(context)
        region_member_records = get_member_obj.get_objects(context,
                                                           **member_dic)
        for member_record in region_member_records:
            get_member_obj.delete(context, member_record.id)
        try:
            delete_region_dic = {}
            delete_region_dic['name'] = db_region_obj['region_id']
            # handling delete region method in RPC
            response = self.rpc_api.glsb_math(context, delete_region_dic,
                                              "delete_region")
        except Exception:
            LOG.error(_LE("Delete corresponding response on device failed"))
            # since delete failed in device, so re-update back object in DB
            region_obj.update(context, id, result_region)
            for member_record in region_member_records:
                get_member_obj.update(context, member_record.id, member_record)
            # raise the exception for catch
            raise
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return response

    def get_region_db_detail(self, context, id):
        """Todo call DB to get one region"""
        # init the DB operations object
        region_obj = objects.RegionInfo(context)
        region_query_dic = {}
        region_query_dic['id'] = id
        region_query_dic['deleted'] = False
        # try/catch the no one get
        try:
            # Todo call DB to get one region by id
            region_obj = region_obj.get_object(context, **region_query_dic)
        except Exception:
            LOG.warning(_LW("No region with id=%(id)s in DB"), {"id": id})
            raise exception.IsNotExistError(param_name="Region with id=" + id)
        return region_obj

    def get_region_user_db_detail(self, context, region_id):
        """Todo call DB to get one region user"""
        # init the DB operations object
        region_user_obj = objects.RegionUserInfo(context)
        region_query_dic = {}
        region_query_dic['region_id'] = region_id
        region_query_dic['deleted'] = False
        # try/catch the no one get
        try:
            # Todo call DB to get one region by id
            region_user_obj = region_user_obj.get_object(context,
                                                         **region_query_dic)
        except Exception:
            LOG.warning(_LW("No region user with id=%(id)s in DB"), {"id": id})
            raise exception.IsNotExistError(param_name="region user with id="
                                                       + id)
        return region_user_obj

    def get_all_db_region(self, context):
        """Todo call DB to get all regions"""
        # init the DB operations object
        region_obj = objects.RegionInfo(context)
        # Filter the data that has been disabled
        query_region_dic = {}
        query_region_dic['deleted'] = False
        # Todo call DB to get all regions
        region_objs = region_obj.get_objects(context, **query_region_dic)
        if region_objs is None:
            LOG.warning(_LW("There is no data in the dns_region_info"))
            raise exception.IsNotExistError(param_name="region with id=" + id)
        return region_objs

    def get_db_regions(self, context, regions):
        """Todo call DB to get all regions"""
        # init the DB operations object
        region_obj = objects.RegionInfo(context)
        # Filter the data that has been disabled
        regions['deleted'] = "0"
        # get the like values
        like_list = ['name']
        # get the union values
        search_list = ['tenant_id', 'deleted']
        # get the run sqlstr
        like_dic, search_dic = tools.classfiy_sql_keys(regions, like_list,
                                                       search_list)
        regions_objs = region_obj.get_all_objects_by_conditions(context,
                                                                like_dic,
                                                                search_dic)
        if regions_objs is None:
            LOG.warning(_LW("There is no data in the dns_region_info"))
            raise exception.IsNotExistError(param_name="region with id=" + id)
        return regions_objs

    def create_sp_policy(self, context, proximity):
        """
        create proximity handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        input_str = json.dumps(proximity)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'CREATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # init the DB operations object
        proximity_obj = objects.SP_Policy(context, **proximity)
        # create the proximity info in db
        db_proximity_obj = self._create_in_storage(context, proximity_obj)
        # the dic for modify
        update_proximity_dic = {}
        try:
            # handling create proximity method in RPC
            response = self.rpc_api.glsb_math(context, proximity,
                                              "create_sp_policy")
        except Exception:
            LOG.error(_LE("Create corresponding response on device failed"))
            # DB rollback since create proximity failed in Device
            proximity_obj.delete(context, db_proximity_obj['id'])
            raise Exception
        update_proximity_dic['sp_policy_id'] = response['id']
        update_proximity_dic['name'] = response['id']
        # modify the database for column(sp_policy_id)
        update_proximity_rst = proximity_obj.update(context,
                                                    db_proximity_obj['id'],
                                                    update_proximity_dic)
        # return the priority from device
        update_proximity_rst['priority'] = response['priority']
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return update_proximity_rst

    def delete_sp_policy(self, context, id):
        """
        delete proximity handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        input_str = "delete sp policy"
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # get the proximity info by id
        result_proximity = self.get_proximity_db_detail(context, id)
        # init the DB operations object
        proximity_obj = objects.SP_Policy(context)
        # delete the proximity in db
        db_proximity_obj = proximity_obj.delete(context, id)
        try:
            d_proximity_dic = {}
            d_proximity_dic['sp_policy_id'] = db_proximity_obj['sp_policy_id']
            d_proximity_dic['name'] = db_proximity_obj['sp_policy_id']
            # handling delete proximity method in RPC
            response = self.rpc_api.glsb_math(context, d_proximity_dic,
                                              "delete_sp_policy")
        except Exception:
            LOG.error(_LE("Delete corresponding response on device failed"))
            # since delete failed in device, so re-update back object in DB
            proximity_obj.update(context, id, result_proximity)
            # raise the exception for catch
            raise
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        return response

    def update_sp_policy(self, context, proximity, id):
        """
        update proximity handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        input_str = json.dumps(proximity)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'UPDATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # get the proximity info by id
        result_proximity = self.get_proximity_db_detail(context, id)
        # update the proximity in device
        proximity['priority'] = proximity['new_priority']
        try:
            u_proximity_dic = {}
            u_proximity_dic['sp_policy_id'] = result_proximity['sp_policy_id']
            u_proximity_dic['name'] = result_proximity['sp_policy_id']
            # the dic for update by device
            update_region_dic = tools.dict_merge(proximity, u_proximity_dic)
            # handling delete proximity method in RPC
            response = self.rpc_api.glsb_math(context, update_region_dic,
                                              "update_sp_policy")
        except Exception:
            LOG.error(_LE("Delete corresponding response on device failed"))
            # raise the exception for catch
            raise
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history['id'], **input_operation_history)
        # get the uuid from db
        response['id'] = id
        return response

    def get_sp_policy(self, context, id):
        """getting target policy details from dns device"""
        # query the sp_policy_info to get the value of name
        query_sp_policy_dic = {}
        query_sp_policy_dic['id'] = id
        sp_policy_obj = objects.SP_Policy(context)
        # Check the region which have same name if is exist in DB
        target_sp_policy = self._valid_if_obj_exist(context, sp_policy_obj,
                                                    query_sp_policy_dic)
        if target_sp_policy is None:
            LOG.warning(_LW("The object of %(param_name)s don't exist!") + id)
            raise exception.IsNotExistError(param_name=id)
        sp_policy_dic = {}
        sp_policy_dic['name'] = target_sp_policy['sp_policy_id']
        try:
            # handling policy method in RPC
            response = self.rpc_api.glsb_math(context, sp_policy_dic,
                                              "get_sp_policy")
            response["id"] = id
        except Exception as e:
            raise e
        return response

    def get_sp_policys(self, context):
        """handling policys method in RPC"""
        try:
            # handling policys method in RPC
            response = self.rpc_api.glsb_math(context, {}, "get_sp_policys")
        except Exception as e:
            raise e
        return response

    def get_proximity_db_detail(self, context, id):
        """Todo call DB to get one proximity"""
        # init the DB operations object
        region_obj = objects.SP_Policy(context)
        region_query_dic = {}
        region_query_dic['id'] = id
        region_query_dic['deleted'] = False
        # try/catch the no one get
        try:
            # Todo call DB to get one region by id
            region_obj = region_obj.get_object(context, **region_query_dic)
        except Exception:
            LOG.warning(_LW("No proximity with id=%(id)s in DB"), {"id": id})
            raise exception.IsNotExistError(param_name="proximity id=" + id)
        return region_obj

    def get_all_db_proximity(self, context):
        """Todo call DB to get all proximitys"""
        # init the DB operations object
        proximity_obj = objects.SP_Policy(context)
        # Filter the data that has been disabled
        query_proximity_dic = {}
        query_proximity_dic['deleted'] = False
        # Todo call DB to get all proximitys
        proximity_objs = proximity_obj.get_objects(context,
                                                   **query_proximity_dic)
        if proximity_objs is None:
            LOG.warning(_LW("There is no data in the dns_proximity_info"))
            raise exception.IsNotExistError(param_name="proximity id=" + id)
        return proximity_objs

    def get_db_proximitys(self, context, proximitys):
        """Todo call DB to get all proximitys"""
        # init the DB operations object
        proximity_obj = objects.SP_Policy(context)
        # Filter the data that has been disabled
        proximitys['deleted'] = "0"
        # get the like values
        like_list = ['src_data1', 'dst_data1']
        # get the union values
        search_list = ['src_type', 'src_logic', 'dst_type', 'dst_logic',
                       'tenant_id', 'deleted']
        # get the run sqlstr
        like_dic, search_dic = tools.classfiy_sql_keys(proximitys, like_list,
                                                       search_list)
        proximitys_objs = proximity_obj.get_all_objects_by_conditions(
            context, like_dic, search_dic)
        if proximitys_objs is None:
            LOG.warning(_LW("There is no data in the dns_proximity_info"))
            raise exception.IsNotExistError(param_name="proximity id=" + id)
        return proximitys_objs

    # operation gmembers
    def get_gmembers_db(self, context, dic):
        """get all gmembers"""
        obj = objects.Gmember(context)
        dic['deleted'] = "0"
        like_list = ['name', 'gslb_zone_name', 'ip']
        search_list = ["tenant_id", "port", "enable", "deleted"]
        like_dic, search_dic = tools.classfiy_sql_keys(dic, like_list,
                                                       search_list)
        query = obj.get_all_objects_by_conditions(context, like_dic,
                                                  search_dic)
        return query

    # operation gmembers
    def get_gmembers_db_restful(self, context):
        """get all gmembers"""
        gmember_kwarg = {}
        gmember_kwarg["deleted"] = False
        gmember_instance = objects.Gmember(context, **gmember_kwarg)
        return gmember_instance.get_objects(context, **gmember_kwarg)

    def get_one_gmember_db(self, context, gmember_uuid):
        """get a gmember"""
        gmember_kwarg = {}
        gmember_kwarg["id"] = gmember_uuid
        gmember_kwarg["deleted"] = False
        gmember_instance = objects.Gmember(context, **gmember_kwarg)
        try:
            gme_info = gmember_instance.get_object(context, **gmember_kwarg)
        except Exception:
            raise exception.IsNotExistError(param_name=gmember_uuid)
        return gme_info

    def create_gmember(self, context, dic):
        """create a gmember"""
        # insert operation history type with Creating in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "CREATE_GMEMBER",
                                                         "FAILED")
        history = self.db_common.insert_operation_history(context,
                                                          **history_kwargs)
        # check gslb_zone  is or not exsit
        gslb_zone_kwarg = {}
        gslb_zone_kwarg["tenant_id"] = dic["tenant_id"]
        gslb_zone_kwarg["name"] = dic["gslb_zone_name"]
        gslb_zone_kwarg["deleted"] = False

        try:
            instance = objects.GslbZone(context, **gslb_zone_kwarg)
            instance.get_object_one(context, **gslb_zone_kwarg)
        except Exception as e:
            raise exception.IsNotExistError(param_name=dic["gslb_zone_name"])
        gmember_kwarg = {}
        gmember_kwarg["tenant_id"] = dic["tenant_id"]
        gmember_kwarg["name"] = dic["name"]
        gmember_kwarg['deleted'] = False
        try:
            instance = objects.Gmember(context, **gmember_kwarg)
            get_gmember = instance.get_object(context, **gmember_kwarg)
        except Exception:
            get_gmember = None
        # check gmember is or not exsit
        if get_gmember is not None:
            raise exception.HaveSameObject(param_name=dic["name"])
        gmember_args = {}
        gmember_args["ip"] = dic["ip"]
        gmember_args["port"] = dic["port"]
        gmember_args['deleted'] = False
        try:
            instance_args = objects.Gmember(context, **gmember_args)
            gmember_args_info = instance_args.get_object(context,
                                                         **gmember_args)
        except Exception:
            gmember_args_info = None
        # check gmember is or not exsit
        if gmember_args_info is not None:
            param_name = '%s and %s' % (dic["ip"], dic["port"])
            raise exception.HaveSameError(param_name=param_name)

        create_instance = objects.Gmember(context, **dic)
        # return response from DB
        response_create = self.db_common.create_in_storage(context,
                                                           create_instance)
        try:
            response_dev = self.rpc_api.glsb_math(context, dic,
                                                  "create_gmember")
        except Exception as e:
            LOG.error(_LE("Create response on device failed"))
            # since create failed in device, so delete object in DB
            error_instance = objects.Gmember(context)
            error_instance.delete(context, response_create["id"])
            raise e
        # update dns_gmember_info table, since record id would be changed
        update_info = {}
        update_info["refcnt"] = response_dev["refcnt"]
        update_info["gmember_id"] = response_dev["id"]
        update_instance = objects.Gmember(context, **update_info)
        response_db = update_instance.update(context,
                                             response_create["id"],
                                             update_info)
        # update operation history type with Failed in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "CREATE_GMEMBER",
                                                         "SUCCESS")
        self.db_common.update_operation_history(context, history['id'],
                                                **history_kwargs)
        return response_db

    def update_gmember(self, context, dic, gmember_uuid):
        """update gmember info"""
        # insert operation history type with Creating in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "UPDATE_GMEMBER",
                                                         "FAILED")
        history = self.db_common.insert_operation_history(context,
                                                          **history_kwargs)
        gmember_kwarg = {}
        gmember_kwarg["id"] = gmember_uuid
        gmember_kwarg['deleted'] = False
        gmember = objects.Gmember(context, **gmember_kwarg)
        try:
            gmemberinfo = gmember.get_object(context, **gmember_kwarg)
        except Exception:
            raise exception.IsNotExistError(param_name=gmember_uuid)
        values = {}
        values["enable"] = dic["enable"]
        gmember_instance = objects.Gmember(context, **values)
        gmember_upd = gmember_instance.update(context, gmember_uuid, values)
        dic["gmember_id"] = gmember_upd["gmember_id"]
        gslb_zone_kwarg = {}
        gslb_zone_kwarg["tenant_id"] = gmember_upd["tenant_id"]
        gslb_zone_kwarg["name"] = gmember_upd["gslb_zone_name"]
        gslb_zone_kwarg['deleted'] = False
        gslb_instance = objects.GslbZone(context, **gslb_zone_kwarg)
        try:
            gslb_info = gslb_instance.get_object(context, **gslb_zone_kwarg)
        except Exception:
            raise exception.IsNotExistError(param_name="the gslb_zone ")
        dic["gslb_zone_name"] = gslb_info["name"]
        dic["gmember_name"] = gmemberinfo["gmember_id"]
        try:
            self.rpc_api.glsb_math(context, dic, "update_gmember")
        except Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            gmember.update(context, gmember_uuid, gmemberinfo)
            raise e
        # update operation history type with Failed in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "UPDATE_GMEMBER",
                                                         "SUCCESS")
        self.db_common.update_operation_history(context, history['id'],
                                                **history_kwargs)
        return gmember_upd

    def delete_gmember(self, context, gmember_uuid):
        """delete target gmember"""
        # insert operation history type with Creating in DB
        history_kwargs = self.db_common.history_col_info("delete_gmember",
                                                         "DELETE_GMEMBER",
                                                         "FAILED")
        history = self.db_common.insert_operation_history(context,
                                                          **history_kwargs)
        gmember_kwarg = {}
        gmember_kwarg["id"] = gmember_uuid
        gmember_kwarg['deleted'] = False
        gmember = objects.Gmember(context, **gmember_kwarg)
        try:
            gmemberinfo = gmember.get_object(context, **gmember_kwarg)
        except Exception:
            raise exception.IsNotExistError(param_name=gmember_uuid)
        gmember_del = gmember.delete(context, gmember_uuid)
        dic = {}
        dic["gmember_id"] = gmember_del["gmember_id"]
        gslb_zone_kwarg = {}
        gslb_zone_kwarg["tenant_id"] = gmember_del["tenant_id"]
        gslb_zone_kwarg["name"] = gmember_del["gslb_zone_name"]
        gslb_zone_kwarg['deleted'] = False
        gslb_instance = objects.GslbZone(context, **gslb_zone_kwarg)
        try:
            gslb_info = gslb_instance.get_object(context, **gslb_zone_kwarg)
        except Exception:
            raise exception.IsNotExistError(param_name="the gslb_zone ")
        dic["gslb_zone_name"] = gslb_info["name"]
        try:
            response_dev = self.rpc_api.glsb_math(context,
                                                  dic, "delete_gmember")
        except Exception as e:
            LOG.error(_LE("Delete corresponding response on device failed"))

            gmember.update(context, gmember_uuid, gmemberinfo)
            raise e
        # update operation history type with Failed in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "DELETE_GMEMBER",
                                                         "SUCCESS")
        self.db_common.update_operation_history(context, history['id'],
                                                **history_kwargs)
        return response_dev

    def get_hm_templates_db(self, context, dic):
        """get all hm_templates"""
        obj = objects.HmTemplate(context)
        dic['deleted'] = "0"
        like_list = ['name']
        search_list = ["tenant_id", "deleted"]
        like_dic, search_dic = tools.classfiy_sql_keys(dic,
                                                       like_list, search_list)
        query = obj.get_all_objects_by_conditions(context, like_dic,
                                                  search_dic)
        return query

    def get_one_hm_template_db(self, context, template_uuid):
        """get a hm_template"""
        hm_template_kwarg = {}
        hm_template_kwarg["id"] = template_uuid
        hm_template_kwarg["deleted"] = False
        instance = objects.HmTemplate(context, **hm_template_kwarg)
        try:
            hm_template_info = instance.get_object(context,
                                                   **hm_template_kwarg)
        except Exception:
            raise exception.IsNotExistError(param_name=template_uuid)
        return hm_template_info

    def create_hm_template(self, context, dic):
        """create a hm_template"""
        # insert operation history type with Creating in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "ADD_HM_TEMPLATE",
                                                         "FAILED")
        history = self.db_common.insert_operation_history(context,
                                                          **history_kwargs)
        # check gslb_zone  is or not exsit
        hm_template_kwarg = {}
        hm_template_kwarg["tenant_id"] = dic["tenant_id"]
        hm_template_kwarg["name"] = dic["name"]
        hm_template_kwarg['deleted'] = False
        try:
            instance = objects.HmTemplate(context, **hm_template_kwarg)
            get_hm_template = instance.get_object(context, **hm_template_kwarg)
        except Exception:
            get_hm_template = None
        if get_hm_template is not None:
            raise exception.HaveSameObject(param_name=dic["name"])
        create_instance = objects.HmTemplate(context, **dic)
        # return response from DB
        response_db = self.db_common.create_in_storage(context,
                                                       create_instance)
        try:
            response_dev = self.rpc_api.glsb_math(context, dic,
                                                  "create_hm_template")
        except Exception as e:
            LOG.error(_LE("Create response on device failed"))
            # since create failed in device, so delete object in DB
            error_instance = objects.HmTemplate(context)
            error_instance.delete(context, response_db["id"])
            raise e
        # update dns_gmember_info table, since record id would be changed
        update_info = {}
        update_info["hm_template_id"] = response_dev["id"]
        update_info["refcnt"] = response_dev["refcnt"]
        update_instance = objects.HmTemplate(context, **update_info)
        response_db = update_instance.update(context,
                                             response_db["id"],
                                             update_info)

        # update operation history type with Failed in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "ADD_HM_TEMPLATE",
                                                         "SUCCESS")
        self.db_common.update_operation_history(context, history['id'],
                                                **history_kwargs)
        return response_db

    def update_hm_template(self, context, dic, template_uuid):
        """update hm_template info"""
        # insert operation history type with Creating in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "UPT_HM_TEMPLATE",
                                                         "FAILED")
        history = self.db_common.insert_operation_history(context,
                                                          **history_kwargs)
        hm_template_kwarg = {}
        hm_template_kwarg["id"] = template_uuid
        hm_template_kwarg['deleted'] = False
        hm_template = objects.HmTemplate(context, **hm_template_kwarg)
        try:
            hm_template_info = hm_template.get_object(context,
                                                      **hm_template_kwarg)
        except Exception:
            raise exception.IsNotExistError(param_name=template_uuid)

        hm_template_instance = objects.HmTemplate(context, **dic)
        hm_template_upd = hm_template_instance.update(context,
                                                      template_uuid, dic)
        dic["hm_template_id"] = hm_template_info["hm_template_id"]
        try:
            self.rpc_api.glsb_math(context, dic, "update_hm_template")
        except Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            hm_template.update(context, template_uuid, hm_template_info)
            raise e
        # update operation history type with Failed in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "UPT_HM_TEMPLATE",
                                                         "SUCCESS")
        self.db_common.update_operation_history(context, history['id'],
                                                **history_kwargs)
        return hm_template_upd

    def delete_hm_template(self, context, template_uuid):
        """delete target hm_template"""
        # insert operation history type with Creating in DB
        history_kwargs = self.db_common.history_col_info("delete_hm_template",
                                                         "DEL_HM_TEMPLATE",
                                                         "FAILED")
        history = self.db_common.insert_operation_history(context,
                                                          **history_kwargs)
        hm_template_kwarg = {}
        hm_template_kwarg["id"] = template_uuid
        hm_template_kwarg['deleted'] = False
        instance = objects.HmTemplate(context, **hm_template_kwarg)
        try:
            hm_template_info = instance.get_object(context,
                                                   **hm_template_kwarg)
        except Exception:
            raise exception.IsNotExistError(param_name=template_uuid)
        hm_template_del = instance.delete(context, template_uuid)
        dic = {}
        dic["hm_template_id"] = hm_template_del["hm_template_id"]
        try:
            response_dev = self.rpc_api.glsb_math(context,
                                                  dic, "delete_hm_template")
        except Exception as e:
            LOG.error(_LE("Delete corresponding response on device failed"))
            instance.update(context, template_uuid, hm_template_info)
            raise e
        # update operation history type with Failed in DB
        history_kwargs = self.db_common.history_col_info(dic,
                                                         "DEL_HM_TEMPLATE",
                                                         "SUCCESS")
        self.db_common.update_operation_history(context, history['id'],
                                                **history_kwargs)
        return response_dev

    # this is a gslb_zone operation
    def create_gslb_zone(self, context, dns_object):
        """
        update gslb_zone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB
        input_str = json.dumps(dns_object)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'CREATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # input the staticnat values with dic format
        gslb_obj = objects.GslbZone(context, **dns_object)
        # create the staticnat info in db
        result = gslb_obj.create(context, gslb_obj.as_dict())
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)

        response_dev = self.rpc_api.glsb_math(context, dns_object,
                                              "create_gslb_zone")
        update_info = {}
        update_info["gslb_zone_id"] = response_dev["id"]
        instance = objects.GslbZone(context, **update_info)
        response_db = instance.update(context, result["id"], update_info)
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return response_db

    def del_gslb_zone(self, context, dns_object):
        """
        delete gslb_zone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        input_str = json.dumps(dns_object)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'delete'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # input the staticnat values with dic format
        gslb_obj = objects.GslbZone(context, **dns_object)
        # create the staticnat info in db
        result = gslb_obj.delete(context, dns_object['id'])
        dns_object["name"] = result["name"]
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        response = self.rpc_api.glsb_math(context, dns_object,
                                          "delete_gslb_zone")
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return response

    def update_gslb_zone(self, context, zone_id, dns_object):
        """
        update gslb_zone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        # insert operation history type with Creating in DB

        input_str = json.dumps(dns_object)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'update'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
            context, **input_operation_history)
        # input the staticnat values with dic format
        gslb_obj = objects.GslbZone(context, **dns_object)
        # create the staticnat info in db
        result = gslb_obj.update(context, zone_id, gslb_obj.as_dict())
        # response_fw = self.rpc_api.creat_addrobj(context, addrobj_infos)
        dns_object["name"] = result["name"]
        self.rpc_api.glsb_math(context, dns_object, "update_gslb_zone")
        self.db_common.update_operation_history(
            context, history['id'], status='SUCCESS')
        return result

    def get_gslb_zone(self, context, dns_object):
        """
        get gslb_zone handling DB operations
        """
        # input the staticnat values with dic format
        gslb_obj = objects.GslbZone(context, **dns_object)
        # create the staticnat info in db
        result = gslb_obj.get_object(context, **dns_object)
        return result

    def get_gslb_zones(self, context, dns_object):
        """
        get_all gslb_zone handling DB operations
        """
        # input the staticnat values with dic format
        gslb_obj = objects.GslbZone(context, **dns_object)
        # create the staticnat info in db
        result = gslb_obj.get_objects(context, **dns_object)
        return result

    def _valid_if_exists(self, context, obj):
        name_dic = {}
        name_dic['name'] = obj.name
        name_dic['deleted'] = False
        target = None
        try:
            # get the zone in db
            target = obj.get_object(context, **name_dic)
        except Exception as e:
            pass
        return target

    def _get_syngroup_db_detail(self, context, id):
        """
        get syngroup detail in db
        :param context:
        :param id:
        :return:
        """
        name_dic = {}
        name_dic['id'] = id
        name_dic['deleted'] = False
        Syngroup_obj = objects.SynGroup(context)
        target = None
        try:
            target = Syngroup_obj.get_object(context, **name_dic)
        except Exception:
            LOG.warning(_LW("No Syngroup with id = %(id)s in DB"), {"id": id})
            raise exception.IsNotExistError(
                param_name="Syngroup with id=" + id)
        return target

    def create_gpool(self, context, gpool_dict):
        # create gpool
        gpool_db_dict = copy.deepcopy(gpool_dict)
        if 'pass' in gpool_db_dict.keys():
            gpool_db_dict['pass_'] = gpool_db_dict['pass']
            del gpool_db_dict['pass']
        gpool_db_create_obj = objects.GPool(
            context, **gpool_db_dict
        )
        if self._valid_if_exists(context, gpool_db_create_obj) is not None:
            LOG.warning(_LW('Have same gpool id/name in DB'))
            raise exception.HaveSameObject(param_name=gpool_db_dict['name'])
        history_str = json.dumps(gpool_db_dict)
        operation_history_dict = {}
        operation_history_dict['input'] = history_str
        operation_history_dict['method'] = "CREATE"
        operation_history_dict['status'] = 'FAILD'
        history_obj = self.db_common.insert_operation_history(
            context, **operation_history_dict
        )
        gpool_db_create_ret_obj = self._create_in_storage(
            context, gpool_db_create_obj)
        response = None
        try:
            gpool_rpc_dict = copy.deepcopy(gpool_dict)
            # gpool_rpc_dict['current_user'] = "admin"
            del gpool_rpc_dict['tenant_id']
            response = self.rpc_api.glsb_math(
                context, gpool_rpc_dict, 'create_gpool')
        except MessagingTimeout as e:
            LOG.error(_LE("Create corresponding response on device failed"))
            gpool_db_create_obj.delete(context, gpool_db_create_ret_obj['id'])
            raise e
        except Exception as e:
            LOG.error(_LE("Create corresponding response on device failed"))
            gpool_db_create_obj.delete(context, gpool_db_create_ret_obj['id'])
            raise e
        id = gpool_db_create_ret_obj['id']
        gpool_db_update_dict = response
        gpool_db_update_dict['gpool_id'] = response['id']
        if gpool_db_update_dict['hms'] == "":
            gpool_db_update_dict['hms'] = []
        gpool_db_update_dict['pass_'] = gpool_db_update_dict['pass']
        del gpool_db_update_dict['id'], gpool_db_update_dict['status']
        del gpool_db_update_dict['pass'], gpool_db_update_dict['gmember_list']
        gpool_db_update_obj = objects.GPool(context)
        gpool_db_update_ret_obj = gpool_db_update_obj.update(
            context, id, gpool_db_update_dict)
        operation_history_dict['status'] = "SUCCESS"
        self.db_common.update_operation_history(
            context, history_obj['id'], **operation_history_dict
        )
        gpool_db_update_ret_dic = self._replace_pass(gpool_db_update_ret_obj)
        return gpool_db_update_ret_dic

    def update_gpool(self, context, gpool_dict):
        # update gpool
        id = gpool_dict['id']
        del gpool_dict['id']
        gpool_db_org_obj = self._get_gpool_db_detail(context, id)
        gpool_db_dict = copy.deepcopy(gpool_dict)
        if 'pass' in gpool_db_dict.keys():
            gpool_db_dict['pass_'] = gpool_db_dict['pass']
            del gpool_db_dict['pass']
        # for key in gpool_db_dict.keys():
        #     gpool_db_dict[key] = str(gpool_db_dict[key])
        gpool_db_update_obj = objects.GPool(context, **gpool_db_dict)
        history_str = json.dumps(gpool_db_dict)
        operation_history_dict = {}
        operation_history_dict['input'] = history_str
        operation_history_dict['method'] = "CREATE"
        operation_history_dict['status'] = 'FAILD'
        history_obj = self.db_common.insert_operation_history(
            context, **operation_history_dict
        )
        gpool_db_update_ret_obj = gpool_db_update_obj.update(
            context, id, gpool_db_update_obj.as_dict())
        try:
            gpool_rpc_dict = copy.deepcopy(gpool_dict)
            # gpool_rpc_dict['current_user'] = 'admin'
            # del gpool_rpc_dict['tenant_id']
            gpool_rpc_dict['name'] = gpool_db_org_obj['gpool_id']
            if 'type' in gpool_rpc_dict.keys():
                gpool_rpc_dict['cname'] = gpool_rpc_dict['type']
                del gpool_rpc_dict['type']
            response = self.rpc_api.glsb_math(
                context, gpool_rpc_dict, 'update_gpool'
            )
        except MessagingTimeout as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            gpool_db_update_obj.update(context, id, gpool_db_org_obj)
            raise e
        except Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            gpool_db_update_obj.update(context, id, gpool_db_org_obj)
            raise
        operation_history_dict['status'] = "SUCCESS"
        self.db_common.update_operation_history(
            context, history_obj['id'], **operation_history_dict
        )
        gpool_db_update_ret_dic = self._replace_pass(gpool_db_update_ret_obj)
        return gpool_db_update_ret_dic

    def delete_gpool(self, context, values):
        # delete gpool
        id = values['id']
        gpool_db_org_obj = self._get_gpool_db_detail(context, id)
        gpool_db_del_obj = objects.GPool(context)
        operation_str = json.dumps({})
        operation_history_dict = {}
        operation_history_dict['input'] = operation_str
        operation_history_dict['method'] = "CREATE"
        operation_history_dict['status'] = 'FAILD'
        history_obj = self.db_common.insert_operation_history(
            context, **operation_history_dict
        )
        gpool_db_del_ret_obj = gpool_db_del_obj.delete(
            context, id)
        response = None
        try:
            gpool_rpc_del_dict = {'name': gpool_db_org_obj['gpool_id']}
            response = self.rpc_api.glsb_math(
                context, gpool_rpc_del_dict, 'delete_gpool'
            )
        except MessagingTimeout as e:
            LOG.error(_LE("Delete corresponding response on device failed"))
            gpool_db_del_obj.update(context, id, gpool_db_org_obj)
            raise e
        except Exception as e:
            LOG.error(_LE("Delete corresponding response on device failed"))
            gpool_db_del_obj.update(context, id, gpool_db_org_obj)
            raise
        operation_history_dict['status'] = "SUCCESS"
        self.db_common.update_operation_history(
            context, history_obj['id'], **operation_history_dict
        )
        gpool_db_del_ret_obj = self._replace_pass(gpool_db_del_ret_obj)
        return {"result": "success"}

    def get_gpool(self, context, id):
        # get gpool not use
        gpool_obj = self._get_gpool_db_detail(context, id)
        gpool_obj = self._replace_pass(gpool_obj)
        return gpool_obj

    def get_gpools(self, context, values):
        # list gpools
        gpool_obj = objects.GPool(context)
        name_dic = values
        name_dic['deleted'] = '0'
        like_list = [
            'name',
            'cname',
            'hms',
            'gmember_list', 'ttl'
        ]
        search_list = [
            'tenant_id',
            'enable',
            'warning',
            'deleted',
            'first_algorithm',
            'second_algorithm',
        ]
        like_dic, search_dic = tools.classfiy_sql_keys(name_dic,
                                                       like_list, search_list)
        gpool_objs = gpool_obj.get_all_objects_by_conditions(context,
                                                             like_dic,
                                                             search_dic)
        result = []
        for syngroup_obj in gpool_objs:
            result.append(self._replace_pass(syngroup_obj))
        return result

    def _get_gpool_db_detail(self, context, id):
        # get gpool info in db
        name_dict = {}
        name_dict['id'] = id
        name_dict['deleted'] = False
        gpool_obj = objects.GPool(context)
        target = None
        try:
            target = gpool_obj.get_object(context, **name_dict)
        except Exception:
            LOG.warning(_LW("No GPool with id = %(id)s in DB"), {"id": id})
            raise exception.IsNotExistError(
                param_name="GPool with id=" + id)
        return target

    def create_gmap(self, context, gmap_dict):
        # create gmap
        gmap_db_dict = copy.deepcopy(gmap_dict)
        # if 'gpool_list' in gmap_db_dict.keys():
        #     gmap_db_dict["gpool_list"] = str(gmap_db_dict['gpool_list'])
        gmap_db_create_obj = objects.GMap(
            context, **gmap_db_dict
        )
        if self._valid_if_exists(context, gmap_db_create_obj) is not None:
            LOG.warning(_LW('Have same gmap id/name in DB'))
            raise exception.HaveSameObject(param_name=gmap_db_dict['name'])
        history_str = json.dumps(gmap_db_dict)
        operation_history_dict = {}
        operation_history_dict['input'] = history_str
        operation_history_dict['method'] = "CREATE"
        operation_history_dict['status'] = 'FAILD'
        history_obj = self.db_common.insert_operation_history(
            context, **operation_history_dict
        )
        gmap_db_create_ret_obj = self._create_in_storage_gmap(
            context, gmap_db_create_obj)
        response = None
        try:
            gmap_rpc_dict = gmap_dict
            del gmap_rpc_dict['tenant_id']
            response = self.rpc_api.glsb_math(
                context, gmap_rpc_dict, 'create_gmap')
        except MessagingTimeout as e:
            LOG.error(_LE("Create corresponding response on device failed"))
            gmap_db_create_obj.delete(context, gmap_db_create_ret_obj['id'])
            raise e
        except Exception as e:
            LOG.error(_LE("Create corresponding response on device failed"))
            gmap_db_create_obj.delete(context, gmap_db_create_ret_obj['id'])
            raise
        id = gmap_db_create_ret_obj['id']
        gmap_db_update_dict = response
        gmap_db_update_dict['gmap_id'] = response['id']
        del gmap_db_update_dict['id']
        gmap_db_update_obj = objects.GMap(context, **gmap_db_update_dict)
        gmap_db_update_ret_obj = gmap_db_update_obj.update(
            context, id, gmap_db_update_dict)
        operation_history_dict['status'] = "SUCCESS"
        self.db_common.update_operation_history(
            context, history_obj['id'], **operation_history_dict
        )
        return gmap_db_update_ret_obj

    def update_gmap(self, context, gmap_dict):
        # update gmap
        id = gmap_dict['id']
        del gmap_dict['id']
        gmap_db_org_obj = self._get_gmap_db_detail(context, id)
        gmap_db_dict = copy.deepcopy(gmap_dict)
        gmap_db_update_obj = objects.GMap(context, **gmap_db_dict)
        history_str = json.dumps(gmap_db_dict)
        operation_history_dict = {}
        operation_history_dict['input'] = history_str
        operation_history_dict['method'] = "CREATE"
        operation_history_dict['status'] = 'FAILD'
        history_obj = self.db_common.insert_operation_history(
            context, **operation_history_dict
        )
        gmap_db_update_ret_obj = gmap_db_update_obj.update(
            context, id, gmap_db_update_obj.as_dict())
        try:
            gmap_rpc_dict = copy.deepcopy(gmap_dict)
            gmap_rpc_dict['name'] = gmap_db_org_obj.gmap_id
            response = self.rpc_api.glsb_math(
                context, gmap_rpc_dict, 'update_gmap'
            )
        except MessagingTimeout as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            gmap_db_update_obj.update(context, id, gmap_db_org_obj)
            raise e
        except Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            gmap_db_update_obj.update(context, id, gmap_db_org_obj)
            raise
        operation_history_dict['status'] = "SUCCESS"
        self.db_common.update_operation_history(
            context, history_obj['id'], **operation_history_dict
        )
        return gmap_db_update_ret_obj

    def delete_gmap(self, context, values):
        # delete gmap
        id = values['id']
        gmap_db_org_obj = self._get_gmap_db_detail(context, id)
        gmap_db_del_obj = objects.GMap(context)
        operation_str = json.dumps({})
        operation_history_dict = {}
        operation_history_dict['input'] = operation_str
        operation_history_dict['method'] = "CREATE"
        operation_history_dict['status'] = 'FAILD'
        history_obj = self.db_common.insert_operation_history(
            context, **operation_history_dict
        )
        gmap_db_del_ret_obj = gmap_db_del_obj.delete(context, id)
        reponse = None
        try:
            gmap_rpc_dict = {'name': gmap_db_org_obj.gmap_id}
            reponse = self.rpc_api.glsb_math(
                context, gmap_rpc_dict, "delete_gmap"
            )
        except MessagingTimeout as e:
            LOG.error(_LE("Delete corresponding response on device failed"))
            gmap_db_del_obj.update(context, id, gmap_db_org_obj)
            raise e
        except Exception as e:
            LOG.error(_LE("Delete corresponding response on device failed"))
            gmap_db_del_obj.update(context, id, gmap_db_org_obj)
            raise
        operation_history_dict['status'] = "SUCCESS"
        self.db_common.update_operation_history(
            context, history_obj['id'], **operation_history_dict
        )
        return {"result": "success"}

    def get_gmap(self, context, id):
        # get gmap
        gmap_obj = self._get_gmap_db_detail(context, id)
        return gmap_obj

    def get_gmaps(self, context, values):
        # list gmaps
        gmap_obj = objects.GMap(context)
        name_dic = values
        name_dic['deleted'] = '0'
        like_list = ['name', 'gpool_list', 'last_resort_pool']
        search_list = ['tenant_id', 'algorithm', 'deleted', 'enable']
        like_dic, search_dic = tools.classfiy_sql_keys(name_dic, like_list,
                                                       search_list)
        gmap_objs = gmap_obj.get_all_objects_by_conditions(context, like_dic,
                                                           search_dic)
        return gmap_objs

    def _get_gmap_db_detail(self, context, id):
        name_dict = {}
        name_dict['id'] = id
        name_dict['deleted'] = False
        gpool_obj = objects.GMap(context)
        target = None
        try:
            target = gpool_obj.get_object(context, **name_dict)
        except Exception:
            LOG.warning(_LW("No GMap with id = %(id)s in DB"), {"id": id})
            raise exception.IsNotExistError(
                param_name="GMap with id=" + id)
        return target

    def create_syngroup(self, context, syngroup_dict):
        # create syngroup
        syngroup_db_dict = copy.deepcopy(syngroup_dict)
        if 'pass' in syngroup_db_dict.keys():
            syngroup_db_dict['pass_'] = syngroup_db_dict['pass']
            del syngroup_db_dict['pass']
        syngroup_db_dict['syngroup_id'] = '1'
        syngroup_db_create_obj = objects.SynGroup(
            context, **syngroup_db_dict
        )
        if self._valid_if_exists(context, syngroup_db_create_obj) is not None:
            LOG.warning(_LW('Have same syngroup id/name in DB'))
            raise exception.HaveSameObject(
                param_name=syngroup_db_dict['name'])
        history_str = json.dumps(syngroup_db_dict)
        operation_history_dict = {}
        operation_history_dict['input'] = history_str
        operation_history_dict['method'] = "CREATE"
        operation_history_dict['status'] = 'FAILD'
        history_obj = self.db_common.insert_operation_history(
            context, **operation_history_dict
        )
        syngroup_db_create_ret_obj = self._create_in_storage(
            context, syngroup_db_create_obj)
        response = None
        try:
            syngroup_rpc_dict = copy.deepcopy(syngroup_dict)
            # syngroup_rpc_dict['current_user'] = "admin"
            if 'gslb_zone_names' in syngroup_rpc_dict.keys():
                syngroup_rpc_dict['dcs'] = syngroup_rpc_dict['gslb_zone_names']
                del syngroup_rpc_dict['gslb_zone_names']
            del syngroup_rpc_dict['tenant_id']
            response = self.rpc_api.glsb_math(
                context, syngroup_rpc_dict, 'create_syngroup')
        except MessagingTimeout as e:
            LOG.error(_LE("Create corresponding response on device failed"))
            syngroup_db_create_obj.delete(
                context, syngroup_db_create_ret_obj['id'])
            raise e
        except Exception as e:
            LOG.error(_LE("Create corresponding response on device failed"))
            syngroup_db_create_obj.delete(
                context, syngroup_db_create_ret_obj['id'])
            raise
        id = syngroup_db_create_ret_obj['id']
        syngroup_db_update_dict = response
        syngroup_db_update_dict['syngroup_id'] = response['id']
        syngroup_db_update_dict['gslb_zone_names'] = response['dcs']
        syngroup_db_update_dict['pass_'] = response['pass']
        del syngroup_db_update_dict['id'], syngroup_db_update_dict[
            'pass'], syngroup_db_update_dict['dcs']
        syngroup_db_update_obj = objects.SynGroup(
            context, **syngroup_db_update_dict)
        syngroup_db_update_ret_obj = syngroup_db_update_obj.update(
            context, id, syngroup_db_update_dict)
        operation_history_dict['status'] = "SUCCESS"
        self.db_common.update_operation_history(
            context, history_obj['id'], **operation_history_dict
        )
        syngroup_db_update_ret_dic = self._replace_pass(
            syngroup_db_update_ret_obj)
        return syngroup_db_update_ret_dic

    def update_syngroup(self, context, syngroup_dict):
        # update syngroup
        id = syngroup_dict['id']
        del syngroup_dict['id']
        syngroup_db_org_obj = self._get_syngroup_db_detail(context, id)
        syngroup_db_dict = copy.deepcopy(syngroup_dict)
        if 'pass' in syngroup_db_dict.keys():
            syngroup_db_dict['pass_'] = syngroup_db_dict['pass']
            del syngroup_db_dict['pass']
        syngroup_db_update_obj = objects.SynGroup(context)
        history_str = json.dumps(syngroup_db_dict)
        operation_history_dict = {}
        operation_history_dict['input'] = history_str
        operation_history_dict['method'] = "CREATE"
        operation_history_dict['status'] = 'FAILD'
        history_obj = self.db_common.insert_operation_history(
            context, **operation_history_dict)
        syngroup_db_update_obj.update(context, id, syngroup_db_dict)
        try:
            syngroup_rpc_dict = copy.deepcopy(syngroup_dict)
            # syngroup_rpc_dict['current_user'] = 'admin'
            # del syngroup_rpc_dict['tenant_id']
            if 'gslb_zone_names' in syngroup_rpc_dict.keys():
                syngroup_rpc_dict['dcs'] = syngroup_rpc_dict['gslb_zone_names']
                del syngroup_rpc_dict['gslb_zone_names']
            syngroup_rpc_dict['name'] = syngroup_db_org_obj.syngroup_id
            response = self.rpc_api.glsb_math(
                context, syngroup_rpc_dict, "update_syngroup"
            )
        except MessagingTimeout as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            syngroup_db_update_obj.update(context, id, syngroup_db_org_obj)
            raise e
        except Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            syngroup_db_update_obj.update(context, id, syngroup_db_org_obj)
            raise
        operation_history_dict['status'] = "SUCCESS"
        pas_dict = {"pass_": response['pass']}
        replace_pass_obj = objects.SynGroup(context, **pas_dict)
        replace_pass_ret = replace_pass_obj.update(
            context, id, replace_pass_obj.as_dict())
        self.db_common.update_operation_history(
            context, history_obj['id'], **operation_history_dict)
        ret_dic = self._replace_pass(replace_pass_ret)
        return ret_dic

    def delete_syngroup(self, context, syngroup_dict):
        # delete syngroup
        id = syngroup_dict['id']
        syngroup_db_org_obj = self._get_syngroup_db_detail(context, id)
        syngroup_db_del_obj = objects.SynGroup(context)
        operation_str = json.dumps({})
        operation_history_dict = {}
        operation_history_dict['input'] = operation_str
        operation_history_dict['method'] = "CREATE"
        operation_history_dict['status'] = 'FAILD'
        history_obj = self.db_common.insert_operation_history(
            context, **operation_history_dict)
        syngroup_db_del_ret_obj = syngroup_db_del_obj.delete(
            context, id)
        reponse = None
        try:
            syngroup_rpc_dict = {'name': syngroup_db_org_obj.syngroup_id}
            reponse = self.rpc_api.glsb_math(context, syngroup_rpc_dict,
                                             'delete_syngroup')
        except MessagingTimeout as e:
            LOG.error(_LE("Delete corresponding response on device failed"))
            syngroup_db_del_obj.update(context, id, syngroup_db_org_obj)
            raise e
        except Exception as e:
            LOG.error(_LE("Delete corresponding response on device failed"))
            syngroup_db_del_obj.update(context, id, syngroup_db_org_obj)
            raise
        operation_history_dict['status'] = "SUCCESS"
        self.db_common.update_operation_history(
            context, history_obj['id'], **operation_history_dict
        )
        self._replace_pass(syngroup_db_del_ret_obj)
        return {"result": "success"}

    def get_syngroup(self, context, id):
        # get_one syngroup not use
        syngroup_obj = self._get_syngroup_db_detail(context, id)
        syngroup_obj = self._replace_pass(syngroup_obj)
        return syngroup_obj

    def get_syngroups(self, context, values):
        # list syngroups
        syngroup_obj = objects.SynGroup(context)
        name_dic = values
        name_dic['deleted'] = '0'
        like_list = ['name', 'gslb_zone_names']
        search_list = ['tenant_id', 'probe_range', 'deleted']
        like_dic, search_dic = tools.classfiy_sql_keys(
            name_dic, like_list, search_list)
        syngroup_objs = syngroup_obj.get_all_objects_by_conditions(context,
                                                                   like_dic,
                                                                   search_dic)
        result = []
        for syngroup_obj in syngroup_objs:
            result.append(self._replace_pass(syngroup_obj))
        return result

    def get_db_syngroups(self, context, values):
        # get_all_syngroup  not use
        syngroup_obj = objects.SynGroup(context)
        syngroup_db_search_dict = values
        syngroup_db_search_dict['deleted'] = False
        syngroup_objs = syngroup_obj.get_objects(
            context, **syngroup_db_search_dict)
        if syngroup_objs is None:
            LOG.warning(_LW("There is no data in the SYNGROUP_INFO"))
            raise exception.IsNotExistError(
                param_name="GPoll_info table is Null")
        result = []
        for syngroup_obj in syngroup_objs:
            result.append(self._replace_pass(syngroup_obj))
        return result

    def _create_in_storage_gmap(self, context, obj):
        try:
            # create the obj in db
            s_dic = obj.as_dict()
            obj = obj.create(context, s_dic)
        except db_exception:
            LOG.error(_LE("Create/Insert db operation failed!"))
            raise db_exception
        return obj

    def _replace_pass(self, obj):
        # replace pass_ to pass
        dic = dict(obj)
        if "pass_" in dic.keys():
            dic['pass'] = dic['pass_']
            del dic['pass_']
        return dic
