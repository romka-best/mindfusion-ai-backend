def get_history_without_duplicates(history: list) -> list:
    result = []
    first_user_found = False

    for item in history:
        if not first_user_found and item["role"] == "user":
            first_user_found = True

        if first_user_found:
            if result and item["role"] == result[-1]["role"]:
                result[-1] = item
            else:
                result.append(item)

    return result
