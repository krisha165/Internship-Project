Description Of All Task:-

Task 01: Symbol-Token Mapping
Steps:
 1.	Download CSV from https://api.kite.trade/instruments
 2.	Read file line by line
 3.	Filter rows where:
  o	exchange = "NSE"
  o	instrument_type = "EQ"
 4.	Extract tradingsymbol and instrument_token
 5.	Build dictionary: {symbol: token}
How it works:
 1.	Download - Get CSV directly from URL
 2.	Parse Headers - Find column positions
 3.	Filter - Keep only NSE+EQ instruments
 4.	Extract - Get symbol & token values
 5.	Build Dict - Create {symbol: token} mapping

Task 02: Stock Data Download
Steps:
 1.	Input: symbol, start_date, end_date, timeframe
 2.	Download 1m data using yfinance
 3.	Clean: Keep OHLCV, remove NaN
 4.	Resample using:
  o	Open: first
  o	High: max
  o Low: min
  o	Close: last
  o	Volume: sum
 5.	Save as {symbol}_{timeframe}.csv
How it Works:
Input: Symbol, Dates, Timeframe
Process:
 1.	Download 1m data
 2.	Clean → keep OHLCV
 3.	Resample → first, max, min, last, sum
 4.	Export CSV

Task 3: SMA Calculation
Steps:
 1.	Input: List of [date, close]
 2.	Sort by date
 3.	For each day, calculate average of last 5 closes
 4.	Return dates with SMA values
How it works:
 •	Uses sliding window of 5 days
 •	Manual average calculation
 •	Starts output from 5th day

Task:06 Intraday P&L analysis for SBIN stock
Steps:
 1.	Download 5-minute data for 7 days
 2.	Filter last 5 trading days
 3.	For each day:
  o	Entry: First candle after 09:30
  o	Exit: Last candle before 15:00
  o	P&L = Exit - Entry
 4.	Calculate totals and averages
How it works:
 •	Buys at 09:30, sells at 15:00 daily
 •	Tracks profit/loss for each day
 •	Shows daily P&L and summary statistics

Final Task 1: 
/task01/symbol-token-map 
Methods: GET, POST
•	Description: 
Reads the instruments CSV file (from JSON body) and returns a Symbol → Token mapping for all NSE Equity (EQ) instruments.

Final Task2:
Endpoint: /task02/download
Methods: GET, POST
•	Purpose:
Downloads stock data from Yahoo Finance, cleans it, optionally resamples it (1m → 5m, 15m, 1h, etc.), and saves the result as a CSV.

Final Task 3:
/task03/sma
TASK 03 – SMA (Simple Moving Average) API Documentation
Methods: GET, POST
•	Description
This API calculates a 3-day Simple Moving Average (SMA-3) based on a list of dates and corresponding closing prices.

Final Task 4:
GET http://127.0.0.1:5000/hello
•	Description:
Simple test API.
Used to check if Flask server is running.
Returns a static message.

POST http://127.0.0.1:5000/hello_post
•	Description
Accepts a JSON body containing a "name" key.
Returns a greeting message using the provided name. 
    
Final Task 5: 
/api/expiry (GET & POST)
•	Purpose
Returns weekly, monthly, or both expiry dates based on a given date.












