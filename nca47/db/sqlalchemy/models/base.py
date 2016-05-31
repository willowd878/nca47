from oslo_db.sqlalchemy import models
import json
from sqlalchemy.types import TypeDecorator, Text
from oslo_utils import timeutils
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

    def soft_delete(self, session):
        """Mark this object as deleted."""
        self.deleted = True
        self.deleted_at = timeutils.utcnow()
        self.save(session=session)


BASE = declarative.declarative_base(cls=Nca47Base)


class HasTenant(object):
    """Tenant mixin, add to subclasses that have a tenant."""

    tenant_id = sa.Column(sa.String(attr.TENANT_ID_MAX_LEN), index=True)


class HasId(object):
    """id mixin, add to subclasses that have an id."""

    id = sa.Column(sa.String(attr.UUID_LEN),
                   primary_key=True,
                   default=uuidutils.generate_uuid)


class HasOperationMode(object):
    """operation_fro mixin, add to subclasses that have an operation_fro."""
    operation_fro = sa.Column(sa.String(attr.NAME_MAX_LEN),
                              default='AUTO')


class HasStatus(object):
    """Status mixin."""

    status = sa.Column(sa.String(16), nullable=False)


class JsonEncodedList(TypeDecorator):
    """
    rewrite oslo.db JsonEncodedList class in type module, in order to
    support chinese character, make sure chinese character can be insert
    into Database as UTF-8 charset
    """

    type = list
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is None:
            if self.type is not None:
                # Save default value according to current type to keep the
                # interface consistent.
                value = self.type()
        elif self.type is not None and not isinstance(value, self.type):
            if isinstance(value, basestring):
                tmp_value = []
                tmp_value.append(value)
                value = tmp_value
        serialized_value = json.dumps(value, encoding='UTF-8',
                                      ensure_ascii=False)
        return serialized_value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
