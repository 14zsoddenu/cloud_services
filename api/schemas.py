from ninja import Schema
from ninja.orm import create_schema


class ErrorSchema(Schema):
    error: str


def create_update_schema(*args, **kwargs):
    result = create_schema(*args, **kwargs)
    for field_name, field in result.__fields__.items():
        field.required = False
    return result
