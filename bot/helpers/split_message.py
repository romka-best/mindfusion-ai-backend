def split_message(markdown_text: str, limit=4096):
    parts = []
    current_part = ""

    for line in markdown_text.splitlines(keepends=True):
        if len(current_part) + len(line) <= limit:
            current_part += line
        else:
            parts.append(current_part)
            current_part = line

    if current_part:
        parts.append(current_part)

    return [part.strip() for part in parts]
