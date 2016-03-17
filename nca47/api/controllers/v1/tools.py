from oslo_serialization import jsonutils as json
import netaddr
import re
from nca47.common.exception import checkParam
from netaddr.core import INET_PTON


def areaname_check(name):
    """check into the area name"""
    spe_char = '.'
    char = name[-1]
    if cmp(spe_char, char):
        return False
    return True


def renewal_check(renewal):
    """check into the auxiliary area is not expired"""
    if ((renewal == "yes") | (renewal == "no")):
        return True
    return False


def current_user_check(current_user):
    """check into the current_user"""
    if (current_user == "admin"):
        return True
    return False


def validat_renewal(values):
    if values['renewal'] == "no":
        for value in values:
            if value == "slaves" or value == "zone_content":
                checkParam._msg_fmt = "The renewal value is NO, "
                "Do not put slaves or zone_content"
                raise checkParam


def validat_values(values, valid_keys):
    k = 0
    for value in values:
        for key in valid_keys:
            if key == value:
                k += 1
                if key != "default_ttl":
                    if len(values[key]) == 0:
                        checkParam._msg_fmt = 'the ' + key + ' is null'
                        raise checkParam
    if len(valid_keys) != k:
        checkParam._msg_fmt = 'Wrong number of parameters'
        raise checkParam


def load_values(req, valid_keys):
    """Load valid attributes from request"""
    result = {}
    try:
        values = json.loads(req.body)
    except Exception:
        checkParam._msg_fmt = 'Input format is incorrect'
        raise checkParam
    """check the in value is null and nums"""
    validat_values(values, valid_keys)
    for value in values:
        if value == "name":
            if not areaname_check(values['name']):
                checkParam._msg_fmt = 'end of the name excepted the . '
                raise checkParam
        elif value == "default_ttl":
            if not is_ttl_valit(values['default_ttl']):
                checkParam._msg_fmt = 'ttl is illegal'
                raise checkParam
        elif value == "renewal":
            if not renewal_check(values['renewal']):
                checkParam._msg_fmt = 'Input items are neither yes nor no'
                raise checkParam
        elif value == "current_user":
            if not current_user_check(values['current_user']):
                checkParam._msg_fmt = 'the current user is not admin'
                raise checkParam
        elif value == "owners":
            if not is_notnull_owners(values['owners']):
                checkParam._msg_fmt = 'the owners is null'
                raise checkParam
        result[value] = values[value]
    return result


def return_dic(json_str):
        dic = json.loads(json_str)
        return dic


def is_name_valit(name):
    """regular expression : Validation Domain name"""
    if re.match(r'^(www\.)?[\w-]+\.\w+[.]$', name, re.M | re.I):
        return True
    else:
        return False


def is_type_valit(_type):
    """regular expression : Validation type ,example:A or AAAA"""
    if re.match(r'^([A]{1}|[A]{4})$', _type):
        return True
    else:
        return False


def is_klass_valit(klass):
    """regular expression : Validation klass ,example:IN"""
    if re.match(r'^([I][N])$', klass):
        return True
    else:
        return False


def is_ttl_valit(ttl):
    """ttl less than 3600"""
    try:
        ttl = int(ttl)
    except Exception:
        return False
    if ttl > 0 and ttl <= 3600:
        return True
    else:
        return False


def is_rdata_valit(rdata):
    """regular expression : Validation rdata ,example:196.168.51.96"""
    if netaddr.valid_ipv4(rdata, INET_PTON):
        return True
    else:
        return False


def is_notnull_view_id(view_id):
    if view_id.strip():
        return True
    else:
        return False


def is_notnull_zone_id(zone_id):
    if zone_id.strip():
        return True
    else:
        return False


def is_notnull_rrs_id(rrs_id):
    if rrs_id.strip():
        return True
    else:
        return False


def is_notnull_current_user(current_user):
    if current_user.strip():
        return True
    else:
        return False


def validation_create_authority_records(json_str):
    """you must validation when you create authority records"""
    dic = return_dic(json_str)
    list_ = ['name', 'type', 'ttl', 'rdata', 'current_user']
    validat_values(dic, list_)
    name = dic['name']
    _type = dic['type']
    ttl = dic['ttl']
    rdata = dic['rdata']
    current_user = dic['current_user']
    if not is_name_valit(name):
        checkParam._msg_fmt = 'domain name is illegal!'
        raise checkParam
    elif not is_type_valit(_type):
        checkParam._msg_fmt = 'resource record types are illegal!'
        raise checkParam
    elif not is_ttl_valit(ttl):
        checkParam._msg_fmt = 'ttl is illegal!'
        raise checkParam
    elif not is_rdata_valit(rdata):
        checkParam._msg_fmt = 'rdata:record data resources is illegal!'
        raise checkParam
    elif not current_user_check(current_user):
        checkParam._msg_fmt = 'current_user:current_user is illegal!'
        raise checkParam
    else:
        return dic


def validation_remove_authority_records(json_str):
    """you must validation when you delete authority records"""
    dic = return_dic(json_str)
    list_ = ['current_user']
    validat_values(dic, list_)
    current_user = dic['current_user']
    if not current_user_check(current_user):
        checkParam._msg_fmt = 'current_user is illegal!'
        raise checkParam
    else:
        return dic


def validation_update_authority_records(json_str):
    """ you must validation when you update authority records """
    dic = return_dic(json_str)
    list_ = ['ttl', 'rdata', 'current_user']
    validat_values(dic, list_)
    current_user = dic['current_user']
    ttl = dic['ttl']
    rdata = dic['rdata']
    if not current_user_check(current_user):
        checkParam._msg_fmt = 'current_user is illegal!'
        raise checkParam
    elif not is_ttl_valit(ttl):
        checkParam._msg_fmt = 'ttl is illegal!'
        raise checkParam
    elif not is_rdata_valit(rdata):
        checkParam._msg_fmt = 'rdatais illegal!'
        raise checkParam
    else:
        return dic


def validation_show_authority_records(args):
    return args


def ret_info(ret_code, ret_msg):
    dic = {"ret_code": ret_code, "ret_msg": ret_msg}
    return dic


def valit_del_cache(json_str):
    dic = return_dic(json_str)
    list_ = ['owners', 'domain_name', 'view_name', 'current_user']
    validat_values(dic, list_)
    owners = dic["owners"]
    domain_name = dic["domain_name"]
    view_name = dic["view_name"]
    current_user = dic["current_user"]
    if not is_notnull_owners(owners):
        checkParam._msg_fmt = 'owners is None!'
        raise checkParam
    elif not is_notnull_domain_name(domain_name):
        checkParam._msg_fmt = 'domain_name is None!'
        raise checkParam
    elif not is_notnull_view_name(view_name):
        checkParam._msg_fmt = 'view_name is None!'
        raise checkParam
    elif not current_user_check(current_user):
        checkParam._msg_fmt = 'current_user is illegal!'
        raise checkParam
    else:
        return dic


def is_notnull_owners(owners):
    if len(owners) > 0:
        return True
    else:
        return False


def is_notnull_domain_name(domain_name):
    if domain_name.strip():
        return True
    else:
        return False


def is_notnull_view_name(view_name):
    if view_name.strip():
        return True
    else:
        return False
