import logging
import requests
from xkcd_scripts.utils import setup_logging

setup_logging()

def get_last_id():
    try:
        response = requests.get("https://xkcd.com/info.0.json", timeout=5)
        response.raise_for_status()
        return response.json().get("num")
    except Exception as e:
        logging.error(f"Error fetching the latest comic ID: {e}")
        return None

def extract_comic_metadata(comic_id):
    url = f"https://xkcd.com/{comic_id}/info.0.json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logging.warning(f"Timeout for comic ID {comic_id}. Skipping.")
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            logging.warning(f"Comic ID {comic_id} not found (404). Skipping.")
        else:
            logging.error(f"HTTP error for comic ID {comic_id}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error for comic ID {comic_id}: {req_err}")
    except Exception as err:
        logging.exception(f"Unexpected error for comic ID {comic_id}: {err}")
    return None