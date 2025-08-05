from dotenv import load_dotenv
from os import path
import os, json, requests, sys, glob, csv, re, time


load_dotenv()

base_url = "https://www.cradlepointecm.com/api/v2"
product_name = ["W1850", "W2005"]

# Get all device names from all CSV files in the current directory
device_name = []
for csv_file in glob.glob("*.csv"):
    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "name" in row:
                device_name.append(row["name"])


def get_headers():
    """Return the headers required for API requests."""
    headers = {
        "X-CP-API-ID": os.getenv("X_CP_API_ID"),
        "X-CP-API-KEY": os.getenv("X_CP_API_KEY"),
        "X-ECM-API-ID": os.getenv("X_ECM_API_ID"),
        "X-ECM-API-KEY": os.getenv("X_ECM_API_KEY"),
        "Content-Type": "application/json",
    }
    return headers


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
        if any(pn in router["full_product_name"] for pn in product_name):
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


max_wait_time = 60
interval = 15
elapsed_time = 0
router_ids = []
for name in device_name:
    router_id = get_router_id_by_name(name)
    router_ids.append(router_id)

# Only speedtest logic is executed after collecting router_ids.
for router_id in router_ids:
    response = do_speedtest(router_id)
    print(response.json())
    max_wait_time = 60  # 1 minute
    interval = 15  # 15 seconds
    elapsed_time = 0

    while elapsed_time < max_wait_time:
        response = get_speedtest(router_id)
        asset_id = response.json().get("asset_id")
        if asset_id:
            print("Asset ID:", asset_id)
            # Raw output from your script
            raw_output = asset_id

            # Define a pattern to match the key-value pairs
            pattern = r"(\w+):([^ -]+)(?: -|$)"

            # Find all matches using the regex
            matches = re.findall(pattern, raw_output)

            # Convert matches into a dictionary
            data = {key: value for key, value in matches}

            # Convert the dictionary to a JSON dump
            json_dump = json.dumps(data, indent=4)

            # Print the JSON dump
            data_dict = json.loads(json_dump)
            print("Speed test completed")
            print(json_dump)
            break
        time.sleep(interval)
        elapsed_time += interval
    else:
        errorMessage = "Error: Asset ID not found within the time limit"
        print(errorMessage)
