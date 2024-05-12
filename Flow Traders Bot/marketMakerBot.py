# This is an example of a silly market maker bot
# The important things to note are sticking methods inside of the tradingbot class 
# (including bot_id which should be your team name and the name of this .py for continuity)

from exchangeSimulator import Exchange, Order, OrderBook
import random
import time
from decimal import Decimal, getcontext

class TradingBot:
    def __init__(self, exchange, symbols):
        self.exchange = exchange
        self.symbols = symbols
        self.spread = 0.1  # distance from the theoretical price
        self.bot_id = 'MarketMakerBot'
        self.outstanding_orders = {symbol: [] for symbol in symbols}
        self.completed_trades = {symbol: [] for symbol in symbols}
        
    def check_trade_history(self):
        # Retrieve trade history from the exchange or order book
        my_trades = [trade for trade in self.exchange.completed_trades if trade['buy_order_id'] == self.bot_id or trade['sell_order_id'] == self.bot_id]
        return my_trades
    
    def place_order(self, symbol, order_type, quantity, price):
        order = Order(bot_id=self.bot_id, symbol=symbol, order_type=order_type, quantity=quantity, price=price)
        self.exchange.add_order(order)
        self.outstanding_orders[symbol].append(order)
                 
             
    def run_trading_loop(self):
        
        recent_trades = self.exchange.get_recent_trades_involving_bot(self.bot_id)
        #print('these are my recent_trades for the market maker bot', recent_trades)
        
        
        symbols = ['AAPL', 'GOOG', 'MSFT', 'MAG', 'SMAG']
        for symbol in symbols:
            bbo = self.exchange.get_bbo(symbol)

            # full_book = self.exchange.get_full_book(symbol)
            # print('[MM1] full book', full_book)

            # last_price = self.exchange.get_last_traded_price(symbol)
            # print('[MM1]', symbol, last_price)

            # get current orders
            my_bids, my_asks = self.exchange.get_current_orders(self.bot_id, symbol)
            print('[MM1]', my_bids, my_asks)
            
            if bbo[0] and bbo[1]:  # both bid and offer exist
                # Calculate the quantity-weighted mid price
                best_bid, best_offer = bbo
                theoretical_price = (best_bid + best_offer) / Decimal('2.0')  # Simplified for example
                
                # Evaluate Desired levels of orders
                buy_price = theoretical_price - Decimal(self.spread)
                sell_price = theoretical_price + Decimal(self.spread)
                quantity = 100  # example fixed quantity
                
                # check for existing orders
                existing_buy_orders = [order for order in self.outstanding_orders[symbol] if order.price == buy_price and order.order_type == 'buy']
                
                
                
                #handle buy order logic
                if not existing_buy_orders:
                    # Place new buy order
                    BUY_ORDER = (Order(None, self.bot_id, symbol, 'buy', quantity, buy_price))
                    self.exchange.add_order(BUY_ORDER)
                    self.outstanding_orders[symbol].append(BUY_ORDER)
                    print(f"{self.bot_id} Placed a buy order for {quantity} shares at ${buy_price:.2f} in {symbol}")
                #elif existing_buy_orders[0].quantity <= 10:  # If quantity is not correct, cancel and replace
                #    self.exchange.cancel_order(existing_buy_orders[0])
                #    self.place_order(symbol, 'buy', 100, buy_price)

                # Check if there are existing orders at desired sell price
                existing_sell_orders = [order for order in self.outstanding_orders[symbol] if order.price == sell_price and order.order_type == 'sell']
                if not existing_sell_orders:
                    # Place new sell order
                    #self.place_order(symbol, 'sell', 100, sell_price)
                    SELL_ORDER = (Order(None, self.bot_id, symbol, 'sell', quantity, sell_price))
                    self.exchange.add_order(SELL_ORDER)
                    self.outstanding_orders[symbol].append(SELL_ORDER)
                    print(f"{self.bot_id} Placed a sell order for {quantity} shares at ${sell_price:.2f} in {symbol}")
                #elif existing_sell_orders[0].quantity != 100:  # If quantity is not correct, cancel and replace
                #    self.exchange.cancel_order(existing_sell_orders[0])
                #    self.place_order(symbol, 'sell', 100, sell_price)
                
                
            
                
                
                

        time.sleep(5)  # Sleep to limit the frequency of order placements
