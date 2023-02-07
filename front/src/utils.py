import unidecode

import requests
import streamlit as st
import yaml

import babel.numbers


with open("/conf/project_config.yml", "r") as f:
    PROJECT_CONFIG = yaml.safe_load(f)


def format_currency(value: float) -> str:
    return unidecode.unidecode(
        babel.numbers.format_currency(
            value, PROJECT_CONFIG.get("config", {}).get("currency")
        )
    )


def make_request(
    endpoint: str, method: str = "GET", data: dict | None = None
) -> requests.Response:

    url = f"http://api:8000/{endpoint}"

    if not st.session_state.get("session_id"):
        # session_id = random.getrandbits(128)
        session_id = "diversify"
        cookies = {"session_id": str(session_id)}
        st.session_state["session_id"] = str(session_id)
    else:
        cookies = {"session_id": st.session_state.get("session_id")}

    if method == "GET":
        response = requests.get(url, cookies=cookies, params=data)

    elif method == "PUT":
        response = requests.put(url, json=data, cookies=cookies)

    elif method == "DELETE":
        response = requests.delete(url, cookies=cookies)

    elif method == "POST":
        response = requests.post(url, json=data, cookies=cookies)

    else:
        raise Exception("Invalid method")

    return response


def fetch_assets() -> list[dict]:
    endpoint = "assets/"

    reponse = make_request(endpoint)

    assets = reponse.json()
    return assets["assets"]


def load_asset_classes() -> list[str]:
    return PROJECT_CONFIG.get("config", {}).get("asset_classes")


def save_asset(asset_class: str, asset_name: str, asset_value: float):
    endpoint = "assets/"
    data = {
        "class_name": asset_class,
        "name": asset_name,
        "value": asset_value,
    }

    r = make_request(endpoint, method="PUT", data=data)

    if r.ok:
        st.success("Asset saved", icon="✅")
    else:
        st.error("Error saving asset", icon="❌")


def get_class_assets(asset_class: str) -> list[dict]:
    endpoint = "assets/search"
    data = {
        "class_name": asset_class,
    }

    r = make_request(endpoint, method="GET", data=data)

    assets = r.json()["assets"]
    return assets


def update_asset_value(asset_name: str, asset_value: float):
    endpoint = "assets/"
    data = {
        "name": asset_name,
        "value": asset_value,
    }

    r = make_request(endpoint, method="POST", data=data)

    if r.ok:
        st.success("Asset updated", icon="✅")
    else:
        st.error("Error updating asset", icon="❌")


def delete_asset(asset_name: str):
    endpoint = f"assets/{asset_name}"

    r = make_request(endpoint, method="DELETE")

    if r.ok:
        st.success("Asset deleted", icon="✅")
    else:
        st.error("Error deleting asset!", icon="❌")
