import requests
import time
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "token.env"))

TAGO_API_URL = os.environ.get("TAGO_API_URL", "https://api.us-e1.tago.io")
NETWORK_TOKEN = os.environ["NETWORK_TOKEN"]
AUTHORIZATION_TOKEN = os.environ["AUTHORIZATION_TOKEN"]

# --- TESTE: alterne entre True/False pra comparar comportamento ---
TESTAR_SEM_AUTHORIZATION = True

_token_cache = {}
CACHE_TTL = 3600

def resolve_device_token(imei):
    cached = _token_cache.get(imei)
    if cached and (time.time() - cached["resolved_at"] < CACHE_TTL):
        return cached["token"]

    if TESTAR_SEM_AUTHORIZATION:
        url = f"{TAGO_API_URL}/integration/network/resolve/{imei}"
    else:
        url = f"{TAGO_API_URL}/integration/network/resolve/{imei}/{AUTHORIZATION_TOKEN}"

    try:
        resp = requests.get(url, headers={"Authorization": NETWORK_TOKEN}, timeout=10)
        print(f"[TAGOIO DEBUG] url={url}")
        print(f"[TAGOIO DEBUG] status={resp.status_code} body={resp.text}")
        resp.raise_for_status()
        data = resp.json()
        if data.get("status"):
            token = data["result"]
            _token_cache[imei] = {"token": token, "resolved_at": time.time()}
            return token
    except Exception as e:
        print(f"[TAGOIO] Erro ao resolver token para IMEI {imei}: {e}")
    return None

def send_data(imei, variables: list):
    token = resolve_device_token(imei)
    if not token:
        print(f"[TAGOIO] Sem device-token para IMEI {imei}, pulando envio.")
        return False

    try:
        resp = requests.post(
            f"{TAGO_API_URL}/data",
            headers={"device-token": token},
            json=variables,
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[TAGOIO] Falha ao enviar dados para IMEI {imei}: {e}")
        return False