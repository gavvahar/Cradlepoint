import csv

input_file = "w2005-ATT-7-23-90-NAT_spdtst.csv"
output_file = "w2005-ATT-7-23-90-NAT_spdtst_reformatted.csv"

REMOVE_COLS = [
    "is_individually_configured",
    "desc",
    "asset_id",
    "mac",
    "actual_firmware_version",
    "last_fw_activity_state",
    "account_name",
    "custom1",
    "router_state_ts",
    "serial_number",
]


def parse_asset_id(asset_id):
    # Example: DL:23.55Mbps - UL:26.16Mbps - Ping:66.122ms - Server:GoNetspeed - ISP:AT&T Wireless - TimeGMT:2025-08-05T16:47:10.175156Z - Img:http://www.speedtest.net/result/18064513079.png
    result = {
        "DL": "",
        "UL": "",
        "Ping": "",
        "Server": "",
        "ISP": "",
        "TimeGMT": "",
        "Img": "",
    }
    if not asset_id:
        return result
    # Split by ' - ' and parse each part
    parts = asset_id.split(" - ")
    for part in parts:
        if part.startswith("DL:"):
            result["DL"] = part[3:].strip()
        elif part.startswith("UL:"):
            result["UL"] = part[3:].strip()
        elif part.startswith("Ping:"):
            result["Ping"] = part[5:].strip()
        elif part.startswith("Server:"):
            result["Server"] = part[7:].strip()
        elif part.startswith("ISP:"):
            result["ISP"] = part[4:].strip()
        elif part.startswith("TimeGMT:"):
            result["TimeGMT"] = part[8:].strip()
        elif part.startswith("Img:"):
            result["Img"] = part[4:].strip()
    return result


with open(input_file, newline="", encoding="utf-8") as infile, open(
    output_file, "w", newline="", encoding="utf-8"
) as outfile:
    reader = csv.DictReader(infile)
    # Remove unwanted columns from fieldnames
    fieldnames = [f for f in reader.fieldnames if f not in REMOVE_COLS]
    # Add new columns
    fieldnames += [
        "DL",
        "UL",
        "Ping",
        "Server",
        "ISP",
        "TimeGMT",
        "Img",
    ]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    rows_with_asset = []
    rows_without_asset = []
    for row in reader:
        asset_id_val = row.get("asset_id", "")
        asset_fields = parse_asset_id(asset_id_val)
        row.update(asset_fields)
        # Remove unwanted columns from row
        for col in REMOVE_COLS:
            row.pop(col, None)
        if asset_id_val.strip():
            rows_with_asset.append(row)
        else:
            rows_without_asset.append(row)
    # Write rows with asset_id first, then those without
    for row in rows_with_asset + rows_without_asset:
        writer.writerow(row)
