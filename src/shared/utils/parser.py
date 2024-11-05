from datetime import datetime
from enum import Enum


def to_dict(obj):
    if not hasattr(obj, "__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        element = []
        if isinstance(val, list):
            for item in val:
                element.append(to_dict(item))
        elif isinstance(val, datetime):
            element = val.isoformat()
        elif isinstance(val, Enum):
            element = val.value
        else:
            element = to_dict(val)
        result[key] = element
    return result
