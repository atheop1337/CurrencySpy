import random, string, aiohttp, logging, asyncio, datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from typing import Union
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np


class const:
    DATABASE_NAME = "database/spy.db"

class _Kbs:

    ...

class _States:

    class SetCurrency(StatesGroup):
        currency = State()

    class SetInterval(StatesGroup):
        interval = State()

    class SetThreshold(StatesGroup):
        threshold = State()

class _Messages:

    @staticmethod
    def get_welcome_message(username: str, successfully: Union[bool, int]) -> str:
        if successfully or successfully == 409:
            return(
            f"""
            <b>Добро пожаловать, {username} в Бота для мониторинга курсов валют!</b> 📈

            Этот бот поможет вам отслеживать изменения курса валют и криптовалют в режиме реального времени. Также он может присылать уведомления при значительных изменениях и делать краткий прогноз по выбранной валюте.

            <b>Команды для начала:</b>
            - <code>/set_currency</code> — выбрать валюту для отслеживания (например, USD, EUR, BTC).
            - <code>/set_interval</code> — установить интервал уведомлений (1 час, 4 часа, 24 часа).
            - <code>/get_rate</code> — узнать текущий курс выбранной валюты.
            - <code>/set_threshold</code> — установить порог изменения курса для уведомлений (например, ±5%).
            - <code>/forecast</code> — получить прогноз курса валюты на основании анализа данных.

            💬 <i>Для подробной информации используйте команды выше.</i>

            <b>Давайте начнем!</b> 👇
            Введите <code>/set_currency</code> для выбора валюты.
            """
            )
        else: 
            return(f"Произошла ошибка при занесении в базу данных, попробуйте позже")

    @staticmethod
    def get_set_currency_message() -> str:
        return (
            """
            <b>🌐 Supported Cryptocurrencies:</b>

            • <b>Bitcoin</b> (BTC)
            • <b>Ethereum</b> (ETH)
            • <b>Ripple</b> (XRP)
            • <b>Litecoin</b> (LTC)
            • <b>Bitcoin Cash</b> (BCH)
            • <b>USD Coin</b> (USDC)
            • <b>Tether</b> (USDT)
            • <b>Cardano</b> (ADA)
            • <b>Polygon</b> (MATIC)
            • <b>Solana</b> (SOL)

            <b>💱 Supported Fiat Currencies:</b>

            • US Dollar (USD)
            • Euro (EUR)
            • British Pound (GBP)

            <b> ⚛ Write me code of currency that you want to track: </b>
            """
        )

    @staticmethod
    def get_rate_message(udata: dict) -> str:
        return(f"""
            <b>Валюта: {udata["currency"]}</b>
            <b>Цена: {udata["last_rate"]}$</b>
            <i>Изменения будут отправлены каждые {udata["interval"]} секунд</i>
            <i>Порог изменения курса для уведомления: {udata["threshold"]}%</i>
            <b>Для получения цены используется coinbase</b>
        """)

    @staticmethod
    def get_set_interval_message() -> str:
        return (
            """
            <b>⚛ Enter notification interval in seconds</b>
            """
        )

    @staticmethod
    def get_set_threshold_message() -> str:
        return (
            """
            <b>⚛ Enter percentage threshold for currency price changes</b>
            """
        )


class _Methods:

    @staticmethod  
    async def get_currency_price(symbol: str) -> Union[int, None]:
        url = f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    try:
                        price = round(float(data["data"]["amount"]))
                        return int(price)
                    except (KeyError, TypeError, ValueError):
                        logging.error(f"Unexpected data format: {data}")
                        return None
                else:
                    logging.error(f"Failed to fetch price for {symbol}: {response.status}")
                    return None


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



