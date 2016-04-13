import exceptions as exc
import pecan
from pecan import expose
from oslo_log import log as logging
from pecan import rest
from nca47.common.i18n import _

LOG = logging.getLogger(__name__)


class BaseRestController(rest.RestController):
    """
    A base class implement pecan RestController.
    """
    @expose('json')
    def index(self):
        return {"Information": "The url is for firewall resources"
                " RestApi interface"}

    @property
    def response(self):
        return pecan.response

    @expose('json')
    def post(self, *args, **kwargs):
        LOG.debug(_('args: %(args)s, kwargs: %(kwargs)s'),
                  {"args": args, "kwargs": kwargs})
        operation = args[0]
        req = pecan.request
        if operation == 'add':
            return self.create(req, *args, **kwargs)
        elif operation == 'del':
            return self.remove(req, *args, **kwargs)
        elif operation == 'get':
            return self.show(req, *args, **kwargs)
        elif operation == 'getall':
            return self.list(req, *args, **kwargs)
        elif operation == 'addif':
            return self.addif(req, *args, **kwargs)
        elif operation == 'delif':
            return self.delif(req, *args, **kwargs)
        else:
            pecan.abort(404)

    def create(self, req, *args, **kwargs):
        raise exc.NotImplementedError

    def remove(self, req, *args, **kwargs):
        raise exc.NotImplementedError

    def list(self, req, *args, **kwargs):
        raise exc.NotImplementedError

    def show(self, req, *args, **kwargs):
        raise exc.NotImplementedError
