from flask import Flask, render_template, request
import yfinance as yf
from datetime import date
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd

app = Flask(__name__)

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

@app.route("/", methods=["GET", "POST"])
def home(): 
    if request.method == "POST":
        selected_stock = request.form["selected_stock"]
        n_years = int(request.form["n_years"])
        periods = n_years * 365

        data = load_data(selected_stock)

        training_data = data[["Date", "Close"]]
        training_data.rename(columns={
            "Date": "ds", "Close": "y"
        }, inplace=True)
        
        training_data['ds'] = pd.to_datetime(training_data['ds'], utc=True).dt.tz_localize(None)

        model = Prophet()
        model.fit(training_data)

        future = model.make_future_dataframe(periods=periods)
        predictions = model.predict(future)

        plot_data = plot_plotly(model, predictions).to_dict()

        plot_data["data"][1]["name"] = "Prediction Lower Bound"
        plot_data["data"][3]["name"] = "Prediction Upper Bound"

        return render_template("result.html", plot_data=plot_data, stock=selected_stock)
        
    stocks = {
        "Apple Inc. (AAPL)" : "AAPL",
        "Microsoft Corporation (MSFT)" : "MSFT",
        "Twitter, Inc. (TWTR)" : "TWTR",
        "Tesla, Inc. (TSLA)" : "TSLA",
        "Alphabet Inc. (GOOG)" : "GOOG", 
        "Meta Platforms, Inc. (META)" : "META"
    }

    return render_template("home.html", stocks=stocks)

@app.route('/result', methods=['POST'])
def result():
    if request.method == "POST":
        selected_stock = request.form["selected_stock"]
        n_years = int(request.form["n_years"])
        periods = n_years * 365

        data = load_data(selected_stock)

        training_data = data[["Date", "Close"]]
        training_data.rename(columns={
            "Date": "ds", "Close": "y"
        }, inplace=True)
        
        training_data['ds'] = pd.to_datetime(training_data['ds'], utc=True).dt.tz_localize(None)

        model = Prophet()
        model.fit(training_data)

        future = model.make_future_dataframe(periods=periods)
        predictions = model.predict(future)

        plot_data = plot_plotly(model, predictions).to_dict()

        plot_data["data"][1]["name"] = "Prediction Lower Bound"
        plot_data["data"][3]["name"] = "Prediction Upper Bound"
      

        return render_template("result.html", stock=selected_stock)
        
    stocks = {
        "Apple Inc. (AAPL)" : "AAPL",
        "Microsoft Corporation (MSFT)" : "MSFT",
        "Twitter, Inc. (TWTR)" : "TWTR",
        "Tesla, Inc. (TSLA)" : "TSLA",
        "Alphabet Inc. (GOOG)" : "GOOG", 
        "Meta Platforms, Inc. (META)" : "META"
    }

    return render_template("result.html", stocks=stocks)

def load_data(ticker: str) -> pd.DataFrame:
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data

def find_highest_stock_price():
    stocks = {
        "Apple Inc. (AAPL)" : "AAPL",
        "Microsoft Corporation (MSFT)" : "MSFT",
        "Twitter, Inc. (TWTR)" : "TWTR",
        "Tesla, Inc. (TSLA)" : "TSLA",
        "Alphabet Inc. (GOOG)" : "GOOG", 
        "Meta Platforms, Inc. (META)" : "META"
    }
    
    max_price = 0
    max_price_stock = None
    for stock_name, ticker in stocks.items():
        data = load_data(ticker)
        max_close = data['Close'].max()
        if max_close > max_price:
            max_price = max_close
            max_price_stock = stock_name
    return max_price_stock
 
if __name__ == "__main__":
    app.run(debug=True)
