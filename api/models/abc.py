from django.db import models
from django.utils import timezone


class AbstractDatetimeTrackable(models.Model):
    added_datetime = models.DateTimeField(default=timezone.now)
    changed_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_added_datetime_lte_changed_datetime",
                check=models.Q(added_datetime__lte=models.F("changed_datetime")),
            )
        ]

    def __str__(self):
        name = self.name if hasattr(self, "name") else None
        return f"{self.__class__.__name__}({'name=' + name + ', ' if name else ''}added_datetime={self.added_datetime}, changed_datetime={self.changed_datetime})"
