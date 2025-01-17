def format_number(value: float | int):
    if value == float('inf'):
        return '♾️'

    return int(value) if float(value).is_integer() else value
