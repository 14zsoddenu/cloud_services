def exclude_none_values(data):
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if value is not None:
                processed_value = exclude_none_values(value)
                if processed_value is not None:
                    result[key] = processed_value
    elif isinstance(data, list):
        result = []
        for item in data:
            processed_value = exclude_none_values(item)
            if processed_value is not None:
                result.append(processed_value)
    else:
        return data
    return result
