
import pandas as pd
import alpaca_trade_api as tradeapi
import matplotlib.pyplot as plt
import numpy as np
import config
from datetime import datetime, timedelta

data_window = 3 * 365 # number of historical days of data to grab
symbol = "MSFT"
timeframe = "1D" # daily data

short_window = 4
long_window = 40

start_date = datetime.today().date() - timedelta(days=data_window)
end_date = datetime.today().date() - timedelta(days=1)

class TradeBot:
	"""
	This needs to:
	- initialize a broker to connect to alpaca trading
	- select a strategy 
	- call a function to determine buy/sell signal
	- call a function to execute trade
	"""
	print("Starting Bot")

	def __init__(self, broker, strategy):
		self.broker = broker
		self.strategy = strategy


	def select_strategy(self):
		""" simple for now - just one strategy """
		pass

	def get_signal(self):
		"""
		- takes in strategy
		- get recent historical data
		- generate and return signal
		"""
		pass
	def execute_trade(self):
		"""
		- takes in signal
		- executes buy/sell if needed
		"""
		pass

class Strategy:
	"""Generic class for which algorithm is selected."""
	#def __init__(self, stock):

	def generate_signals(stock):
		pass

class MovingAvgStrategy(Strategy):
	""" implementing simple moving average strategy """
	def __init__(self, short_window=3, long_window=28):
		self.short_window = short_window
		self.long_window = long_window

	def generate_signals(self, stock):
		stock.historical_data['closed_short'] = stock.historical_data['close'].rolling(window=self.short_window).mean().shift(1)
		stock.historical_data['closed_long'] = stock.historical_data['close'].rolling(window=self.long_window).mean().shift(1)

		stock.historical_data.dropna(subset=['close', 'closed_short', 'closed_long'], inplace=True)

		stock.historical_data['signal'] = 0
		stock.historical_data.loc[stock.historical_data['closed_short'] > stock.historical_data['closed_long'], 'signal'] = 1
		stock.historical_data.loc[stock.historical_data['closed_short'] < stock.historical_data['closed_long'], 'signal'] = -1

		stock.historical_data['signal'] = stock.historical_data['signal'].diff(1)
		return stock

class Broker:
	"""  """
	print("Initializing Broker")

	def __init__(self, api_key, secret_key, base_url):
		self.api = tradeapi.REST(api_key, secret_key, base_url)

	def get_historical_data(self, symbol, start_date, end_date, timeframe):
		print("Retrieving historical data for " + symbol)
		bars = self.api.get_bars(symbol, timeframe, start=start_date, end=end_date).df
		print("Number of records retrieved: ", str(len(bars)))
		return bars

	def get_latest_data(self, symbol, timeframe='1D'):
		print("Retrieving latest data for " + symbol)
		latest_bar = self.api.get_bars(symbol, timeframe, limit=1).df
		return latest_bar

	def place_order(self, order_type, symbol, qty):

		if order_type == "buy":
			self.api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='gtc')
		elif order_type == "sell":
			self.api.submit_order(symbol=symbol, qty=qty, side='sell', type='market', time_in_force='gtc')


class Stock:
	def __init__(self, symbol, broker):
		self.symbol = symbol
		self.latest_data = broker.get_latest_data(symbol, timeframe)
		self.historical_data = broker.get_historical_data(symbol, start_date, end_date, timeframe)

		self.historical_data['timestamp'] = pd.to_datetime(self.historical_data.index).date

		self.historical_data['close_roll_90d'] = self.historical_data['close'].rolling(window=90).mean().shift(1)
		self.historical_data['close_roll_28d'] = self.historical_data['close'].rolling(window=28).mean().shift(1)
		self.historical_data['close_roll_7d'] = self.historical_data['close'].rolling(window=7).mean().shift(1)
	
	def plot_historical_data(self):

		# Plot the time series data
		plt.figure(figsize=(12, 6))
		plt.plot(self.historical_data['timestamp'], self.historical_data['close'], label=self.symbol)
		plt.plot(self.historical_data['timestamp'], self.historical_data['close_roll_7d'], label = '7d Rolling Avg')
		plt.plot(self.historical_data['timestamp'], self.historical_data['close_roll_28d'], label = '28d Rolling Avg')
		plt.plot(self.historical_data['timestamp'], self.historical_data['close_roll_90d'], label = '90d Rolling Avg')

		# Customize the plot
		plt.title('Stock Prices: ' + self.symbol)
		plt.xlabel('Date')
		plt.ylabel('Closing Price')
		plt.legend()
		plt.grid(True)

		# Display the plot
		plt.show()

	def plot_strategy_markers(self): 
		#if signals exist, plot, else don't

		# Plot the time series data
		plt.figure(figsize=(12, 6))
		plt.plot(self.historical_data['timestamp'], self.historical_data['close'], label=self.symbol)
		
		# Add markers for buy signals
		plt.plot(self.historical_data['timestamp'][self.historical_data['signal'] == 2], self.historical_data['close'][self.historical_data['signal'] == 2], '^', markersize=10, color='green', label='Buy')
		plt.plot(self.historical_data['timestamp'][self.historical_data['signal'] == -2], self.historical_data['close'][self.historical_data['signal'] == -2], '^', markersize=10, color='red', label='Sell')

		# Customize the plot
		plt.title('Stock Price with Strategy Buy/Sell: ' + self.symbol)
		plt.xlabel('Date')
		plt.ylabel('Closing Price')
		plt.legend()
		plt.grid(True)

		# Display the plot
		plt.show()
		pass

if __name__ == "__main__":
	broker = Broker(config.API_KEY, config.API_SECRET, config.BASE_URL)
	my_stock = Stock(symbol, broker)
	my_stock = MovingAvgStrategy(short_window, long_window).generate_signals(my_stock)

	my_stock.plot_historical_data()
	my_stock.plot_strategy_markers()

	print(my_stock.historical_data.head(20))


