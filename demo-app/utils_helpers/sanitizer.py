import re


ALLOWED_TAGS = {"b", "i", "em", "strong", "p", "br", "ul", "ol", "li"}

TAG_PATTERN = re.compile(r"<(/?)(\w+)([^>]*)>")

ENTITY_MAP = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#x27;",
}


def escape_html(text):
    if not isinstance(text, str):
        return ""
    for char, entity in ENTITY_MAP.items():
        text = text.replace(char, entity)
    return text


def sanitize_html(text):
    if not isinstance(text, str):
        return ""

    def replace_tag(match):
        closing, tag_name, attrs = match.groups()
        if tag_name.lower() in ALLOWED_TAGS:
            return f"<{closing}{tag_name.lower()}>"
        return escape_html(match.group(0))

    return TAG_PATTERN.sub(replace_tag, text)


def sanitize_filename(filename):
    if not isinstance(filename, str):
        return "unnamed"
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    filename = re.sub(r"[^\w\s\-.]", "", filename)
    return filename[:255] or "unnamed"
