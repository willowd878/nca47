import ast
import six
from oslo_versionedobjects import fields as object_fields


class IntegerField(object_fields.IntegerField):
    pass


class UUIDField(object_fields.UUIDField):
    pass


class StringField(object_fields.StringField):
    pass


class DateTimeField(object_fields.DateTimeField):
    pass


class BooleanField(object_fields.BooleanField):
    pass


class ListOfStringsField(object_fields.ListOfStringsField):
    pass


class FlexibleDict(object_fields.FieldType):
    @staticmethod
    def coerce(obj, attr, value):
        if isinstance(value, six.string_types):
            value = ast.literal_eval(value)
        return dict(value)


class FlexibleDictField(object_fields.AutoTypedField):
    AUTO_TYPE = FlexibleDict()

    # TODO(lucasagomes): In our code we've always translated None to {},
    # this method makes this field to work like this. But probably won't
    # be accepted as-is in the oslo_versionedobjects library
    def _null(self, obj, attr):
        if self.nullable:
            return {}
        super(FlexibleDictField, self)._null(obj, attr)
