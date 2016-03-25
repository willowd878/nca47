import netaddr
from nca47.common.exception import ParamNull
from nca47.common.exception import NonExistParam
from nca47.common.exception import ParamValueError
from nca47.common.exception import ParamFormatError

from netaddr.core import INET_PTON


def check_renewal(renewal):
    """check into the auxiliary area is not expired"""
    if renewal == "yes" or renewal == "no":
        return True
    return False


def check_areaname(name):
    """check into the area name"""
    try:
        spe_char = '.'
        char = name[-1]
        if cmp(spe_char, char):
            return False
        return True
    except Exception:
        return False


def check_current_user(current_user):
    """check into the current_user"""
    if (current_user == "admin"):
        return True
    return False


def check_ttl(ttl):
    """ttl less than 3600"""
    try:
        ttl = int(ttl)
        if ttl > 0 and ttl <= 3600:
            return True
        else:
            return False
    except Exception:
        return False


def check_rdata(rdata):
    """Validation rdata, example:196.168.51.96"""
    try:
        if netaddr.valid_ipv4(rdata, INET_PTON):
            return True
        else:
            return False
    except Exception:
        return False


def is_not_nil(string):
    '''string is not null'''
    string = string.strip()
    try:
        if len(string) > 0:
            return True
        else:
            return False
    except Exception:
        return False


def validat_values(values, valid_keys):
    """Non null input parameters"""
    recom_msg = {}
    for key in valid_keys:
        if key not in values.keys():
            raise NonExistParam(param_name=key)
        else:
            recom_msg[key] = values[key]
        if values[key] is None:
            raise ParamNull(param_name=key)
    return recom_msg


def ret_info(ret_code, ret_msg):
    dic = {"ret_code": ret_code, "ret_msg": ret_msg}
    return dic


def validat_parms(values, valid_keys):
    """check the in value is null and nums"""
    recom_msg = validat_values(values, valid_keys)
    for value in recom_msg:
        if value == "name":
            if not check_areaname(values['name']):
                raise ParamFormatError(param_name=value)
        elif value == "default_ttl":
            if not check_ttl(values['default_ttl']):
                raise ParamFormatError(param_name=value)
        elif value == "renewal":
            if not check_renewal(values['renewal']):
                raise ParamValueError(param_name=value)
        elif value == "current_user":
            if not check_current_user(values['current_user']):
                raise ParamValueError(param_name=value)
        elif value == "owners":
            if not is_not_nil(values['owners']):
                raise ParamNull(param_name=value)
        elif value == "type":
            if not is_not_nil(values['type']):
                raise ParamNull(param_name=value)
        elif value == "ttl":
            if not check_ttl(values['ttl']):
                raise ParamFormatError(param_name=value)
        elif value == "rdata":
            if not check_rdata(values['rdata']):
                raise ParamNull(param_name=value)
        elif value == "domain_name":
            if not is_not_nil(values['domain_name']):
                raise ParamNull(param_name=value)
        elif value == "view_name":
            if not is_not_nil(values['view_name']):
                raise ParamNull(param_name=value)
        elif value == "zone_content":
            if not is_not_nil(values['zone_content']):
                raise ParamNull(param_name=value)
        elif value == "slaves":
            if not is_not_nil(values['slaves']):
                raise ParamNull(param_name=value)
    return recom_msg
