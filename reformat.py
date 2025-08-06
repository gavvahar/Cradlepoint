import csv, os, glob

CSV_FOLDER = "csv"
OUTPUT_FOLDER = f"{CSV_FOLDER}_reformatted"
REMOVE_COLS = {
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
}
NEW_COLS = ["DL", "UL", "Ping", "Server", "ISP", "TimeGMT", "Img"]


def parse_asset_id(asset_id):
    parts = dict(part.split(":", 1) for part in asset_id.split(" - ") if ":" in part)
    return {
        "DL": parts.get("DL", "").strip(),
        "UL": parts.get("UL", "").strip(),
        "Ping": parts.get("Ping", "").strip(),
        "Server": parts.get("Server", "").strip(),
        "ISP": parts.get("ISP", "").strip(),
        "TimeGMT": parts.get("TimeGMT", "").strip(),
        "Img": parts.get("Img", "").strip(),
    }


os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for input_file in glob.glob(os.path.join(CSV_FOLDER, "*.csv")):
    with open(input_file, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        base = os.path.splitext(os.path.basename(input_file))[0]
        out_path = os.path.join(OUTPUT_FOLDER, f"{base}_reformatted.csv")

        fieldnames = [f for f in reader.fieldnames if f not in REMOVE_COLS] + NEW_COLS
        with open(out_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            rows_with, rows_without = [], []
            total, over_40, under_or_eq_40, blank_asset = 0, 0, 0, 0

            for row in reader:
                total += 1
                asset_id = row.get("asset_id", "")
                parsed = parse_asset_id(asset_id)
                row.update(parsed)
                for col in REMOVE_COLS:
                    row.pop(col, None)

                if not asset_id.strip():
                    blank_asset += 1
                    rows_without.append(row)
                else:
                    rows_with.append(row)
                    try:
                        dl = float(parsed["DL"].replace("Mbps", "").strip() or 0)
                        ul = float(parsed["UL"].replace("Mbps", "").strip() or 0)
                    except ValueError:
                        dl = ul = 0

                    if dl > 40 or ul > 40:
                        over_40 += 1
                    else:
                        under_or_eq_40 += 1

            for row in rows_with + rows_without:
                writer.writerow(row)

            if total:
                print(f"File: {input_file}")
                print(f"  DL or UL > 40Mbps: {(over_40 / total) * 100:.2f}%")
                print(f"  DL and UL <= 40Mbps: {(under_or_eq_40 / total) * 100:.2f}%")
                print(f"  Blank asset_id: {(blank_asset / total) * 100:.2f}%")
