from oslo_config import cfg
from oslo_utils import timeutils
from oslo_serialization import jsonutils as json
from oslo_db import exception as db_exception
from oslo_log import log as logging
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
            raise exception.HaveSameObject(object_name=target_zone.zone_name)
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
            # handling create zone method in RPC
            response = self.rpc_api.create_zone(context, zone)
            # get the default zone records
            zone_id = target_values['zone_id']
            rrs_results = self.rpc_api.get_records(context, zone_id)
            for resourc in rrs_results['resources']:
                records = {}
                records['rrs_id'] = resourc['id']
                records['zone_id'] = db_zone_obj['id']
                records['rrs_name'] = resourc['name']
                records['type'] = resourc['type']
                records['ttl'] = resourc['ttl']
                records['klass'] = resourc['klass']
                records['rdata'] = resourc['rdata']
                # init the DB operations objec with zone_record
                zone_rrs_obj = objects.DnsZoneRrs(context, **records)
                # create the zone info in db
                self._create_in_storage(context, zone_rrs_obj)
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
            # handling delete zone method in RPC
            response = self.rpc_api.delete_zone(context, zone, zone_id)
            raise e
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
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
            zone_id = db_zone_obj['zone_id']
            # handling update zone method in RPC
            response = self.rpc_api.update_zone(context, zone, zone_id)

        except Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            # DB rollback since update failed in Device, to re-update back
            zone_obj.update(context, id, org_db_zone_obj)
            raise e
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
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
            zone_id = db_zone_obj['zone_id']
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
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
        return db_zone_obj

    def delete_zone(self, context, zone, id):
        """
        delete zone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        org_db_zone_obj = self.get_zone_db_details(context, id)
        # init the DB operations object
        zone_obj = objects.DnsZone(context)
        # insert operation history type with Creating in DB
        input_str = json.dumps(zone)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
                        context, **input_operation_history)
        # delete the zone in db
        db_zone_obj = zone_obj.delete(context, id)
        try:
            zone_id = db_zone_obj['zone_id']
            # handling delete zone method in RPC
            response = self.rpc_api.delete_zone(context, zone, zone_id)
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
            zone_obj.update(context, id, org_db_zone_obj.as_dict())
            # raise the exception for catch
            raise e
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
        return response

    def get_zone_one(self, context, zone_id):
        """getting target zone details from dns device"""
        # handling zone method in RPC
        response = self.rpc_api.get_zone_one(context, zone_id)
        return response

    def get_zones(self, context):
        """handling zones method in RPC"""
        # handling zones method in RPC
        response = self.rpc_api.get_zones(context)
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

    def get_dev_records(self, context, zone_id):
        response = self.rpc_api.get_records(context, zone_id)
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
        zone_name_dic['zone_id'] = zone.zone_name
        zone_name_dic['deleted'] = False
        target_zone = None
        try:
            # get the zone in db
            target_zone = zone.get_object(context, **zone_name_dic)
        except Exception:
            pass
        return target_zone

    def _create_in_storage(self, context, obj):
        """create the zone in DB"""
        try:
            # create the zone in db
            obj = obj.create(context, obj.as_dict())
        except db_exception:
            LOG.error(_LE("Create/Insert db operation failed!"))
            raise db_exception
        return obj

    def create_record(self, context, record, zone_id):
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
            raise exception.HaveSameObject(object_name=record['name'])
        # check zone is or not exsit
        target_zone = self.is_exist_zone(context, zone_id)
        # dev_zone_id is zone_id of device
        if target_zone is None:
            raise exception.IsNotExistError(param_name=zone_id)
        dev_zone_id = target_zone["zone_id"]
        LOG.info(_LI("the zone object with id=%(zone_id)s is existed"),
                 {"zone_id": zone_id})
        json_name = record['name']
        zones = self.get_zone_name_bytenant_id(context, record['tenant_id'])
        if len(zones) == 0:
            raise exception.IsNotExistError(param_name="tenant_id")
        flag = True
        for zone in zones:
            dev_zone_name = zone["zone_name"]
            dev_zone_name = '%s%s' % ('.', dev_zone_name)
            if json_name.endswith(dev_zone_name):
                flag = False
                break
        if flag:
            raise exception.ZoneOfRecordIsError(json_name=json_name)
        record_values = self._make_dns_record_object(record, zone_id)
        record_obj = objects.DnsZoneRrs(context, **record_values)
        # return response from DB
        response = self._create_in_storage(context, record_obj)
        new_name = tools.clean_end_str(dev_zone_name, record['name'])
        record['name'] = new_name
        try:
            response_dev = self.rpc_api.create_record(context, record,
                                                      dev_zone_id)
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
            context, history.id, **input_operation_history)
        return response

    def update_record(self, context, record, zone_id, record_id):
        # insert operation history type with Creating in DB
        input_str = json.dumps(record)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'UPDATE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
                        context, **input_operation_history)
        # zone is not exsit
        target_zone = self.is_exist_zone(context, zone_id)
        if target_zone is None:
            raise exception.IsNotExistError(param_name=zone_id)
        record_obj = self.get_record_from_db(context, record_id)
        if record_obj["zone_id"] != zone_id:
            raise exception.RecordNotInZone(record_id=record_id,
                                            zone_id=zone_id)
        dev_zone_id = target_zone["zone_id"]
        LOG.info(_LI("%(zone_id)s is existed"), {"zone_id": zone_id})
        # return response from DB
        response = self.update_rrs_info(context, record_id, record, None)
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
            rrs_obj.update(context, record_id, record_obj)
            # raise the exception for catch
            raise e
        response_upd = self.update_rrs_info(context, record_id,
                                            None, response_dev)
        if ("ttl" in record.keys()) and (record_obj["ttl"] != record["ttl"]):
            self.update_rrs_info_byget_objs(context, zone_id, response_dev)
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
        return response_upd

    def delete_record(self, context, record, zone_id, record_id):
        # insert operation history type with Creating in DB
        input_str = json.dumps(record)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'DELETE'
        input_operation_history['status'] = 'FAILED'
        history = self.db_common.insert_operation_history(
                        context, **input_operation_history)
        # zone is not exsit
        target_zone = self.is_exist_zone(context, zone_id)
        if target_zone is None:
            raise exception.IsNotExistError(param_name=zone_id)
        org_db_record_obj = self.get_record_from_db(context, record_id)
        if org_db_record_obj["zone_id"] != zone_id:
            raise exception.RecordNotInZone(record_id=record_id,
                                            zone_id=zone_id)
        dev_zone_id = target_zone["zone_id"]
        LOG.info(_LI("%(zone_id)s is existed"), {"zone_id": zone_id})
        response = self.delete_rrs_info(context, record_id)
        # dev_rrs_id is rrs_id of device
        dev_rrs_id = response["rrs_id"]
        try:
            # handling delete zone record method in RPC
            # delete a information of dns_rrs_info table from Device
            response_dev = self.rpc_api.delete_record(context, record,
                                                      dev_zone_id,
                                                      dev_rrs_id)
        except Exception as e:
            LOG.error(_LE("Delete response on device failed"))
            # Rollback DB
            rrs_obj = objects.DnsZoneRrs(context)
            rrs_obj.update(context, record_id, org_db_record_obj)
            raise e
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
        return response_dev

    # The following is a method that cleaning the cache !
    def del_cache(self, context, domain):
        """Clear DNS cache"""
        # insert operation history type with Creating in DB
        input_str = json.dumps(domain)
        input_operation_history = {}
        input_operation_history['input'] = input_str
        input_operation_history['method'] = 'UPDATE'
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
        # update operation history type with Failed in DB
        input_operation_history['status'] = 'SUCCESS'
        self.db_common.update_operation_history(
            context, history.id, **input_operation_history)
        return response

    def _make_dns_zone_object(self, zone_values):
        target_values = {}
        for k in zone_values.keys():
            if k == 'name':
                target_values['zone_name'] = zone_values[k]
                target_values['zone_id'] = zone_values[k]
            elif k == 'current_user':
                pass
            else:
                target_values[k] = zone_values[k]
        return target_values

    def _make_dns_record_object(self, record_values, zone_id):
        target_values = {}
        target_values["zone_id"] = zone_id
        for k in record_values.keys():
            if k == 'name':
                target_values['rrs_name'] = record_values[k]
            elif k == 'current_user':
                pass
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
            rrs_resp["ttl"] = dic["ttl"]
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
