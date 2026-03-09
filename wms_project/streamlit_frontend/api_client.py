"""
api_client.py — Helper functions for calling the Django REST API
"""

import requests
import streamlit as st

BASE_URL = "http://localhost:8000/api"


def get_headers():
    token = st.session_state.get("token", "")
    return {"Authorization": f"Token {token}", "Content-Type": "application/json"}


# ─── AUTH ─────────────────────────────────────────────────────────────────────
def login(username: str, password: str):
    try:
        r = requests.post(f"{BASE_URL}/auth/login/", json={"username": username, "password": password}, timeout=5)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server. Make sure Django is running on port 8000."}, 503


def logout():
    try:
        requests.post(f"{BASE_URL}/auth/logout/", headers=get_headers(), timeout=5)
    except Exception:
        pass


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
def get_dashboard_stats():
    try:
        r = requests.get(f"{BASE_URL}/dashboard/", headers=get_headers(), timeout=5)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


# ─── SKU ──────────────────────────────────────────────────────────────────────
def get_skus(search=""):
    try:
        params = {"search": search} if search else {}
        r = requests.get(f"{BASE_URL}/sku/", headers=get_headers(), params=params, timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def create_sku(data: dict):
    r = requests.post(f"{BASE_URL}/sku/create/", json=data, headers=get_headers(), timeout=5)
    return r.json(), r.status_code


def update_sku(pk: int, data: dict):
    r = requests.put(f"{BASE_URL}/sku/{pk}/", json=data, headers=get_headers(), timeout=5)
    return r.json(), r.status_code


def delete_sku(pk: int):
    r = requests.delete(f"{BASE_URL}/sku/{pk}/", headers=get_headers(), timeout=5)
    return r.status_code


# ─── INBOUND ──────────────────────────────────────────────────────────────────
def get_inbound_trucks():
    try:
        r = requests.get(f"{BASE_URL}/inbound/", headers=get_headers(), timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def create_inbound_truck(data: dict):
    r = requests.post(f"{BASE_URL}/inbound/create/", json=data, headers=get_headers(), timeout=5)
    return r.json(), r.status_code


def update_inbound_truck(pk: int, data: dict):
    r = requests.put(f"{BASE_URL}/inbound/{pk}/", json=data, headers=get_headers(), timeout=5)
    return r.json(), r.status_code


def delete_inbound_truck(pk: int):
    r = requests.delete(f"{BASE_URL}/inbound/{pk}/", headers=get_headers(), timeout=5)
    return r.status_code


# ─── OUTBOUND ─────────────────────────────────────────────────────────────────
def get_outbound_trucks():
    try:
        r = requests.get(f"{BASE_URL}/outbound/", headers=get_headers(), timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def create_outbound_truck(data: dict):
    r = requests.post(f"{BASE_URL}/outbound/create/", json=data, headers=get_headers(), timeout=5)
    return r.json(), r.status_code


def update_outbound_truck(pk: int, data: dict):
    r = requests.put(f"{BASE_URL}/outbound/{pk}/", json=data, headers=get_headers(), timeout=5)
    return r.json(), r.status_code


def delete_outbound_truck(pk: int):
    r = requests.delete(f"{BASE_URL}/outbound/{pk}/", headers=get_headers(), timeout=5)
    return r.status_code
