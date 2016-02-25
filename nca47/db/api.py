import abc

from oslo_config import cfg
from oslo_db import api as db_api
from oslo_db.sqlalchemy import session
import six

_BACKEND_MAPPING = {'sqlalchemy': 'nca47.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)
_FACADE = None


def get_instance():
    """Return a DB API instance."""
    return IMPL


def _create_facade_lazily():
    global _FACADE

    if _FACADE is None:
        _FACADE = session.EngineFacade.from_config(cfg.CONF, sqlite_fk=True)

    return _FACADE


def get_engine():
    """Helper method to grab engine."""
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session():
    return IMPL.get_session()


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    @abc.abstractmethod
    def create_dns_server(self, dns_server):
        """Create a new dns server"""

    @abc.abstractmethod
    def delete_dns_server(self, id):
        """Delete a dns server"""

    @abc.abstractmethod
    def get_dns_server(self, id):
        """Return a dns server"""

    @abc.abstractmethod
    def list_dns_servers(self):
        """Return dns server list"""

    @abc.abstractmethod
    def update_dns_server(self, id, dns_server):
        """Update a dns server"""
