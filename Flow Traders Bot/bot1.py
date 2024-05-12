# This simple TradingBot is meant to represent one of the bots that you will be interacting with on the final simulation
# This bot is quite naive in the way that it interacts with the market, you may be met with similar bots and or bots that behave smarter...
import random
import time
from exchangeSimulator import Exchange, Order, OrderBook
from decimal import Decimal, getcontext

class TradingBot:

    def __init__(self, exchange, symbols):
        """Initialize the bot with an instance of the Exchange.
        """
        self.exchange = exchange
        self.symbols = symbols
        self.orders_placed = []  # Track all orders placed to manage them later
        self.bot_id = 'bot1'
        
        
    def place_order(self, symbol, order_type, quantity, price):
        order = Order(bot_id=self.bot_id, symbol=symbol, order_type=order_type, quantity=quantity, price=price)
        self.exchange.add_order(order)
        self.outstanding_orders[symbol].append(order)
        
    def on_trade_completion(self, trade):
        self.completed_trades[trade['symbol']].append(trade)
        # Potentially update or remove the matched orders from outstanding_orders
        # Example: Remove the executed order (simplistic and may need more logic)
        orders = self.outstanding_orders[trade['symbol']]
        self.outstanding_orders[trade['symbol']] = [order for order in orders if order.order_id != trade['order_id']]
        
    def run_trading_loop(self):
        print('trying to run bot1')
        
        # get my trade history
        trade_history = self.exchange.get_trade_history(self.bot_id)
        print('[Bot1] my trade history:', trade_history)

        #recent_trades = self.exchange.get_recent_trades_involving_bot(self.bot_id)
        # print('[BOT1] these are my recent_trades for bot1', recent_trades)
        
        symbols = ['AAPL', 'GOOG', 'MSFT', 'MAG', 'SMAG']
        for symbol in symbols:
            last_price = self.exchange.get_last_traded_price('AAPL')
            
            bbo = self.exchange.get_bbo(symbol)
            best_bid, best_offer = bbo
            
            if last_price is not None:
                # Create a random order around the last traded price
                order_type = random.choice(['buy', 'sell'])
                quantity = random.randint(1, 10) * 10
                # Randomize price to be within +/- 10% of the last traded price
                if order_type == 'buy':
                    price_variation = Decimal(random.uniform(0, 0.1)) * Decimal(last_price)
                else:
                    price_variation = Decimal(random.uniform(-0.1, 0)) * Decimal(last_price)
                price = round(last_price + price_variation,2)

                order = Order(None, self.bot_id, symbol, order_type, quantity, price)
                self.exchange.add_order(order)
                print(str(time.ctime(time.time())), f"Bot 1 Placed {order_type} order for {quantity} shares at ${price:.2f} in {symbol}")
            
            else:
                order_type = 'BUY'
                quantity = 100
                price = Decimal(round(best_offer,2))
                order = Order(None, self.bot_id, symbol, order_type, quantity, price)
                self.exchange.add_order(order)
                print(str(time.ctime(time.time())), f"bot1 Placed {order_type} order for {quantity} shares at ${price:.2f} in {symbol}")

        time.sleep(1)  # Sleep to prevent overwhelming the exchange -> only needed for example bots
        

