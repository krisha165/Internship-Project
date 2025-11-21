# final1.py
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

CSV_URL = "https://api.kite.trade/instruments"   # working mirror source

def get_nse_equity_symbols(url=CSV_URL):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return {"status": "error", "message": f"Unable to download CSV! Status code: {response.status_code}"}

        content = response.text.splitlines()

        if len(content) < 2:
            return {"status": "error", "message": "CSV file is empty"}

        symbol_token_map = {}

        for row in content[1:]:
            columns = row.split(",")

            if len(columns) < 12:
                continue

            instrument_token = columns[0]
            exchange = columns[11]       # exchange field
            instrument_type = columns[9] # EQ / FUT / CE / PE
            symbol = columns[2]          # symbol name

            # Filter NSE + EQ only
            if exchange == "NSE" and instrument_type == "EQ":
                symbol_token_map[symbol] = instrument_token

        if not symbol_token_map:
            return {"status": "error", "message": "No NSE EQ symbols found in CSV"}

        return {
            "status": "success",
            "count": len(symbol_token_map),
            "data": symbol_token_map
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.route("/")
def home():
    return "Flask API Server Running!"


@app.route("/task01", methods=["POST"])
def task01():
    data = request.get_json()
    url = data.get("url", CSV_URL)
    result = get_nse_equity_symbols(url)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5004)
