from dotenv import load_dotenv
from os import path
import os


load_dotenv()

def get_headers():
    """Return the headers required for API requests."""
    return {
        "X-CP-API-ID": os.getenv("X_CP_API_ID"),
        "X-CP-API-KEY": os.getenv("X_CP_API_KEY"),
        "X-ECM-API-ID": os.getenv("X_ECM_API_ID"),
        "X-ECM-API-KEY": os.getenv("X_ECM_API_KEY"),
        "Content-Type": "application/json",
    }

def get_router_id_by_name(device_name):
    """Fetch the router ID for the specified device name from the Cradlepoint API."""
    url = f"{base_url}/routers/?name={device_name}"
    print(url)
    headers = get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.json()}")
    try:
        router_data = response.json()
    except json.JSONDecodeError:
        raise Exception("Error decoding JSON response")
    if not router_data["data"]:
        print("No router found with the specified Store Number.")
        sys.exit(1)

    for router in router_data["data"]:
        if product_name in router["full_product_name"]:
            return router["id"]

    print(f"No router found with '{product_name}' in the full product name.")
    sys.exit(1)

def do_speedtest(router_id):
    url = f"{base_url}/routers/{router_id}/"
    headers = get_headers()
    req = requests.put(url, headers=headers, json={"asset_id": ""})
    if req.status_code == 401:
        raise Exception("Unauthorized: Invalid Credentials")
    return req


def get_speedtest(router_id):
    url = f"{base_url}/routers/{router_id}/"
    headers = get_headers()
    req = requests.get(url, headers=headers, json={"asset_id": ""})
    if req.status_code == 401:
        raise Exception("Unauthorized: Invalid Credentials")
    return req
