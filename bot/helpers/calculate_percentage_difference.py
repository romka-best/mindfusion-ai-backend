from typing import Union


def calculate_percentage_difference(
    is_all_time: bool, current: Union[int, float], before: Union[int, float]
):
    if is_all_time:
        return ""
    if before == 0:
        if current > 0:
            return "(+∞%)"
        elif current < 0:
            return "(-∞%)"
        else:
            return ""

    percentage_diff = round(((current - before) / before) * 100, 2)
    sign = "+" if percentage_diff >= 0 else ""
    return (
        f"({sign}{percentage_diff:.2f}%)"
        if percentage_diff % 1
        else f"({sign}{int(percentage_diff)}%)"
    )
