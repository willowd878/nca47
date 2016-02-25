import threading

from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import utils as oslo_db_utils
from oslo_log import log
from oslo_utils import strutils
from oslo_utils import uuidutils

from nca47.common import exception
from nca47.db import api
from nca47.db.sqlalchemy import models

LOG = log.getLogger(__name__)

_CONTEXT = threading.local()


def get_backend():
    """The backend is this module itself."""
    return Connection()


def _session_for_read():
    return enginefacade.reader.using(_CONTEXT)


def _session_for_write():
    return enginefacade.writer.using(_CONTEXT)


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """
    with _session_for_read() as session:
        query = oslo_db_utils.model_query(model, session, *args, **kwargs)
        return query


def add_identity_filter(query, id):
    """Adds an identity filter to a query.

    Filters results by ID, if supplied value is a valid integer.
    Otherwise attempts to filter results by UUID.

    :param query: Initial query to add filter to.
    :param id: id for filtering results by.
    :return: Modified query.
    """
    if uuidutils.is_uuid_like(id):
        return query.filter_by(id=id)
    else:
        raise exception.Invalid("invalid id")


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def create_dns_server(self, server):
        args = {
            'id': uuidutils.generate_uuid(),
            'name': server['name'],
        }
        dns_server = models.DnsServer(**args)
        with _session_for_write() as session:
            try:
                session.add(dns_server)
                session.flush()
            except db_exc.DBDuplicateEntry as exc:
                raise exception.Nca47Exception(exc.message)
            return dns_server

    def delete_dns_server(self, id):
        with _session_for_write():
            query = model_query(models.DnsServer)
            query = add_identity_filter(query, id)
            query.delete()

    def get_dns_server(self, id):
        with _session_for_read():
            query = model_query(models.DnsServer)
            query = add_identity_filter(query, id)
            dns_server_ref = query.one()
            return dns_server_ref

    def list_dns_servers(self):
        with _session_for_read():
            query = model_query(models.DnsServer)
            dns_servers_ref = query.all()
            return dns_servers_ref

    def update_dns_server(self, id, values):
        try:
            return self._do_update_dns_server(id, values)
        except Exception as e:
            raise e

    def _do_update_dns_server(self, id, values):
        with _session_for_write():
            query = model_query(models.DnsServer)
            query = add_identity_filter(query, id)
            ref = query.with_lockmode('update').one()
            ref.update(values)
        return ref
