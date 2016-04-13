import sqlalchemy as sa
from oslo_db.sqlalchemy import types as db_types
from nca47.db.sqlalchemy.models import base as model_base
from nca47.objects import attributes as attr


HasTenant = model_base.HasTenant
HasId = model_base.HasId
HasStatus = model_base.HasStatus
HasOperationMode = model_base.HasOperationMode


class VFW(model_base.BASE, HasId, HasOperationMode):

    """Represents a virtual firewall system server."""

    __tablename__ = 'fw_vfw_info'

    vfw_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_type = sa.Column(sa.String(attr.STATUS_LEN))
    vfw_info = sa.Column(db_types.JsonEncodedList)
    dc_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    network_zone_name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    network_zone_class = sa.Column(sa.String(attr.NAME_MAX_LEN))
    protection_class = sa.Column(sa.String(attr.STATUS_LEN))
    vres_id = sa.Column(sa.String(attr.UUID_LEN))


class Dnat(model_base.BASE, HasId, HasOperationMode):

    """Represents an DNAT."""

    __tablename__ = 'fw_dnat_info'

    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    inifname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    wanip = sa.Column(sa.String(attr.IP_LEN))
    wantcpports = sa.Column(db_types.JsonEncodedList)
    wanudpports = sa.Column(db_types.JsonEncodedList)
    lanipstart = sa.Column(sa.String(attr.IP_LEN))
    lanipend = sa.Column(sa.String(attr.IP_LEN))
    lanport = sa.Column(sa.String(attr.UUID_LEN))
    slot = sa.Column(sa.String(attr.STATUS_LEN))
    vfwname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))


class PacketFilter(model_base.BASE, HasId, HasOperationMode):

    """Represents an firewall packet filter."""

    __tablename__ = 'fw_packetfilter_info'

    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    srczonename = sa.Column(sa.String(attr.NAME_MAX_LEN))
    dstzonename = sa.Column(sa.String(attr.NAME_MAX_LEN))
    srcipobjnames = sa.Column(db_types.JsonEncodedList)
    dstipobjnames = sa.Column(db_types.JsonEncodedList)
    servicenames = sa.Column(db_types.JsonEncodedList)
    action = sa.Column(sa.String(attr.STATUS_LEN))
    vfwname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))


class VLAN(model_base.BASE, HasId, HasOperationMode):

    """Represents a firewall vlan interface."""

    __tablename__ = 'fw_vlan_info'

    vlan_id = sa.Column(sa.String(attr.UUID_LEN))
    ipaddr = sa.Column(sa.String(attr.INPUT_MAX_LEN))
    ifnames = sa.Column(db_types.JsonEncodedList)
    vres_id = sa.Column(sa.String(attr.UUID_LEN))


class ADDROBJ(model_base.BASE, HasId, HasOperationMode):

    """Represents a firewall addrobj interface."""

    __tablename__ = 'fw_addrobj_info'

    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    ip = sa.Column(sa.String(attr.IP_LEN))
    expip = sa.Column(sa.String(attr.IP_LEN))
    vfwname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))
    operation_fro = sa.Column(sa.String(attr.UUID_LEN))


class FwSnatAddrPool(model_base.BASE, HasId, HasOperationMode):

    """Represents a firewall snataddrpool interface."""

    __tablename__ = 'fw_snataddrpool_info'

    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    ipstart = sa.Column(sa.String(attr.IP_LEN))
    ipend = sa.Column(sa.String(attr.IP_LEN))
    slotip = sa.Column(sa.String(attr.STATUS_LEN))
    vfwname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))
    operation_fro = sa.Column(sa.String(attr.UUID_LEN))


class NetService(model_base.BASE, HasId, HasOperationMode):

    """Represents a firewall NetService interface."""

    __tablename__ = 'fw_netservices_info'

    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    proto = sa.Column(sa.String(attr.NAME_MAX_LEN))
    port = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfwname = sa.Column(sa.String(attr.UUID_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))


class FW_SecurityZone(model_base.BASE, HasId):
    """Represents a FW_SecurityZone."""
    __tablename__ = 'fw_security_zone_info'
    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    ifnames = sa.Column(db_types.JsonEncodedList)
    priority = sa.Column(sa.String(attr.TTL_LEN))
    vfwname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))
    operation_fro = sa.Column(sa.String(attr.UUID_LEN))


class FW_Staticnat(model_base.BASE, HasId):
    """Represents a FW_Staticnat."""
    __tablename__ = 'fw_staticnat_info'
    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    ifname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    lanip = sa.Column(sa.String(attr.IP_LEN))
    wanip = sa.Column(sa.String(attr.IP_LEN))
    slot = sa.Column(sa.String(attr.STATUS_LEN))
    vfwname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))
    operation_fro = sa.Column(sa.String(attr.UUID_LEN))


class FW_vrf(model_base.BASE, HasId):
    """Represents a FW_vrf."""
    __tablename__ = 'fw_vrf_info'
    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vrfInterface = sa.Column(db_types.JsonEncodedList)
    vfwname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))
    vres_id = sa.Column(sa.String(attr.UUID_LEN))
    operation_fro = sa.Column(sa.String(attr.UUID_LEN))


class FW_snat(model_base.BASE, HasId):
    """Represents a FW_vrf."""
    __tablename__ = 'fw_snat_info'
    name = sa.Column(sa.String(attr.NAME_MAX_LEN))
    outifname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    srcipobjname = sa.Column(db_types.JsonEncodedList)
    dstipobjname = sa.Column(db_types.JsonEncodedList)
    wanippoolname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfwname = sa.Column(sa.String(attr.NAME_MAX_LEN))
    vfw_id = sa.Column(sa.String(attr.UUID_LEN))
    operation_fro = sa.Column(sa.String(attr.UUID_LEN))
