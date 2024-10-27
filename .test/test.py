import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CryptoTracker:
    def __init__(self, symbol, interval='1d', days_back=60):
        self.symbol = symbol
        self.interval = interval
        self.days_back = days_back
        self.model = LinearRegression()

    def fetch_data(self):
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=self.days_back)
        data = yf.download(self.symbol, start=start_date, end=end_date, interval=self.interval)
        return data['Close']

    def train_model(self, data):
        X = np.arange(len(data)).reshape(-1, 1)
        self.model.fit(X, data.values)

    def forecast(self, data, days=7):
        future_X = np.arange(len(data), len(data) + days).reshape(-1, 1)
        return self.model.predict(future_X)

    def plot_and_analyze(self, data, forecast):
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data.values, label='Historical Price')
        
        forecast_dates = [data.index[-1] + datetime.timedelta(days=i + 1) for i in range(len(forecast))]
        plt.plot(forecast_dates, forecast, label='Forecast', linestyle='--')
        
        plt.title(f'{self.symbol} Price Forecast')
        plt.xlabel('Date')
        plt.ylabel('Price in USD')
        plt.legend()
        plt.grid()
        plt.savefig(f'{self.symbol}-FORECAST-PRICE.png')
        plt.close()
        logging.info(f"Forecast price graph saved as '{self.symbol}-FORECAST-PRICE.png.'")

        trend = "upward" if forecast[-1] > data.values[-1] else "downward"
        forecasted = f"{forecast[0].item():.2f}"
        logging.info(f"Analysis: The forecast indicates an {trend} trend in the next period.")
        logging.info(f"Predicted closing price for the next day: {forecasted} USD")
        return forecasted

    def run_analysis(self):
        data = self.fetch_data()
        self.train_model(data)
        
        forecast = self.forecast(data)
        forecasted = self.plot_and_analyze(data, forecast)
        
        logging.info("Analysis complete.")

        return forecasted

tracker = CryptoTracker(symbol="SOL-USD")
a = tracker.run_analysis()
print(a)