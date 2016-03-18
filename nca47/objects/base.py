import abc

from oslo_db import exception as obj_exc
from oslo_utils import reflection
from oslo_versionedobjects import base as obj_base
import six

from nca47.common.i18n import _
from nca47.common import exception
from nca47.db import api as db_api


class NotSpecifiedSentinel:
    pass


class ObjectUpdateForbidden(exception.Nca47Exception):
    _msg_fmt = _("Unable to update the following object fields: %(fields)s")


class DuplicateEntry(exception.Conflict):
    _msg_fmt = _("Failed to create a duplicate %(object_type)s: "
                 "for attribute(s) %(attributes)s with value(s) %(values)s")

    def __init__(self, object_class, db_exception):
        super(DuplicateEntry, self).__init__(
            object_type=reflection.get_class_name(object_class,
                                                  fully_qualified=False),
            attributes=db_exception.columns,
            values=db_exception.value)


def get_updatable_fields(cls, fields):
    fields = fields.copy()
    for field in cls.fields_no_update:
        if field in fields:
            del fields[field]
    return fields


@six.add_metaclass(abc.ABCMeta)
class Nca47Object(obj_base.VersionedObject,
                  obj_base.VersionedObjectDictCompat,
                  obj_base.ComparableVersionedObject):
    synthetic_fields = []

    def __init__(self, context=None, **kwargs):
        super(Nca47Object, self).__init__(context, **kwargs)

    def to_dict(self):
        return dict(self.items())

    def as_dict(self):
        return dict((k, getattr(self, k))
                    for k in self.fields
                    if hasattr(self, k))

    @classmethod
    def clean_obj_from_primitive(cls, primitive, context=None):
        obj = cls.obj_from_primitive(primitive, context)
        obj.obj_reset_changes()
        return obj

    @classmethod
    def get_by_id(cls, context, id):
        raise NotImplementedError()

    @classmethod
    def validate_filters(cls, **kwargs):
        bad_filters = [key for key in kwargs
                       if key not in cls.fields or key in cls.synthetic_fields]
        if bad_filters:
            bad_filters = ', '.join(bad_filters)
            msg = _("'%s' is not supported for filtering") % bad_filters
            raise exception.Invalid(error_message=msg)

    @classmethod
    @abc.abstractmethod
    def get_objects(cls, context, **kwargs):
        raise NotImplementedError()

    def create(self, context, values):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def get_object(self, context, values):
        raise NotImplementedError()


class Nca47DbObject(Nca47Object):
    # should be overridden for all persistent objects
    db_model = None

    fields_no_update = []

    def __init__(self):
        self.db_api = db_api.get_instance()
        super(Nca47DbObject, self).__init__()

    def from_db_object(self, *objs):
        for field in self.fields:
            for db_obj in objs:
                if field in db_obj:
                    setattr(self, field, db_obj[field])
                break
        self.obj_reset_changes()

    @classmethod
    def get_by_id(cls, context, id):
        db_obj = db_api.get_instance().get_object(context, cls.db_model, id=id)
        if db_obj:
            obj = cls(context, **db_obj)
            obj.obj_reset_changes()
            return obj

    @classmethod
    def get_objects(cls, context, **kwargs):
        cls.validate_filters(**kwargs)
        db_objs = db_api.get_instance().get_objects(context, cls.db_model,
                                                    **kwargs)
        objs = [cls(context, **db_obj) for db_obj in db_objs]
        for obj in objs:
            obj.obj_reset_changes()
        return objs

    def _get_changed_persistent_fields(self):
        fields = self.obj_get_changes()
        for field in self.synthetic_fields:
            if field in fields:
                del fields[field]
        return fields

    def _validate_changed_fields(self, fields):
        fields = fields.copy()
        # We won't allow id update anyway, so let's pop it out not to trigger
        # update on id field touched by the consumer
        fields.pop('id', None)

        forbidden_updates = set(self.fields_no_update) & set(fields.keys())
        if forbidden_updates:
            raise ObjectUpdateForbidden(fields=forbidden_updates)

        return fields

    def create(self):
        fields = self._get_changed_persistent_fields()
        try:
            db_obj = self.db_api.create_object(self._context, self.db_model,
                                               fields)
        except obj_exc.DBDuplicateEntry as db_exc:
            raise DuplicateEntry(object_class=self.__class__,
                                 db_exception=db_exc)

        self.from_db_object(db_obj)

    def update(self):
        updates = self._get_changed_persistent_fields()
        updates = self._validate_changed_fields(updates)

        if updates:
            db_obj = self.db_api.update_object(self._context, self.db_model,
                                               self.id, updates)
            self.from_db_object(self, db_obj)

    def delete(self):
        self.db_api.delete_object(self._context, self.db_model, self.id)
