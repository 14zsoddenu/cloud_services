import base64
import zlib
from typing import Optional, Union

from django.db import models
from django.db.models import DurationField
from django.utils.duration import duration_iso_string


class ISODurationString(DurationField):
    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        if val is None:
            return ""

        return duration_iso_string(val)


class ImageStringField(models.TextField):
    def to_python(self, value: Optional[Union[str, bytes]]):
        if value is None or type(value) == bytes:
            return value

        return zlib.decompress(base64.b64decode(value.encode()))

    def from_db_value(self, value, expression, connection):
        if value is None or type(value) == bytes:
            return value

        return zlib.decompress(base64.b64decode(value.encode()))

    def get_prep_value(self, value: Optional[Union[memoryview, bytes]]):
        if value is None:
            return value
        if type(value) == str:
            return value
        return base64.b64encode(zlib.compress(value)).decode()
