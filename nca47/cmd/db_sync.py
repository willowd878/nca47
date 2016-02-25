import sys

from oslo_log import log
import sqlalchemy as sa

from nca47.common.i18n import _LE
from nca47.common import service as nca47_service
from nca47.db import api as db_api
from nca47.objects import attributes as attr

LOG = log.getLogger(__name__)


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

    tables = [dns_servers, ]
    for table in tables:
        try:
            table.create()
        except Exception:
            LOG.info(repr(table))
            LOG.exception(_LE('Exception while creating table.'))
            raise


if __name__ == '__main__':
    sys.exit(main())
