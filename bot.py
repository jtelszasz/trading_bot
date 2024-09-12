

import pandas as pd
import alpaca_trade_api as tradeapi
import matplotlib.pyplot as plt
import numpy as np

class TradeBot:
	"""
	This needs to:
	- initialize a broker to connect to alpaca trading
	- select a strategy 
	- call a function to determine buy/sell signal
	- call a function to execute trade


	"""
	def __init__(self, broker, strategy):
		self.broker = broker
		self.strategy = strategy


	def select_strategy:
		""" simple for now - just one strategy """


	def get_signal:
		"""
		- takes in strategy
		- get recent historical data
		- generate and return signal
		"""

	def execute_trade:
		"""
		- takes in signal
		- executes buy/sell if needed
		"""

class Strategy:
	"""Generic class for which algorithm is selected."""
	def __init__(self, name="MovingAvg"):
		self.name = name

class MovingAvgStrategy(Strategy):
	"""   """


	def __init__(self):
		super().__init__(name)



class Broker:
    def __init__(self, api_key, secret_key, base_url):
        self.api = tradeapi.REST(api_key, secret_key, base_url)

    def get_historical_data(self, symbol, start_date, end_date, timeframe):
        bars = self.api.get_bars(symbol, timeframe, start=start_date, end=end_date).df
        return bars

    def get_latest_data(self, symbol):
        latest_bar = self.api.get_bars(symbol, TimeFrame.Minute, limit=1).df
        return latest_bar

    def place_order(self, order_type, symbol, qty):
        if order_type == "buy":
            self.api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='gtc')
        elif order_type == "sell":
            self.api.submit_order(symbol=symbol, qty=qty, side='sell', type='market', time_in_force='gtc')
