from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

# ---------------------------------------------------------
# COMMON FUNCTION FOR DATA DOWNLOAD + CLEAN + RESAMPLE
# ---------------------------------------------------------
def process_task2(symbol, start_date, end_date, timeframe, resample_choice=None):
    try:
        # VALIDATION
        if not all([symbol, start_date, end_date, timeframe]):
            return {"error": "All inputs are required!"}, 400

        try:
            pd.to_datetime(start_date)
            pd.to_datetime(end_date)
        except:
            return {"error": "Invalid date format! Use YYYY-MM-DD"}, 400

        # DOWNLOAD
        df = yf.download(symbol, start=start_date, end=end_date,
                         interval=timeframe, progress=False)

        if df.empty:
            return {"error": "No data found for given inputs!"}, 404

        # CLEAN DATA
        df = df.dropna()
        df.index = pd.to_datetime(df.index)
        df["date"] = df.index.date
        df["time"] = df.index.time

        df = df[["date", "time", "Open", "High", "Low", "Close", "Volume"]]
        df.columns = ["date", "time", "open", "high", "low", "close", "volume"]

        # RESAMPLING
        if resample_choice:
            df.index = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str))

            df = df.resample(resample_choice).agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }).dropna()

            df["date"] = df.index.date
            df["time"] = df.index.time
            df = df[["date", "time", "open", "high", "low", "close", "volume"]]

        # SAVE CSV
        folder = "data"
        os.makedirs(folder, exist_ok=True)

        filename = f"{symbol}_{resample_choice if resample_choice else timeframe}.csv"
        filepath = os.path.join(folder, filename)
        df.to_csv(filepath, index=False)

        # FIX JSON SERIALIZATION FOR PREVIEW
        preview = df.head().copy()
        preview["date"] = preview["date"].astype(str)
        preview["time"] = preview["time"].astype(str)

        return {
            "status": "success",
            "file_saved": filepath,
            "preview": preview.to_dict(orient="records")
        }, 200

    except Exception as e:
        return {"error": str(e)}, 500


# ---------------------------------------------------------
# POST METHOD (JSON BODY)
# ---------------------------------------------------------
@app.route("/task02/download", methods=["POST"])
def task02_post():
    body = request.get_json()

    symbol = body.get("symbol")
    start_date = body.get("start_date")
    end_date = body.get("end_date")
    timeframe = body.get("timeframe")
    resample_to = body.get("resample_to")

    return process_task2(symbol, start_date, end_date, timeframe, resample_to)


# ---------------------------------------------------------
# GET METHOD (URL PARAMS)
# ---------------------------------------------------------
@app.route("/task02/download", methods=["GET"])
def task02_get():

    symbol = request.args.get("symbol")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    timeframe = request.args.get("timeframe")
    resample_to = request.args.get("resample_to")

    return process_task2(symbol, start_date, end_date, timeframe, resample_to)


# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5005)