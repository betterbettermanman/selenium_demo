"""JSON 字段校验工具"""


def validate_json_object_or_array(value, field_name='JSON'):
    """校验值是否为 null 或 JSON 对象/数组。"""
    if value is None:
        return None
    if not isinstance(value, (dict, list)):
        return f'{field_name}必须是 JSON 对象或数组'
    return None
