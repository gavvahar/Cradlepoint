import csv

input_file = "w2005-ATT-7-23-90-NAT_spdtst.csv"
output_file = "w2005-ATT-7-23-90-NAT_spdtst_reformatted.csv"


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
    fieldnames = reader.fieldnames + [
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
    for row in reader:
        asset_fields = parse_asset_id(row.get("asset_id", ""))
        row.update(asset_fields)
        writer.writerow(row)
