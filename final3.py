from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# ------------------------------
# Manual SMA calculation
# ------------------------------
def calculate_sma(df, column, window):
    sma_values = []
    for i in range(len(df)):
        if i + 1 < window:
            sma_values.append(None)
        else:
            total = sum(df.loc[i - window + 1:i, column])
            sma_values.append(round(total / window, 4))
    return sma_values

# ------------------------------
# Core logic
# ------------------------------
def process_sma(df, column, window, rows=3):
    if column not in df.columns:
        return {"status":"error","message":f"Column '{column}' not found"}

    df['SMA'] = calculate_sma(df, column, window)
    # Keep only required columns
    df_result = df[['Date', column, 'SMA']].tail(rows)
    # Convert Date to string for JSON
    df_result['Date'] = df_result['Date'].astype(str)
    return df_result

# ------------------------------
# GET method example
# ------------------------------
@app.route("/sma_task2", methods=['GET'])
def sma_task2_get():
    window = int(request.args.get("window", 5))
    column = request.args.get("column", "Close")
    rows = int(request.args.get("rows", 3))

    # Sample data
    data = {
        'Date': pd.date_range(start='2025-11-01', periods=10, freq='D'),
        'Close': [100,102,101,105,107,110,108,111,115,117]
    }
    df = pd.DataFrame(data)

    result_df = process_sma(df, column, window, rows)
    return jsonify(result_df.to_dict(orient='records'))

# ------------------------------
# POST method example
# ------------------------------
@app.route("/sma_task2", methods=['POST'])
def sma_task2_post():
    data = request.get_json()
    if not data:
        return jsonify({"status":"error","message":"JSON body required"}), 400

    window = int(data.get("window", 5))
    column = data.get("column", "Close")
    rows = int(data.get("rows", 3))
    data_list = data.get("data")

    if not data_list:
        return jsonify({"status":"error","message":"Data list required"}), 400

    df = pd.DataFrame(data_list)
    if 'Date' not in df.columns:
        return jsonify({"status":"error","message":"Date column missing"}), 400

    result_df = process_sma(df, column, window, rows)
    return jsonify(result_df.to_dict(orient='records'))

# ------------------------------
# Run Flask
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True,port=5006)
