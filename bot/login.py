import os
import requests
import sys
from loader import BASE_DIR
from dotenv import load_dotenv

load_dotenv((BASE_DIR / ".env").as_posix())

API_BASE_URL = os.getenv("API_BASE_URL")
if API_BASE_URL is None:
    sys.exit("Incorrect API url")


def get_token(username: str = None, password: str = None) -> str:
    if (username is None) or (password is None):
        data = {
            "username": os.getenv("TG_USERNAME"),
            "password": os.getenv("PASSWORD")
        }
    else:
        data = {
            "username": username,
            "password": password
        }
    response = requests.post(url=API_BASE_URL + "auth/token/login/",
                             data=data)
    # if response.status_code == 400:
    #     requests.post(url=API_BASE_URL + "auth/users/",
    #                   data=data)
    #     response = requests.post(url=API_BASE_URL + "auth/token/login/",
    #                              data=data)
    #     json_data = response.json()
    #     return json_data["auth_token"]
    # else:
    json_data = response.json()
    return json_data["auth_token"]
