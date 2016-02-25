from oslo_db.sqlalchemy import models
from oslo_utils import uuidutils
import sqlalchemy as sa
from sqlalchemy.ext import declarative

from nca47.objects import attributes as attr


class Nca47Base(models.ModelBase,
                models.SoftDeleteMixin,
                models.ModelIterator):
    """Base class for Nca47 Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}

    @declarative.declared_attr
    def __tablename__(cls):
        """
        Use the pluralized name of the class as the table.
        eg. If class name is DnsServer, return dns_servers.
        """
        cls_name_list = ['_' + s if s.isupper() else s for s in cls.__name__]
        return ''.join(cls_name_list).lstrip('_').lower() + 's'

    def __repr__(self):
        """sqlalchemy based automatic __repr__ method."""
        items = ['%s=%r' % (col.name, getattr(self, col.name))
                 for col in self.__table__.columns]
        return "<%s.%s[object at %x] {%s}>" % (self.__class__.__module__,
                                               self.__class__.__name__,
                                               id(self), ', '.join(items))

    def next(self):
        self.__next__()


BASE = declarative.declarative_base(cls=Nca47Base)


class HasTenant(object):
    """Tenant mixin, add to subclasses that have a tenant."""

    tenant_id = sa.Column(sa.String(attr.TENANT_ID_MAX_LEN), index=True)


class HasId(object):
    """id mixin, add to subclasses that have an id."""

    id = sa.Column(sa.String(attr.UUID_LEN),
                   primary_key=True,
                   default=uuidutils.generate_uuid)


class HasStatus(object):
    """Status mixin."""

    status = sa.Column(sa.String(16), nullable=False)
