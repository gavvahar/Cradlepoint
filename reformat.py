import csv, os, glob

CSV_FOLDER = "csv"
OUTPUT_FOLDER = "csv_reformatted"

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


if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

csv_files = glob.glob(os.path.join(CSV_FOLDER, "*.csv"))
for input_file in csv_files:
    base = os.path.splitext(os.path.basename(input_file))[0]
    ext = os.path.splitext(input_file)[1]
    output_file = os.path.join(OUTPUT_FOLDER, f"{base}_reformatted{ext}")
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
        total_rows = 0
        dl_ul_above_40 = 0
        dl_ul_below_or_eq_40 = 0
        blank_asset_id = 0
        non_blank_asset_id = 0
        for row in reader:
            total_rows += 1
            asset_id_val = row.get("asset_id", "")
            asset_fields = parse_asset_id(asset_id_val)
            row.update(asset_fields)
            # Remove unwanted columns from row
            for col in REMOVE_COLS:
                row.pop(col, None)
            # Count blank asset_id
            if not asset_id_val.strip():
                blank_asset_id += 1
                rows_without_asset.append(row)
            else:
                rows_with_asset.append(row)
                # Check DL/UL > 40Mbps and <= 40Mbps
                try:
                    dl_val = (
                        float(asset_fields["DL"].replace("Mbps", "").strip())
                        if asset_fields["DL"]
                        else 0
                    )
                except Exception:
                    dl_val = 0
                try:
                    ul_val = (
                        float(asset_fields["UL"].replace("Mbps", "").strip())
                        if asset_fields["UL"]
                        else 0
                    )
                except Exception:
                    ul_val = 0
                if dl_val > 40 or ul_val > 40:
                    dl_ul_above_40 += 1
                else:
                    dl_ul_below_or_eq_40 += 1
        # Write rows with asset_id first, then those without
        for row in rows_with_asset + rows_without_asset:
            writer.writerow(row)
        # Print stats for this file
        if total_rows > 0:
            percent_dl_ul_above_40 = (dl_ul_above_40 / total_rows) * 100
            percent_dl_ul_below_or_eq_40 = (dl_ul_below_or_eq_40 / total_rows) * 100
            percent_blank_asset_id = (blank_asset_id / total_rows) * 100
        else:
            percent_dl_ul_above_40 = 0
            percent_dl_ul_below_or_eq_40 = 0
            percent_blank_asset_id = 0
        print(f"File: {input_file}")
        print(
            f"  Percentage of rows with DL or UL > 40Mbps: {percent_dl_ul_above_40:.2f}%"
        )
        print(
            f"  Percentage of rows with DL and UL <= 40Mbps: {percent_dl_ul_below_or_eq_40:.2f}%"
        )
        print(
            f"  Percentage of rows with blank asset_id: {percent_blank_asset_id:.2f}%"
        )
