import threading

from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import utils as oslo_db_utils
from oslo_log import log
from oslo_utils import uuidutils
from sqlalchemy.orm.base import _entity_descriptor
from sqlalchemy import sql

from nca47.common import exception
from nca47.db import api
from nca47.api.controllers.v1 import tools

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


def beginSession(sess):
    try:
        sess.begin_nested()
    except:
        sess.begin(subtransactions=True)


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def create(self, model, values):
        with _session_for_write() as session:
            if 'id' not in values:
                values['id'] = uuidutils.generate_uuid()
            db_obj = model(**values)
            beginSession(session)
            try:
                session.add(db_obj)
                session.flush()
                session.commit()
            except Exception as e:
                session.rollback()
                LOG.exception(e)
                raise exception.DBError(param_name="CREATE")
        return dict(db_obj)

    def get_object(self, model, **kwargs):
        with _session_for_read():
            query = model_query(model)
            query = query.filter_by(**kwargs)
            db_obj = query.one()
            return db_obj

    def get_objects(self, model, **kwargs):
        with _session_for_read():
            query = model_query(model)
            query = query.filter_by(**kwargs)
            db_obj_list = query.all()
            return db_obj_list

    def _safe_get_object(self, model, id):
        db_obj = self.get_object(model, id=id)
        if db_obj is None:
            raise exception.NotFound()
        return db_obj

    def update_object(self, model, id, values):
        with _session_for_write() as session:
            db_obj = self._safe_get_object(model, id)
            beginSession(session)
            try:
                db_obj.update(values)
                session.commit()
            except Exception as e:
                session.rollback()
                LOG.exception(e)
                raise exception.DBError(param_name="UPDATE")
        return db_obj

    def delete_object(self, model, id):
        """Delete an object."""
        with _session_for_write() as session:
            beginSession(session)
            query = self._safe_get_object(model, id)
            try:
                query.soft_delete(session)
                session.commit()
            except Exception as e:
                session.rollback()
                LOG.exception(e)
                raise exception.DBError(param_name="UPDATE")
        return query

    def get_all_objects_by_conditions(self, model, like_dic, search_dic):
        with _session_for_read():
            query = model_query(model)

            like_clauses = [_entity_descriptor(query._joinpoint_zero(), key).
                            like('%' + value + '%') for key, value in
                            like_dic.items()]
            clauses = [_entity_descriptor(query._joinpoint_zero(), key) ==
                       value for key, value in search_dic.items()]

            clauses.extend(like_clauses)
            query = query.filter(sql.and_(*clauses))
            db_obj_list = query.all()
            return db_obj_list

    def get_all_objects(self, model, str_sql):
        with _session_for_read() as session:
            beginSession(session)
            try:
                connect = session.connection()
                result_obj = connect.execute(str_sql)
                keys = result_obj.keys()
                values = result_obj.fetchall()
            except Exception as e:
                LOG.exception(e)
                raise exception.DBError(param_name="get_all_by_fuzzy")
        obj_dic = tools.get_obj_list(keys, values)
        return obj_dic
