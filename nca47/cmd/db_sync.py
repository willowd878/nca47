import sys
import sqlalchemy as sa

from migrate.changeset.constraint import ForeignKeyConstraint
from oslo_log import log
from nca47.common import service as nca47_service
from nca47.common.i18n import _LE
from nca47.db import api as db_api
from nca47.objects import attributes as attr

sys.path.append('/vagrant/nca47')

LOG = log.getLogger(__name__)


def main():
    nca47_service.prepare_service(sys.argv)
    engine = db_api.get_engine()
    meta = sa.MetaData()
    meta.bind = engine

    dns_servers = sa.Table('dns_servers', meta,
                           sa.Column('id', sa.String(attr.UUID_LEN),
                                     primary_key=True,
                                     nullable=False),
                           sa.Column('name', sa.String(attr.NAME_MAX_LEN),
                                     nullable=True),
                           sa.Column('deleted_at', sa.DateTime(),
                                     nullable=True),
                           sa.Column('deleted', sa.Boolean(), nullable=True),
                           mysql_engine='InnoDB',
                           mysql_charset='utf8')

    nca_agent_info = sa.Table('nca_agent_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('agent_id', sa.String(attr.UUID_LEN), unique=True,
                  nullable=False),
        sa.Column('agent_ip', sa.String(attr.IP_LEN), nullable=False),
        sa.Column('agent_nat_ip', sa.String(attr.IP_LEN), nullable=True),
        sa.Column('dc_name', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('network_zone', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('agent_type', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('availiable', sa.Boolean(), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    nca_vdns_info = sa.Table('nca_vdns_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('vdns_id', sa.String(attr.UUID_LEN), unique=True,
                  nullable=False),
        sa.Column('vdns_name', sa.String(attr.NAME_MAX_LEN), nullable=True),
        sa.Column('tenant_id', sa.String(attr.TENANT_ID_MAX_LEN),
                  nullable=True),
        sa.Column('agent_id', sa.String(attr.UUID_LEN), nullable=True),
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
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    dns_zone_info = sa.Table('dns_zone_info', meta,
        sa.Column('id', sa.String(attr.UUID_LEN), primary_key=True,
                  nullable=False),
        sa.Column('zone_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('vdns_id', sa.String(attr.UUID_LEN), nullable=True),
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
        sa.Column('rrs_id', sa.String(attr.UUID_LEN), nullable=True),
        sa.Column('zone_id', sa.String(attr.UUID_LEN), nullable=False),
        sa.Column('rrs_name', sa.String(attr.NAME_MAX_LEN), nullable=False,
                  primary_key=True),
        sa.Column('type', sa.String(attr.TYPE_LEN), nullable=False,
                  primary_key=True),
        sa.Column('ttl', sa.String(attr.TTL_LEN), nullable=False),
        sa.Column('klass', sa.String(attr.TENANT_ID_MAX_LEN), nullable=True),
        sa.Column('rdata', sa.String(attr.TENANT_ID_MAX_LEN), nullable=True),
        sa.Column('operation_fro', sa.String(attr.NAME_MAX_LEN),
                  nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    tables = [dns_zone_info, nca_agent_info, nca_vdns_info,
              nca_operation_history, dns_rrs_info]
    for table in tables:
        try:
            if not table.exists():
                table.create()
        except Exception:
            LOG.info(repr(table))
            LOG.exception(_LE('Exception while creating table.'))
            raise

    nca_agent_info_table = sa.Table('nca_agent_info', meta, autoload=True)
    nca_vdns_info_table = sa.Table('nca_vdns_info', meta, autoload=True)
    nca_operation_history_table = sa.Table('nca_operation_history', meta,
                                           autoload=True)
    dns_zone_info_table = sa.Table('dns_zone_info', meta, autoload=True)
    dns_rrs_info_table = sa.Table('dns_rrs_info', meta, autoload=True)

    nca_vdns_info_agent_fk = ForeignKeyConstraint(
        [nca_vdns_info_table.c.agent_id],
        [nca_agent_info_table.c.agent_id])
    nca_vdns_info_agent_fk.create()

    nca_operation_history_rrs_fk = ForeignKeyConstraint(
        [nca_operation_history_table.c.config_id],
        [nca_vdns_info_table.c.id])
    nca_operation_history_rrs_fk.create()

#     dns_zone_info_rrs_fk = ForeignKeyConstraint(
#         [dns_zone_info_table.c.zone_id],
#         [dns_rrs_info_table.c.zone_id])
#     dns_zone_info_rrs_fk.create()

    dns_zone_info_vdns_fk = ForeignKeyConstraint(
        [dns_zone_info_table.c.vdns_id],
        [nca_vdns_info_table.c.vdns_id])
    dns_zone_info_vdns_fk.create()

if __name__ == '__main__':
    sys.exit(main())
