from oslo_config import cfg
from oslo_log import log as logging
import six
from six.moves import http_client
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.common.i18n import _LW

LOG = logging.getLogger(__name__)


exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help=_('Used if there is a formatting error when generating '
                       'an exception message (a programming error). If True, '
                       'raise an exception; if False, use the unformatted '
                       'message.')),
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


class Nca47Exception(Exception):
    """
    Base Nca Exception

    To correctly use this class, inherit from it and define
    a '_msg_fmt' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    If you need to access the message from an exception you should use
    six.text_type(exc)

    """
    _msg_fmt = _("An unknown exception occurred.")
    code = http_client.INTERNAL_SERVER_ERROR
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            # Check if class is using deprecated 'message' attribute.
            if (hasattr(self, 'message') and self.message):
                LOG.warning(_LW("Exception class: %s Using the 'message' "
                                "attribute in an exception has been "
                                "deprecated. The exception class should be "
                                "modified to use the '_msg_fmt' "
                                "attribute."), self.__class__.__name__)
                self._msg_fmt = self.message

            try:
                message = self._msg_fmt % kwargs

            except Exception as e:
                # kwargs doesn't match a variable in self._msg_fmt
                # log the issue and the kwargs
                LOG.exception(_LE('Exception in string format operation'))
                for name, value in kwargs.items():
                    LOG.error("%s: %s" % (name, value))

                if CONF.fatal_exception_format_errors:
                    raise e
                else:
                    # at least get the core self._msg_fmt out if something
                    # happened
                    message = self._msg_fmt

        super(Nca47Exception, self).__init__(message)

    def __str__(self):
        """Encode to utf-8 then wsme api can consume it as well."""
        if not six.PY3:
            return unicode(self.args[0]).encode('utf-8')

        return self.args[0]

    def __unicode__(self):
        """Return a unicode representation of the exception message."""
        return unicode(self.args[0])


class NotAuthorized(Nca47Exception):
    _msg_fmt = _("Not authorized.")
    code = http_client.FORBIDDEN


class OperationNotPermitted(NotAuthorized):
    _msg_fmt = _("Operation not permitted.")


class Invalid(Nca47Exception):
    _msg_fmt = _("Unacceptable parameters.")
    code = http_client.BAD_REQUEST


class checkParam(Nca47Exception):
    _msg_fmt = _("check param :%(param_name)s is errored")


class checkBody(Nca47Exception):
    _msg_fmt = _("check body is None!")
    code = http_client.BAD_REQUEST


class BadRequest(Nca47Exception):
    _msg_fmt = _('Bad %(resource)s request: %(msg)s.')


class NotFound(Nca47Exception):
    _msg_fmt = _("Resource could not be found.")
    code = http_client.NOT_FOUND


class Conflict(Nca47Exception):
    pass


class HaveSameObject(Nca47Exception):
    _msg_fmt = _("The object with name= %(object_name)s already exists")
    code = http_client.BAD_REQUEST


class NonExistDevices(NotFound):
    _msg_fmt = _("some devices don't exist any more")


class DriverNotFound(NotFound):
    _msg_fmt = _("Could not find the following driver(s): %(driver_name)s.")


class ParamNull(Nca47Exception):
    _msg_fmt = _("the values of the %(param_name)s is null")


class ParamFormatError(Nca47Exception):
    _msg_fmt = _("the values of the %(param_name)s format error")


class NonExistParam(Nca47Exception):
    _msg_fmt = _("please input the %(param_name)s")


class ParamValueError(Nca47Exception):
    _msg_fmt = _("the value of the %(param_name)s is error")


class IsNotExistError(Nca47Exception):
    _msg_fmt = _("The object of %(param_name)s don't exist!")


class NoexistOrMultipleError(Nca47Exception):
    _msg_fmt = _("The object of %(param_name)s don't exist or exist multiple"
                 " results!")


class DBError(Nca47Exception):
    _msg_fmt = _("DB error happened in %(param_name)s method")


class RecordNotInZone(Nca47Exception):
    _msg_fmt = _("the record %(record_id)s not in %(zone_id)s !")


class RrsNameValueError(Nca47Exception):
    _msg_fmt = _("rrs name %(json_name)s don't end of the %(zone_name)s !")


class ZoneOfRecordIsError(Nca47Exception):
    _msg_fmt = _("Zone of rrs name %(json_name)s is Error!")


class ConfigInvalid(Nca47Exception):
    _msg_fmt = _("Config is Error!")
