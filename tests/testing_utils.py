import json

from django.http import JsonResponse


def empty_data_validation(logged_client, url, expected_result, status_code):
    response: JsonResponse = logged_client.get(
        url,
        HTTP_USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/85.0.4183.102 "
        "Safari/537.36",
    )
    try:
        assert response.status_code == status_code
    except AssertionError as e:
        raise
    content = json.loads(response.content)
    if type(content) != dict and type(content) != list:
        content = json.loads(content)
    assert content == expected_result


def remove_Z_in_datetime_value(d):
    if not isinstance(d, dict) and not isinstance(d, list):
        return d

    if isinstance(d, dict):
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = remove_Z_in_datetime_value(value)
            elif isinstance(value, list):
                result[key] = [remove_Z_in_datetime_value(v) for v in value]
            elif "time" in key or "_on" in key:
                try:
                    result[key] = value[: value.index("Z")]
                except (ValueError, AttributeError):
                    result[key] = value
            else:
                result[key] = value
    elif isinstance(d, list):
        result = [remove_Z_in_datetime_value(item) for item in d]
    else:
        result = None
    return result


def exclude_time_values(d):
    if isinstance(d, dict):
        result = {}
        for key, value in d.items():
            if not "time" in key:
                result[key] = value
    else:
        return d
    return result
