
import pandas as pd
import alpaca_trade_api as tradeapi
import matplotlib.pyplot as plt
import numpy as np
import config
from datetime import datetime, timedelta

data_window = 3 * 365 # number of historical days of data to grab
symbol = "MSFT"
timeframe = "1D" # daily data

qty = 1

short_window = 10
long_window = 50

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
	#print("Starting Bot")

	def __init__(self, broker, strategy):
		self.broker = broker
		self.strategy = strategy

	def run_backtest(self, strategy, stock):
		strategy.generate_backtest(stock)
		strategy.plot_returns(stock)

	def get_signal(self, stock):
		"""

		"""
		self.transaction = None
		if stock.historical_data.iloc[-1]['transaction'] == 2:
			self.transaction = "buy"
		elif stock.historical_data.iloc[-1]['transaction'] == -2:
			self.transaction = "sell"


	def execute_trade(self):
		"""
		- takes in signal
		- executes buy/sell if needed
		"""
		self.broker.place_order(self.transaction, symbol, qty)


class Strategy:
	"""Generic class for which algorithm is selected."""
	def __init__(self, stock):
		self.data = stock.historical_data

	def generate_signals(self):
		pass

	def generate_backtest(self):

		self.data['log_return'] = np.log(self.data['close']).diff()
		self.data['log_system_return'] = self.data['log_return'] * self.data['signal']

		self.buyhold_return = np.exp(self.data['log_return']).cumprod().iloc[-1] - 1
		self.system_return = np.exp(self.data['log_system_return']).cumprod().iloc[-1] - 1

	def plot_returns(self):

		# Plot the time series data
		plt.figure(figsize=(12, 6))
		plt.plot(self.data['timestamp'], np.exp(self.data['log_return']).cumprod(), label="Buy-Hold Return")
		plt.plot(self.data['timestamp'], np.exp(self.data['log_system_return']).cumprod(), label='System Return')

		# Customize the plot
		plt.title('Buy-Hold vs. System Returns: ' + self.symbol)
		plt.xlabel('Date')
		plt.ylabel('Closing Price')
		plt.legend()
		plt.grid(True)

		# Display the plot
		plt.show()


class MovingAvgStrategy(Strategy):
	""" implementing simple moving average strategy """
	def __init__(self, short_window=3, long_window=28):
		self.name = "Moving Average Crossover"
		self.short_window = short_window
		self.long_window = long_window
		self.data = None



	def generate_signals(self):
		self.data['closed_short'] = self.data['close'].rolling(window=self.short_window).mean().shift(1)
		self.data['closed_long'] = self.data['close'].rolling(window=self.long_window).mean().shift(1)

		self.data.dropna(subset=['close', 'closed_short', 'closed_long'], inplace=True)

		self.data['signal'] = 0
		self.data.loc[self.data['closed_short'] > self.data['closed_long'], 'signal'] = 1
		self.data.loc[self.data['closed_short'] < self.data['closed_long'], 'signal'] = -1

		self.data['transaction'] = self.data['signal'].diff(1)


class Stock:
	def __init__(self, symbol, broker, start_date, end_date):
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
		plt.plot(self.historical_data['timestamp'][self.historical_data['transaction'] == 2], self.historical_data['close'][self.historical_data['transaction'] == 2], '^', markersize=10, color='green', label='Buy')
		plt.plot(self.historical_data['timestamp'][self.historical_data['transaction'] == -2], self.historical_data['close'][self.historical_data['transaction'] == -2], '^', markersize=10, color='red', label='Sell')

		# Customize the plot
		plt.title('Stock Price with Strategy Buy/Sell: ' + self.symbol)
		plt.xlabel('Date')
		plt.ylabel('Closing Price')
		plt.legend()
		plt.grid(True)

		# Display the plot
		plt.show()


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
		self.api.submit_order(symbol=symbol, qty=qty, side=order_type, type='market', time_in_force='gtc')



if __name__ == "__main__":

	broker = Broker(config.API_KEY, config.API_SECRET, config.BASE_URL)
	strategy = MovingAvgStrategy(short_window, long_window)
	bot = TradeBot(broker, strategy)

	my_stock = Stock(symbol, broker, start_date, end_date)
	strategy.generate_signals()

	#my_stock.plot_historical_data()

	bot.get_signal(my_stock)
	#bot.execute_trade()
	bot.run_backtest(strategy, my_stock)

	print("Transaction: " + str(bot.transaction))
	print("Overall Buy-Hold Return: " + str(strategy.buyhold_return))
	print("Overall System Return: " + str(strategy.system_return))

	#risk

	my_stock.plot_strategy_markers()

