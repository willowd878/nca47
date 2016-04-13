import netaddr
import re
from netaddr.core import INET_PTON

from nca47.common.exception import ParamNull
from nca47.common.exception import NonExistParam
from nca47.common.exception import ParamValueError
from nca47.common.exception import ParamFormatError


def check_renewal(renewal):
    """check into the auxiliary area is not expired"""
    if renewal == "yes" or renewal == "no":
        return True
    return False


def check_areaname(name):
    """check into the area name"""
    if re.match(r'^(?=^.{3,255}$)(http(s)?:\/\/)?(www\.)?[a-zA-Z0-9]'
                '[-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+'
                '(:\d+)*(\/\w+\.\w+)*$',
                name, re.M | re.I):
        return True
    else:
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


def is_not_list(value):
    """To determine whether the array is not empty"""
    flag = "0"
    if isinstance(value, list):
        if not value:
            flag = "1"
            return flag
        return True
    else:
        return flag


def validat_values(values, valid_keys):
    """Non null input parameters"""
    recom_msg = {}
    for key in valid_keys:
        if key not in values.keys():
            raise NonExistParam(param_name=key)
        else:
            """check into the area name"""
            if key == 'name':
                try:
                    spe_char = '.'
                    char = values[key][-1]
                    if not cmp(spe_char, char):
                        values[key] = values[key][:-1]
                except Exception:
                    raise ParamFormatError(param_name=key)
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
        elif value == "tenant_id":
            if not is_not_nil(values['tenant_id']):
                raise ParamNull(param_name=value)
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
            flag = is_not_list(values['owners'])
            if flag == "0":
                raise ParamFormatError(param_name=value)
            elif flag == "1":
                raise ParamNull(param_name=value)
        elif value == "slaves":
            flag = is_not_list(values['slaves'])
            if flag == "0":
                raise ParamFormatError(param_name=value)
            elif flag == "1":
                raise ParamNull(param_name=value)
        elif value == "type":
            if not is_not_nil(values['type']):
                raise ParamFormatError(param_name=value)
        elif value == "ttl":
            if not check_ttl(values['ttl']):
                raise ParamFormatError(param_name=value)
        elif value == "rdata":
            if not check_rdata(values['rdata']):
                raise ParamFormatError(param_name=value)
        elif value == "domain_name":
            if not is_not_nil(values['domain_name']):
                raise ParamNull(param_name=value)
        elif value == "view_name":
            if not is_not_nil(values['view_name']):
                raise ParamNull(param_name=value)
        elif value == "zone_content":
            if not is_not_nil(values['zone_content']):
                raise ParamNull(param_name=value)
    return recom_msg


def dict_merge(merge_dict, add_dict):
    ''' Note: the same key will be overwritten '''
    return dict(merge_dict, **add_dict)


def message_regrouping(dic, list_imp, list_uni):
    validat_values(dic, list_imp)
    values = {}
    dic_key = dic.keys()
    for key_imp in list_imp:
        values[key_imp] = dic[key_imp]

    uni = {}
    for k in list_uni:
        if k not in dic_key:
            if k == "ttl":
                uni[k] = "3600"
            elif k == "klass":
                uni[k] = "IN"
            elif k == "current_user":
                uni[k] = "admin"
            else:
                continue

    merge = dict_merge(values, uni)

    exist_imp = {}
    for key in dic_key:
        if key == "ttl":
            if is_not_nil(dic[key]):
                exist_imp[key] = dic[key]
            else:
                exist_imp[key] = "3600"
        elif key == "current_user":
            if is_not_nil(dic[key]):
                exist_imp[key] = dic[key]
            else:
                exist_imp[key] = "admin"

        elif key == "klass":
            if is_not_nil(dic[key]):
                exist_imp[key] = dic[key]
            else:
                exist_imp[key] = "IN"
        else:
            continue
    new_list = list_imp + list_uni
    new_dic = dict_merge(merge, exist_imp)
    return validat_parms(new_dic, new_list)


def get_complementary_set(remote_dic, local_dic):
    """
    Get complementary set. for example:
    t = ['1','2','3'] and s = ['1','2','3','4'], you can get ['4']
    note: t is subset of s
    """
    if is_subset(remote_dic, local_dic):
        val_ifnames = list(set(local_dic).difference(set(remote_dic)))
        return val_ifnames
    else:
        return None


def is_subset(remote_dic, local_dic):
    """remote_dic is or not subset of local_dic"""
    return set(remote_dic).issubset(set(local_dic))


def _is_valid_port_range(port_range):
    """
    Use to judge port range pattern if valid, the pattern must like 8080-8080
    and the first port value must greater than the second port value, also the
    port value must be in line with port valid pattern
    """
    bool_value = True
    reg = r'^([0-9]{1,5}[-][0-9]{1,5})$'
    match_obj = re.match(reg, port_range)
    if match_obj is None:
        bool_value = False
    port_list = match_obj.group(0).split('-')
    port1 = int(port_list[0])
    port2 = int(port_list[1])
    if port1 > 65535 or port2 > 65535:
        bool_value = False
    else:
        if port1 > port2:
            bool_value = False
    return bool_value


def _is_valid_port(port):
    """Use to judge the port whether is valid port value"""
    bool_value = True
    regex = "^([1-9]|[1-9]\\d{1,3}|[1-6][0-5][0-5][0-3][0-5])$"
    match_obj = re.match(regex, port)
    if match_obj is None:
        bool_value = False
    return bool_value


def _is_valid_ipv4_addr(ipaddr):
    """Use to judge the ip address if is valid IPv4 address"""
    if netaddr.valid_ipv4(ipaddr, INET_PTON):
        return True
    else:
        return False


def clean_end_str(end_str, source_str):
    """Remove the specified at the end of the string"""
    tem1 = end_str[::-1]
    tem2 = source_str[::-1]
    return tem2[len(tem1):len(tem2)][::-1]


def filter_string_not_null(dic, list_):
    """fliter String is or not null ,and get required field"""
    dic_key = dic.keys()
    value = {}
    for key in dic_key:
        if key in list_:
            val = dic[key]
            if isinstance(val, list):
                pass
            elif not is_not_nil(val):
                raise ParamNull(param_name=key)
            value[key] = val
    return value


def firewall_params(dic, list_):
    dic = filter_string_not_null(dic, list_)
    dic_key = dic.keys()
    for key in dic_key:
        val_key = dic[key]
        if key == "ifnames":
            flag = is_not_list(val_key)
            if flag == "0":
                raise ParamFormatError(param_name=key)
            elif flag == "1":
                raise ParamNull(param_name=key)
        elif key == "proto":
            try:
                val_int = int(val_key)
                if val_int < 0 or val_int > 255:
                    raise ParamFormatError(param_name=key)
            except Exception:
                raise ParamFormatError(param_name=key)
        elif key == "port":
            if not _is_valid_port_range(val_key):
                raise ParamFormatError(param_name=key)
        else:
            continue
    return dic


def _is_valid_slotip(slotip):
    slotip_list = [0, 5, 23]
    if slotip in slotip_list:
        return True
    else:
        return False
