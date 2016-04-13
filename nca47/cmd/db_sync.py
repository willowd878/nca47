import sys
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement

from migrate.changeset.constraint import ForeignKeyConstraint
from oslo_log import log
from nca47.common import service as nca47_service
from nca47.common.i18n import _LE
from nca47.db import api as db_api
from nca47.objects import attributes as attr

sys.path.append('/vagrant/nca47')
LOG = log.getLogger(__name__)


class CreateView(Executable, ClauseElement):
    def __init__(self, name, select):
        self.name = name
        self.select = select


@compiles(CreateView)
def visit_create_view(element, compiler, **kw):
    return "CREATE VIEW %s AS %s" % (
         element.name,
         compiler.process(element.select, literal_binds=True)
         )


def main():
    nca47_service.prepare_service(sys.argv)
    engine = db_api.get_engine()
    meta = sa.MetaData()
    meta.bind = engine

    dns_servers = sa.Table('dns_servers', meta,
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.NAME_MAX_LEN), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    nca_agent_info = sa.Table('nca_agent_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('agent_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('agent_ip', sa.String(attr.IP_LEN), nullable=False),
        sa.Column('agent_nat_ip', sa.String(attr.IP_LEN), nullable=True),
        sa.Column('dc_name', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('network_zone', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('agent_type', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('availiable', sa.Boolean(), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True),
        sa.Column('operation_fro', sa.String(attr.NAME_MAX_LEN),
                  nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    nca_vres_info = sa.Table('nca_vres_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('vres_id', sa.String(attr.UUID_LEN), unique=True,
                  nullable=False),
        sa.Column('vres_name', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('tenant_id', sa.String(attr.TENANT_ID_MAX_LEN),
                  nullable=True),
        sa.Column('agent_id', sa.String(attr.UUID_LEN), nullable=True),
        sa.Column('operation_fro', sa.String(attr.NAME_MAX_LEN),
                  nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    nca_operation_history = sa.Table('nca_operation_history', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('config_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('input', sa.String(attr.INPUT_MAX_LEN), nullable=False),
        sa.Column('operation_type', sa.String(attr.NAME_MAX_LEN),
                  nullable=True),
        sa.Column('operation_time', sa.DateTime(), nullable=True),
        sa.Column('operation_status', sa.String(attr.NAME_MAX_LEN),
                  nullable=True),
        sa.Column('operation_fro', sa.String(attr.NAME_MAX_LEN),
                  nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    dns_zone_info = sa.Table('dns_zone_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('zone_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('tenant_id', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vres_id', sa.String(attr.UUID_LEN), nullable=True),
        sa.Column('zone_name', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('masters', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('slaves', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('default_ttl', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('ad_controller', sa.String(attr.NAME_MAX_LEN),
                  nullable=True),
        sa.Column('renewal', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('owners', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('comment', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('operation_fro', sa.String(attr.NAME_MAX_LEN),
                  nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    dns_rrs_info = sa.Table('dns_rrs_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('rrs_id', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('zone_id', sa.String(attr.UUID_LEN), nullable=True),
        sa.Column('rrs_name', sa.String(attr.NAME_MAX_LEN), nullable=False,
                  primary_key=True),
        sa.Column('type', sa.String(attr.TYPE_LEN), nullable=False,
                  primary_key=True),
        sa.Column('ttl', sa.String(attr.TTL_LEN), nullable=False),
        sa.Column('klass', sa.String(attr.TENANT_ID_MAX_LEN), nullable=True),
        sa.Column('rdata', sa.String(attr.TENANT_ID_MAX_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.NAME_MAX_LEN),
                  nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_vlan_info = sa.Table('fw_vlan_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('vlan_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('ipaddr', sa.String(attr.INPUT_MAX_LEN), nullable=False),
        sa.Column('ifnames', sa.String(attr.INPUT_MAX_LEN), nullable=False),
        sa.Column('vres_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_vrf_info = sa.Table('fw_vrf_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('vrfInterface', sa.String(attr.INPUT_MAX_LEN),
                  nullable=False),
        sa.Column('vfwname', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('vfw_id', sa.String(attr.UUID_LEN), nullable=True),
        sa.Column('vres_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_vfw_info = sa.Table('fw_vfw_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('vfw_name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vfw_type', sa.String(attr.STATUS_LEN), nullable=False),
        sa.Column('vfw_info', sa.String(attr.INPUT_MAX_LEN), nullable=False),
        sa.Column('dc_name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('network_zone_name',
                  sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('network_zone_class',
                  sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('protection_class',
                  sa.String(attr.STATUS_LEN), nullable=True),
        sa.Column('vres_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_security_zone_info = sa.Table('fw_security_zone_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('ifnames', sa.String(attr.INPUT_MAX_LEN), nullable=True),
        sa.Column('priority', sa.String(attr.TTL_LEN), nullable=False),
        sa.Column('vfwname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vfw_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_addrobj_info = sa.Table('fw_addrobj_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('ip', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('expip', sa.String(attr.UUID_LEN), nullable=True),
        sa.Column('vfwname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vfw_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_netservices_info = sa.Table('fw_netservices_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('proto', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('port', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('vfwname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vfw_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_snataddrpool_info = sa.Table('fw_snataddrpool_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('ipstart', sa.String(attr.IP_LEN), nullable=False),
        sa.Column('ipend', sa.String(attr.IP_LEN), nullable=False),
        sa.Column('slotip', sa.String(attr.STATUS_LEN), nullable=False),
        sa.Column('vfwname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vfw_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_snat_info = sa.Table('fw_snat_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('outifname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('srcipobjname', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('dstipobjname', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('wanippoolname',
                  sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('vfwname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vfw_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_dnat_info = sa.Table('fw_dnat_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('inifname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('wanip', sa.String(attr.IP_LEN), nullable=False),
        sa.Column('wantcpports', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('wanudpports', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('lanipstart', sa.String(attr.IP_LEN), nullable=False),
        sa.Column('lanipend', sa.String(attr.IP_LEN), nullable=False),
        sa.Column('lanport', sa.String(attr.TTL_LEN), nullable=False),
        sa.Column('slot', sa.String(attr.STATUS_LEN), nullable=False),
        sa.Column('vfwname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vfw_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro',
                  sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_packetfilter_info = sa.Table('fw_packetfilter_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('srczonename', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('dstzonename', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('srcipobjnames', sa.String(attr.NAME_MAX_LEN),
                  nullable=True),
        sa.Column('dstipobjnames', sa.String(attr.NAME_MAX_LEN),
                  nullable=True),
        sa.Column('servicenames', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('action', sa.String(attr.STATUS_LEN), nullable=True),
        sa.Column('log', sa.String(attr.STATUS_LEN), nullable=True),
        sa.Column('vfwname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vfw_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    fw_staticnat_info = sa.Table('fw_staticnat_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('name', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('ifname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('lanip', sa.String(attr.IP_LEN), nullable=False),
        sa.Column('wanip', sa.String(attr.IP_LEN), nullable=False),
        sa.Column('slot', sa.String(attr.STATUS_LEN), nullable=False),
        sa.Column('vfwname', sa.String(attr.NAME_MAX_LEN), nullable=False),
        sa.Column('vfw_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('operation_fro',
                  sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    tables = [dns_zone_info, nca_agent_info, nca_vres_info,
              nca_operation_history, dns_rrs_info, fw_vlan_info,
              fw_vfw_info, fw_security_zone_info, fw_addrobj_info,
              fw_netservices_info, fw_snataddrpool_info,
              fw_snat_info, fw_dnat_info, fw_packetfilter_info,
              fw_staticnat_info, fw_vrf_info]
    for table in tables:
        try:
            if not table.exists():
                table.create()
        except Exception:
            LOG.info(repr(table))
            LOG.exception(_LE('Exception while creating table.'))
            raise

    columns = [nca_vres_info.c.id.label('id'),
               nca_agent_info.c.id.label('agent_id'),
               nca_agent_info.c.agent_ip.label('agent_ip'),
               nca_agent_info.c.agent_nat_ip.label('agent_nat_ip'),
               nca_vres_info.c.id.label('vres_id'),
               nca_vres_info.c.tenant_id.label('tenant_id'),
               nca_agent_info.c.dc_name.label('dc_name'),
               nca_agent_info.c.network_zone.label('network_zone'),
               nca_vres_info.c.vres_name.label('vres_name'),
               nca_agent_info.c.agent_type.label('agent_type'),
               nca_agent_info.c.deleted_at.label('deleted_at'),
               nca_agent_info.c.deleted.label('deleted')]
    condition1 = (nca_agent_info.c.id == nca_vres_info.c.agent_id)
    condition2 = (nca_agent_info.c.availiable is True)
    condition3 = (nca_vres_info.c.deleted is False)
    vres_agent_view = CreateView('vres_agent_view',
                                 select(columns).where(condition1 and
                                                       condition2 and
                                                       condition3))
    engine.execute(vres_agent_view)

    vfw_trigger = sa.DDL('''\
                    CREATE TRIGGER cascadeDel_on_vfw AFTER UPDATE ON
                    fw_vfw_info FOR EACH ROW
                    BEGIN
                        UPDATE fw_dnat_info set deleted_at=now(), deleted=1
                            WHERE (vfw_id = old.id) and (old.deleted = 0) and
                            (new.deleted = 1);
                        UPDATE fw_staticnat_info set deleted_at=now(),
                            deleted=1 WHERE (vfw_id = old.id) and
                            (old.deleted = 0) and (new.deleted = 1);
                        UPDATE fw_snat_info set deleted_at=now(), deleted=1
                            WHERE (vfw_id = old.id) and (old.deleted = 0)
                            and (new.deleted = 1);
                        UPDATE fw_addrobj_info set deleted_at=now(), deleted=1
                            WHERE (vfw_id = old.id) and (old.deleted = 0) and
                            (new.deleted = 1);
                        UPDATE fw_snataddrpool_info set deleted_at=now(),
                            deleted=1 WHERE (vfw_id = old.id) and
                            (old.deleted = 0) and (new.deleted = 1);
                        UPDATE fw_netservices_info set deleted_at=now(),
                            deleted=1
                            WHERE (vfw_id = old.id) and (old.deleted = 0)
                            and (new.deleted = 1);
                        UPDATE fw_security_zone_info set deleted_at=now(),
                            deleted=1
                            WHERE (vfw_id = old.id) and (old.deleted = 0)
                            and (new.deleted = 1);
                        UPDATE fw_packetfilter_info set deleted_at=now(),
                            deleted=1 WHERE (vfw_id = old.id) and
                            (old.deleted = 0) and (new.deleted = 1);
                    END;''')
    engine.execute(vfw_trigger)

    nca_agent_info_table = sa.Table('nca_agent_info', meta, autoload=True)
    nca_vres_info_table = sa.Table('nca_vres_info', meta, autoload=True)
    nca_operation_history_table = sa.Table('nca_operation_history', meta,
                                           autoload=True)
    dns_zone_info_table = sa.Table('dns_zone_info', meta, autoload=True)
    dns_rrs_info_table = sa.Table('dns_rrs_info', meta, autoload=True)

    fw_vlan_info_table = sa.Table('fw_vlan_info', meta, autoload=True)
    fw_vfw_info_table = sa.Table('fw_vfw_info', meta, autoload=True)
    fw_security_zone_info_table = sa.Table('fw_security_zone_info',
                                           meta, autoload=True)
    fw_addrobj_info_table = sa.Table('fw_addrobj_info',
                                     meta, autoload=True)
    fw_netservices_info_table = sa.Table('fw_netservices_info',
                                         meta, autoload=True)
    fw_snataddrpool_info_table = sa.Table('fw_snataddrpool_info',
                                          meta, autoload=True)
    fw_snat_info_table = sa.Table('fw_snat_info', meta, autoload=True)
    fw_dnat_info_table = sa.Table('fw_dnat_info', meta, autoload=True)
    fw_packetfilter_info_table = sa.Table('fw_packetfilter_info',
                                          meta, autoload=True)
    fw_staticnat_info_table = sa.Table('fw_staticnat_info',
                                       meta, autoload=True)
    fw_vrf_info_table = sa.Table('fw_vrf_info',
                                 meta, autoload=True)

    nca_vres_info_agent_fk = ForeignKeyConstraint(
        [nca_vres_info_table.c.agent_id],
        [nca_agent_info_table.c.id])
    nca_vres_info_agent_fk.create()

    nca_operation_history_rrs_fk = ForeignKeyConstraint(
        [nca_operation_history_table.c.config_id],
        [nca_vres_info_table.c.id])
    nca_operation_history_rrs_fk.create()

    dns_zone_info_rrs_fk = ForeignKeyConstraint(
        [dns_rrs_info_table.c.zone_id],
        [dns_zone_info_table.c.id])
    dns_zone_info_rrs_fk.create()

    dns_zone_info_vres_fk = ForeignKeyConstraint(
        [dns_zone_info_table.c.vres_id],
        [nca_vres_info_table.c.vres_id])
    dns_zone_info_vres_fk.create()

    fw_vlan_info_fk = ForeignKeyConstraint(
        [fw_vlan_info_table.c.vres_id],
        [nca_vres_info_table.c.id])
    fw_vlan_info_fk.create()

    fw_vrf_info_fk = ForeignKeyConstraint(
        [fw_vrf_info_table.c.vres_id],
        [nca_vres_info_table.c.id])
    fw_vrf_info_fk.create()

    fw_vfw_info_fk = ForeignKeyConstraint(
        [fw_vfw_info_table.c.vres_id],
        [nca_vres_info_table.c.id])
    fw_vfw_info_fk.create()

    fw_security_zone_info_fk = ForeignKeyConstraint(
        [fw_security_zone_info_table.c.vfw_id],
        [fw_vfw_info_table.c.id])
    fw_security_zone_info_fk.create()

    fw_addrobj_info_fk = ForeignKeyConstraint(
        [fw_addrobj_info_table.c.vfw_id],
        [fw_vfw_info_table.c.id])
    fw_addrobj_info_fk.create()

    fw_netservices_info_fk = ForeignKeyConstraint(
        [fw_netservices_info_table.c.vfw_id],
        [fw_vfw_info_table.c.id])
    fw_netservices_info_fk.create()

    fw_snataddrpool_info_fk = ForeignKeyConstraint(
        [fw_snataddrpool_info_table.c.vfw_id],
        [fw_vfw_info_table.c.id])
    fw_snataddrpool_info_fk.create()

    fw_snat_info_fk = ForeignKeyConstraint(
        [fw_snat_info_table.c.vfw_id],
        [fw_vfw_info_table.c.id])
    fw_snat_info_fk.create()

    fw_dnat_info_fk = ForeignKeyConstraint(
        [fw_dnat_info_table.c.vfw_id],
        [fw_vfw_info_table.c.id])
    fw_dnat_info_fk.create()

    fw_packetfilter_info_fk = ForeignKeyConstraint(
        [fw_packetfilter_info_table.c.vfw_id],
        [fw_vfw_info_table.c.id])
    fw_packetfilter_info_fk.create()

    fw_staticnat_info_fk = ForeignKeyConstraint(
        [fw_staticnat_info_table.c.vfw_id],
        [fw_vfw_info_table.c.id])
    fw_staticnat_info_fk.create()

if __name__ == '__main__':
    sys.exit(main())
