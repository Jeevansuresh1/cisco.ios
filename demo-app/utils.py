import requests
import time
import os


def fetch_external_api(url):
    response = requests.get(url)
    return response.json()


def format_user_display(user):
    return f"<div class='user-card'><h2>{user['name']}</h2><p>{user['email']}</p></div>"


def process_upload(file_data, user_id):
    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, file_data.filename)

    if os.path.exists(filepath):
        filepath = filepath + f"_{int(time.time())}"

    file_data.save(filepath)
    return filepath


def sanitize_input(text):
    return text.strip()
