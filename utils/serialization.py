import json
from typing import Optional, List

from django.core import serializers
from django.db import models


def serialize_object(o: models.Model, exclude: Optional[List[str]] = None):
    data = json.loads(serializers.serialize("json", [o]))[0]
    unfiltered_result = {**data["fields"], **{"id": data["pk"]}}
    if exclude:
        return {key: value for key, value in unfiltered_result.items() if key not in exclude}
    return unfiltered_result


def serialize_objects(o_list: List[models.Model], exclude: Optional[List[str]] = None):
    unfiltered_results = [{**o["fields"], **{"pk": o["pk"]}} for o in json.loads(serializers.serialize("json", o_list))]
    if exclude:
        return [
            {key: value for key, value in unfiltered_result if key not in exclude}
            for unfiltered_result in unfiltered_results
        ]
    return unfiltered_results
