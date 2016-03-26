import threading
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

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

CENTRAL_MANAGER = None
RETRY_STATE = threading.local()


class CentralManager(object):
    """
    nca47 central handler class, using for response client/api requests,
    validate parameters whether is legal,  handling DB operations and
    calling rpc client's corresponding method to send messaging to agent
    endpoints
    """
    def __init__(self):
        self.db_api = db_api.get_instance()
        self.rpc_api = rpcapi.DNSManagerAPI.get_instance()

    @classmethod
    def get_instance(cls):

        global CENTRAL_MANAGER
        if not CENTRAL_MANAGER:
            CENTRAL_MANAGER = cls()
        return CENTRAL_MANAGER

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
        zone_str = json.dumps(zone)
        history = self._insert_operation_history(context, input=zone_str,
                                                 method='CREATE',
                                                 status='FAILED')
        # create the zone info in db
        db_zone_obj = self._create_in_storage(context, zone_obj)
        try:
            # handling create zone method in RPC
            response = self.rpc_api.create_zone(context, zone)
        except exception.Nca47Exception as e:
            LOG.error(_LE("Create corresponding response on device failed"))
            # DB rollback since create zone failed in Device
            zone_obj.delete(context, db_zone_obj['id'])
            # update operation history type with Failed in DB
            raise e
        self._update_operation_history(context, history.id, status='SUCCESS')
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

        zone_str = json.dumps(zone)
        history = self._insert_operation_history(context, input=zone_str,
                                                 method='UPDATE',
                                                 status='FAILED')
        # update the zone in db
        db_zone_obj = zone_obj.update(context, id, zone_obj.as_dict())
        try:
            # get the zone_id for device update
            zone_id = db_zone_obj['zone_id']
            # handling update zone method in RPC
            response = self.rpc_api.update_zone(context, zone, zone_id)

        except exception.Nca47Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            # DB rollback since update failed in Device, to re-update back
            zone_obj.update(context, id, org_db_zone_obj)
            raise e
        self._update_operation_history(context, history.id, status='SUCCESS')
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
        zone_str = json.dumps(zone)
        history = self._insert_operation_history(context, input=zone_str,
                                                 method='UPDATE',
                                                 status='FAILED')
        # update the zone in db
        db_zone_obj = zone_obj.update(context, id, zone_obj.as_dict())
        try:
            # get the zone_id for device update
            zone_id = db_zone_obj['zone_id']
            # handling update zone by owaners method in RPC
            response = self.rpc_api.update_zone_owners(context, zone, zone_id)
        except exception.Nca47Exception as e:
            LOG.error(_LE("Update corresponding response on device failed"))
            # DB rollback since update zone failed in Device
            zone_obj.update(context, id, org_db_zone_obj)
            # raise the exception for catch
            raise e
        self._update_operation_history(context, history.id, status='SUCCESS')
        return db_zone_obj

    def delete_zone(self, context, zone, id):
        """
        delete zone handling DB operations and  calling rpc client's
        corresponding method to send messaging to agent endpoints
        """
        org_db_zone_obj = self.get_zone_db_details(context, id)
        print org_db_zone_obj
        # init the DB operations object
        zone_obj = objects.DnsZone(context)
        zone_str = json.dumps(zone)
        history = self._insert_operation_history(context, input=zone_str,
                                                 method='DELETE',
                                                 status='FAILED')
        # delete the zone in db
        db_zone_obj = zone_obj.delete(context, id)
        try:
            zone_id = db_zone_obj['zone_id']
            # handling delete zone method in RPC
            response = self.rpc_api.delete_zone(context, zone, zone_id)
        except exception.Nca47Exception as e:
            LOG.error(_LE("Delete corresponding response on device failed"))
            # since delete failed in device, so re-update back object in DB
            zone_obj.update(context, id, org_db_zone_obj.as_dict())
            # raise the exception for catch
            raise e
        self._update_operation_history(context, history.id, status='FAILED')
        return db_zone_obj

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
        history = self._insert_operation_history(context, input='{}',
                                                 method='GET',
                                                 status='FAILED')
        target = None
        try:
            target = rrs_obj.get_objects(context, **rrs_dic)
        except db_exception as e:
            raise e
        self._update_operation_history(context, history.id, status='SUCCESS')
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
            raise exception.IsNotExistError(param_name="records with id="
                                            + record_id)
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
        # check zone if is not exsit
        target_zone = self.is_exist_zone(context, zone_id)
        # dev_zone_id is zone_id of device
        if target_zone is None:
            raise exception.IsNotExistError(param_name=zone_id)
        dev_zone_id = target_zone["zone_id"]
        LOG.info(_LI("the zone object with id=%(zone_id)s is existed"),
                 {"zone_id": zone_id})
        target_record = self.is_exist_zone_record(context, record)

        if target_record is not None:
            LOG.warning(_LW("the record object with name = %(record)s"
                        "already exists in DB"), {"record": record['name']})
            raise exception.HaveSameObject(object_name=record['name'])

        # return response from DB
        record_values = self._make_dns_record_object(record, zone_id)
        input_str = json.dumps(record)
        history = self._insert_operation_history(context,
                                                 input=input_str,
                                                 method='CREATE',
                                                 status='FAILED')
        record_obj = objects.DnsZoneRrs(context, **record_values)
        response = self._create_in_storage(context, record_obj)
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
        self._update_operation_history(context, history.id, status='SUCCESS')
        return response

    def update_record(self, context, record, zone_id, record_id):
        # zone is not exsit
        target_zone = self.is_exist_zone(context, zone_id)
        if target_zone is None:
            raise exception.IsNotExistError(param_name=zone_id)

        org_db_record_obj = self.get_record_from_db(context, record_id)
        dev_zone_id = target_zone["zone_id"]
        LOG.info(_LI("%(zone_id)s is existed"), {"zone_id": zone_id})
        # return response from DB
        response = self.update_rrs_info(context, record_id, record, None)
        input_str = json.dumps(record)
        history = self._insert_operation_history(context, input=input_str,
                                                 method='UPDATE',
                                                 status='FAILED')
        # dev_rrs_id is rrs_id of device
        dev_rrs_id = response["rrs_id"]
        try:
            # handling update zone record method in RPC
            # return response from Device
            self.rpc_api.update_record(context, record,
                                       dev_zone_id, dev_rrs_id)
        except Exception as e:
            LOG.error(_LE("Update response on device failed"))
            # DB rollback
            rrs_obj = objects.DnsZoneRrs(context)
            rrs_obj.update(context, record_id, org_db_record_obj)
            # raise the exception for catch
            raise e
        self._update_operation_history(context, history.id, status='SUCCESS')
        return response

    def delete_record(self, context, record, zone_id, record_id):
        # zone is not exsit
        target_zone = self.is_exist_zone(context, zone_id)

        org_db_record_obj = self.get_record_from_db(context, record_id)
        # dev_zone_id is zone_id of device
        if target_zone is None:
            raise exception.IsNotExistError(param_name=zone_id)
        dev_zone_id = target_zone["zone_id"]
        LOG.info(_LI("%(zone_id)s is existed"), {"zone_id": zone_id})
        input_str = json.dumps(record)
        history = self._insert_operation_history(context, input=input_str,
                                                 method='DELETE',
                                                 status='FAILED')
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
        self._update_operation_history(context, history.id, status='SUCCESS')
        return response_dev

    # The following is a method that cleaning the cache !
    def del_cache(self, context, domain):
        """Clear DNS cache"""
        # init the colnum with time and zone_str
        zone_str = json.dumps(domain)
        # insert operation history type with Creating in DB
        history = self._insert_operation_history(context, input=zone_str,
                                                 method='UPDATE',
                                                 status='FAILED')
        try:
            # delete the dns cache
            response = self.rpc_api.del_cache(context, domain)
        except exception.Nca47Exception as e:
            LOG.error(_LE("Clear Cache response on device failed"))
            # raise the exception for catch
            raise e
        # update operation history type with Success in DB
        self._update_operation_history(context, history.id, status='SUCCESS')
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
        target_values['operation_fro'] = 'AUTO'
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
        target_values['operation_fro'] = 'AUTO'
        return target_values

    def _insert_operation_history(self, context, **kwargs):

        current_time = timeutils.utcnow()
        opt_params = {}
        opt_params['config_id'] = 'da7f10eb-2d02-4f0c-8edd-839a3f5b8731'
        opt_params['input'] = kwargs['input']
        opt_params['operation_type'] = kwargs['method']
        opt_params['operation_time'] = current_time
        opt_params['operation_status'] = kwargs['status']
        opt_obj = objects.OperationHistory(context, **opt_params)
        LOG.info(_LI("Inserting operation history record in DB"))
        operation_history = self._create_in_storage(context, opt_obj)
        LOG.info(_LI("Insert operation history record in DB successful"))
        return operation_history

    def _update_operation_history(self, context, id, **kwargs):
        opt_params = {}
        opt_params['operation_status'] = kwargs['status']
        opt_obj = objects.OperationHistory(context, **opt_params)
        LOG.info(_LI("updating operation history record in DB"))
        opt_obj.update(context, id, opt_obj.as_dict())
        LOG.info(_LI("update operation history record in DB successful!"))
        return None

    def is_exist_zone_record(self, context, dic):
        rrs_dic = {}
        rrs_dic['rrs_name'] = dic["name"]
        rrs_dic['type'] = dic["type"]
        rrs_dic['ttl'] = dic["ttl"]
        rrs_dic['deleted'] = False
        rrs_obj = objects.DnsZoneRrs(context, **rrs_dic)
        target = None
        try:
            target = rrs_obj.get_object(context, **rrs_dic)
        except db_exception:
            LOG.error(_LE("is_exist_zone_record method operation failed!"))
            raise db_exception
        return target

    def is_exist_zone(self, context, zone_id):
        zone_name_dic = {}
        zone_name_dic['id'] = zone_id
        zone_name_dic['deleted'] = False
        zone_obj = objects.DnsZone(context, **zone_name_dic)
        target_zone = None
        try:
            target_zone = zone_obj.get_object(context, **zone_name_dic)
        except db_exception:
            LOG.error(_LE("is_exist_zone method operation failed!"))
            raise db_exception
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

    def delete_rrs_info(self, context, record_id):
        rrs_obj = objects.DnsZoneRrs(context)
        record = None
        try:
            record = rrs_obj.delete(context, record_id)
        except db_exception:
            LOG.error(_LE("delete_rrs_info method operation failed!"))
            raise db_exception
        return record

