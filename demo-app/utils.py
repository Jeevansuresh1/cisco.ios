import requests
import time
import os
import uuid
import logging

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_BACKOFF = 1.5


def fetch_external_api(url, timeout=DEFAULT_TIMEOUT, retries=MAX_RETRIES):
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Fetching {url} (attempt {attempt}/{retries})")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            last_exception = requests.exceptions.Timeout(
                f"Request to {url} timed out after {timeout}s"
            )
            logger.warning(f"Timeout on attempt {attempt}/{retries} for {url}")
        except requests.exceptions.ConnectionError as e:
            last_exception = e
            logger.warning(f"Connection error on attempt {attempt}/{retries}: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from {url}: {e}")
            raise

        if attempt < retries:
            wait_time = RETRY_BACKOFF ** attempt
            logger.info(f"Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)

    raise last_exception


def format_user_display(user):
    name = _escape_html(user.get("name", ""))
    email = _escape_html(user.get("email", ""))
    return f"<div class='user-card'><h2>{name}</h2><p>{email}</p></div>"


def process_upload(file_data, user_id):
    upload_dir = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file_data.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, unique_name)

    file_data.save(filepath)
    logger.info(f"File saved: {filepath} (user: {user_id})")
    return filepath


def sanitize_input(text):
    if not isinstance(text, str):
        return ""
    return text.strip()


def _escape_html(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
