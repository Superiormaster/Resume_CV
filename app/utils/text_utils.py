
def split_text_to_lines(text, max_chars):
    """Split text into multiple lines without breaking words."""
    if not text:
        return []
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        cur = ""
        for w in words:
            if len(cur) + len(w) + (1 if cur else 0) <= max_chars:
                cur += (" " if cur else "") + w
            elif len(w) > max_chars:
                while len(w) > max_chars:
                    lines.append(w[:max_chars])
                    w = w[max_chars:]
                cur = w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines