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


def get_session(autocommit=True, expire_on_commit=False, use_slave=False):
    """Helper method to grab session."""
    facade = _create_facade_lazily()
    return facade.get_session(autocommit=autocommit,
                              expire_on_commit=expire_on_commit,
                              use_slave=use_slave)


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    @abc.abstractmethod
    def create(self, model, values):
        """Create an object."""

    @abc.abstractmethod
    def get_object(self, model, **kwargs):
        """Get an object."""

    @abc.abstractmethod
    def get_objects(self, model, **kwargs):
        """Get an object list."""

    @abc.abstractmethod
    def update_object(self, model, id, values):
        """Update an object."""

    @abc.abstractmethod
    def delete_object(self, model, id):
        """Delete an object."""
