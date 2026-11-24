"""Load email templates and replace {{placeholders}} with real values."""
import re

from .config import TEMPLATES_DIR

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def load_template(filename: str):
    """Template format: first line 'Subject: ...', then the body. Returns (subject, body)."""
    path = TEMPLATES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {filename}")
    first_line, _, body = path.read_text(encoding="utf-8").partition("\n")
    if not first_line.lower().startswith("subject:"):
        raise ValueError(f"Template {filename} must start with 'Subject:'")
    return first_line[len("subject:"):].strip(), body.strip()


def render(text: str, context: dict) -> str:
    """Replace {{key}} with context[key]. A missing key raises KeyError (caught + logged upstream)."""
    def _replace(match):
        key = match.group(1)
        if key not in context:
            raise KeyError("Missing value for placeholder '" + key + "'")
        return str(context[key])

    return PLACEHOLDER.sub(_replace, text)
