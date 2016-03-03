import exceptions as exc
import functools
import pecan
from pecan import rest

from oslo_log import log as logging

from nca47.common.i18n import _

LOG = logging.getLogger(__name__)


def expose(function):
    """
    Packaging pecan RestController expose method. Resolving WSGi request body.
    """

    @pecan.expose('json')
    @functools.wraps(function)
    def decorated_function(self, *args, **kwargs):
        func = functools.partial(function, self, pecan.request)
        return func(*args, **kwargs)

    return decorated_function


class BaseRestController(rest.RestController):
    """
    A base class implement pecan RestController.
    """

    @expose
    def post(self, req, *args, **kwargs):
        LOG.debug(_('args: %(args)s, kwargs: %(kwargs)s'),
                  {"args": args, "kwargs": kwargs})
        return self._post(req, *args, **kwargs)

    @expose
    def put(self, req, id, *args, **kwargs):
        LOG.debug(_('id: %(id)s, args: %(args)s, kwargs: %(kwargs)s'),
                  {"id": id, "args": args, "kwargs": kwargs})
        return self._put(req, id, *args, **kwargs)

    @expose
    def delete(self, req, id, *args, **kwargs):
        LOG.debug(_('id: %(id)s, args: %(args)s, kwargs: %(kwargs)s'),
                  {"id": id, "args": args, "kwargs": kwargs})
        return self._delete(req, id, *args, **kwargs)

    @expose
    def get_all(self, req, *args, **kwargs):
        LOG.debug(_('args: %(args)s, kwargs: %(kwargs)s'),
                  {"args": args, "kwargs": kwargs})
        return self._get_all(req, *args, **kwargs)

    @expose
    def get_one(self, req, id, *args, **kwargs):
        LOG.debug(_('id: %(id)s, args: %(args)s, kwargs: %(kwargs)s'),
                  {"id": id, "args": args, "kwargs": kwargs})
        return self._get_one(req, id, *args, **kwargs)

    def _post(self, req, *args, **kwargs):
        raise exc.NotImplementedError

    def _put(self, req, id, *args, **kwargs):
        raise exc.NotImplementedError

    def _delete(self, req, id, *args, **kwargs):
        raise exc.NotImplementedError

    def _get_all(self, req, *args, **kwargs):
        raise exc.NotImplementedError

    def _get_one(self, req, id, *args, **kwargs):
        raise exc.NotImplementedError
