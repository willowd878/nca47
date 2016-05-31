import netaddr
import re
from netaddr.core import INET_PTON

from nca47.common.exception import ParamNull
from nca47.common.exception import NonExistParam
from nca47.common.exception import checkParam


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


def is_no_empty_list(value):
    """
    Use to check the value type if is list and not empty
    if value is no empty list then return True, else return False
    """
    if isinstance(value, list) and value:
        return True
    else:
        return False


def validat_values(values, valid_keys):
    """Non null input parameters"""
    recom_msg = {}
    for key in valid_keys:
        if key not in values.keys():
            raise NonExistParam(param_name=key)
        else:
            if isinstance(values[key], basestring):
                if (values[key].isspace()) or (len(values[key]) == 0):
                    raise ParamNull(param_name=key)
            elif isinstance(values[key], list):
                if len(values[key]) == 0:
                    raise ParamNull(param_name=key)
            recom_msg[key] = values[key]
    return recom_msg


def validat_update_values(values, valid_keys):
    recom_msg = {}
    for key in values.keys():
        if key not in valid_keys:
            raise checkParam(param_name=key)
        else:
            if isinstance(values[key], basestring):
                if values[key].isspace():
                    raise ParamNull(param_name=key)
            elif isinstance(values[key], list):
                if len(values[key]) == 0:
                    raise ParamNull(param_name=key)
            recom_msg[key] = values[key]
    return recom_msg


def ret_info(ret_code, ret_msg):
    dic = {"ret_code": ret_code, "ret_msg": ret_msg}
    return dic


def dict_merge(merge_dict, add_dict):
    ''' Note: the same key will be overwritten '''
    return dict(merge_dict, **add_dict)


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


def _is_valid_ipv4_mask(mask):
    try:
        if int(mask) <= 32 and int(mask) >= 1:
            return True
        else:
            return False
    except:
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
    for key in list_:
        if key not in dic_key:
            raise NonExistParam(param_name=key)
        val = dic[key]
        if isinstance(val, list):
            pass
        elif not is_not_nil(val):
            raise ParamNull(param_name=key)
        value[key] = val
    return value


def _is_valid_slotip(slotip):
    slotip_list = ['0', '5', '23']
    slotip = str(slotip)
    if slotip in slotip_list:
        return True
    else:
        return False


def is_or_not_list(value):
    """To determine whether the array is not empty"""
    flag = "0"
    if isinstance(value, list):
        if value:
            for v in value:
                if not is_not_nil(v):
                    flag = "1"
                    return flag
            return True
        else:
            flag = "1"
            return flag
    else:
        return flag


def is_list_and_no_emtpy_string(values):
    if not isinstance(values, list):
        return False
    for value in values:
        if not is_not_nil(value):
            return False
    return True


def is_proto_range(proto):
    """protocol range is 0-255"""
    try:
        val_int = int(proto)
        if val_int < 0 or val_int > 255:
            return False
    except Exception:
        return False
    return True


def input_dic(keys, dic):
    """Fill the data in the dictionary"""
    obj_dic = {}
    for key in keys:
        if key not in dic.keys():
            pass
        else:
            obj_dic[key] = dic[key]
    return obj_dic


def joinString(dic):
    str_n = ""
    ind = 0
    for key in dic:
        if ind == 0:
            str_n = dic[0]
        else:
            str_n = str_n + "," + key
        ind = ind + 1
    return str_n


def get_obj_list(keys, values):
    obj_list = []
    for value in values:
        obj_dic = {}
        for column in xrange(len(keys)):
            obj_dic[keys[column]] = value[column]
        obj_list.append(obj_dic)
    return obj_list


def get_obj_input_str(str_dict):
    str_list = list(str_dict.keys())
    str_list.append('operation_for')
    str_list.append('deleted_at')
    str_list.append('deleted')
    input_str = ','.join(str_list)
    return input_str


def classfiy_sql_keys(values, lik_list, search_list):
    lik_ret = dict()
    search_ret = dict()
    for key in values.keys():
        if len(values[key].strip()) > 0:
            if key in lik_list:
                lik_ret[key] = values[key]
            elif key in search_list:
                search_ret[key] = values[key]
    return lik_ret, search_ret


def get_sql_str(table_name):
    # Get sql header ,like select * from table_name where 1=1
    return "select * from %s where 1=1 " % table_name


def is_valid_ip_with_netmask(ip):
    if len(ip.split('/')) == 2:
        a = ip.split('/')
        if _is_valid_ipv4_addr(a[0]) and _is_valid_ipv4_mask(a[1]):
            return True
        else:
            return False
    else:
        if _is_valid_ipv4_addr(ip):
            return True
        else:
            return False


def is_valid_ip_list_with_netmask(ip_list):
    if isinstance(ip_list, list):
        for ip in ip_list:
            if len(ip.split('/')) == 2:
                ip_ = ip.split('/')
                if not (
                    _is_valid_ipv4_addr(
                        ip_[0]) and _is_valid_ipv4_mask(
                        ip_[1])):
                    return False
    else:
        return True


def filter_specific_values(dic, specific_values_keys):
    """specific values can not null"""
    for key in specific_values_keys:
        if key not in dic.keys():
            raise NonExistParam(param_name=key)
        else:
            continue
    return dic
