from django.db.models import DurationField
from django.utils.duration import duration_iso_string


class ISODurationString(DurationField):
    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        if val is None:
            return ""

        return duration_iso_string(val)
