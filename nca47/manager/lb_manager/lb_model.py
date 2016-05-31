realservername = ""
rip = ""
groupname = ""
virtualservername = ""
virtualname = ""
vip = ""
vport = ""
rport = ""
pbindtype = ""
dbindtype = ""
ptmouttime = ""
metrictype = ""


def get_realserver(**dic):
    real_list = []
    realservername = dic['realservername']
    rip = dic['rip']
    real_list.append("/c/slb/real "+realservername)
    real_list.append("ena")
    real_list.append("ipver v4")
    real_list.append("rip "+rip)
    # realserver = "/c/slb/real "+realservername+"/ena/ipver v4/rip "+rip
    return real_list


def get_group(**dic):
    group_list = []
    realservername = dic['realservername']
    metrictype = dic['metrictype']
    groupname = dic['groupname']
    group_list.append("/c/slb/group "+groupname)
    group_list.append("ipver v4")
    for key in realservername:
        group_list.append("add "+key)
    if metrictype is not None and metrictype is not"":
        group_list.append("metric "+metrictype)
    group_list.append("health tcp")
    # group = ("/c/slb/group " + groupname + "/ipver v4/add " +
    # realservername + "/health tcp")
    return group_list


def get_vip(**dic):
    vip_list = []
    virtualservername = dic['virtualservername']
    vip = dic['vip']
    virtualname = dic['virtualname']
    vip_list.append("/c/slb/virt "+virtualservername)
    vip_list.append("ena")
    vip_list.append("ipver v4")
    vip_list.append("vip "+vip)
    vip_list.append("vname "+virtualname)
    # v_ip = ("/c/slb/virt " + virtualservername + "/ena/ipver v4/vip " +
    # vip +"/vname " + virtualname)"""
    return vip_list


def get_service(**dic):
    service_list = []
    protocol = dic["protocol"]
    virtualservername = dic['virtualservername']
    groupname = dic['groupname']
    rport = dic['rport']
    vport = dic['vport']
    pbindtype = dic['pbindtype']
    dbindtype = dic['dbindtype']
    ptmouttime = dic['ptmouttime']
    service_list.append("/c/slb/virt " + virtualservername + "/service " +
                        vport + " " + protocol)
    service_list.append("group "+groupname)
    service_list.append("rport "+rport)
    if pbindtype is not None and pbindtype is not"":
        service_list.append("pbind "+pbindtype)
    if dbindtype is not None and dbindtype is not"":
        service_list.append("dbind "+dbindtype)
    if ptmouttime is not None and ptmouttime is not"":
        service_list.append("ptmout "+ptmouttime)
    # service_ = ("/c/slb/virt " + virtualservername + "/service " + vport +
    #            " http/group " + groupname + "/rport " + rport + "/pbind " +
    #            pbindtype + "/dbind " + dbindtype + "/ptmout " + ptmouttime +
    #            "/metric " + metrictype)"""
    return service_list


def delete_realserver(real_name):
    del_real_ser_list = []
    del_real_ser_list.append("/c/slb/real "+real_name)
    del_real_ser_list.append("del")
    return del_real_ser_list


def delete_group_realser(**dic):
    del_group_realser_list = []
    groupname = dic["groupname"]
    realservername = dic["realservername"]
    del_group_realser_list.append("/c/slb/group "+groupname)
    del_group_realser_list.append("rem "+realservername)
    return del_group_realser_list
