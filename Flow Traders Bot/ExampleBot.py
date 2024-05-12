# This is an example bot

import random
import time
from decimal import Decimal, getcontext
from exchangeSimulator import Exchange, Order, OrderBook

# code must all live inside the same TradingBot classname
class TradingBot:
    """Example Trading Bot for Trading Simulation Competition.
    
    This bot demonstrates how to interact with the Exchange by placing and cancelling orders.
    Follow this template to ensure compatibility with the simulation framework.
    """

    def __init__(self, exchange, symbols):
        """Initialize the bot with an instance of the Exchange.
        """
        self.exchange = exchange
        self.symbols = symbols
        self.bot_id = 'ExampleBot'
        self.orders_placed = []  # Track all orders placed to manage them later
        
        self.outstanding_orders = {symbol: [] for symbol in symbols}
        self.completed_trades = {symbol: [] for symbol in symbols}
        

    def place_orders(self):
        symbols = ['AAPL', 'GOOG', 'MSFT', 'MAG', 'SMAG']
        for _ in range(5):  # Create and place 5 orders
            order_type = 'buy' if random.choice([True, False]) else 'sell'
            symbol = random.choice(symbols)
            quantity = random.randint(1, 10) * 10
            price = Decimal(random.randint(100, 200))
            bot_id = self.bot_id
            order = Order(bot_id, symbol, order_type, quantity, price)
            self.exchange.add_order(order)  # Order ID is assigned by the exchange

    def observe_market(self):
        """Method to observe BBO and the order book."""
        symbol = 'AAPL'
        bbo = self.exchange.get_bbo(symbol)
        full_book = self.exchange.get_order_book(symbol)
        # These print statements are to help you get familiar with the structure of the exchange
        # Please do not leave print or debug messages in your final code
        print(f"BBO for {symbol}: {bbo}")
        print(f"Full Book for {symbol}: {full_book}")

    def cancel_order(self, order):
        """Cancels an order that was placed on the exchange.
        This method demonstrates how to cancel orders from the exchange.
        """
        self.exchange.cancel_order(order)

    # This must be the function that runs all of your code as this is what will be called by the exchange
    def run_trading_loop(self):
        """Runs a continuous trading loop that reacts to market conditions. - do not need to stick code inside a while loop"""
        print('ExampleBot is running')
        time.sleep(1)  # Sleep to prevent overwhelming the exchange -> only needed for example bots
        
            # Implement your trading logic

            # Place Orders
            # self.place_orders(market_data)

            # Cancel Old Orders
            # self.cancel_order(market_data)

        
# The bot class and methods provided are examples.
# Participants should modify this template to develop their own trading strategies.