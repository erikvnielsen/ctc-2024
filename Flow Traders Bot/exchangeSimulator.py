import random
import time
import datetime
import matplotlib.pyplot as plt
import threading
import multiprocessing
import weakref
import itertools
import json
import pandas as pd
from threading import Lock
import threading
import logging
from decimal import Decimal, getcontext
getcontext().prec = 6
from sortedcontainers import SortedDict

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# This is the exchange matching engin logic, each bot should be able to access the functions within the Exchange class
# If things feel foreign feel free to add print or debug statments (some examples of those have been kept here)

class Order:
    def __init__(self, order_id, bot_id, symbol, order_type, quantity, price=None):
        self.order_id = order_id
        self.bot_id = bot_id
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.price = Decimal(price).quantize(Decimal('0.01'))
        self.added_time = datetime.datetime.now()

    def change_quantity(self, executed_quantity):
        self.quantity -= executed_quantity
    
    def get_quantity(self):
        return self.quantity

class PriceLevel:
    def __init__(self, price):
        self.price = price
        self.total_quantity = 0
        self.orders = []  # List to maintain time priority

    def add_order(self, order):
        self.orders.append(order)
        self.total_quantity += order.quantity

    def remove_order(self, order):
        if order in self.orders:
            self.orders.remove(order)
            self.total_quantity -= order.quantity

    def modify_total_quantity(self, executed_quantity):
        self.total_quantity -= executed_quantity

    def get_order_array_length(self):
        return len(self.orders)

    def get_order(self):
        return self.orders[0]

class OrderBook:
    def __init__(self, initial_price):
        
        self.buy_levels = SortedDict(lambda x: -x)
        self.sell_levels = SortedDict()
        self.last_price = initial_price
        self.completed_trades = []
        self.subscribers = []
        self.lock = threading.RLock()
        logging.debug("OrderBook initialized")

    
    
    
    def add_order(self, order):
        if (order.price * 10000) % 100 != 0.0:
            raise ValueError(f"Order price {order.price} does not adhere to the tick size of 0.01")
            print('rejecting an order for invalid price ')
            
        #logging.debug(f"Attempting to acquire lock to add order: {order}")
        print('attempting to add an order from ' +str(order.bot_id) + ' to ' +str(order.order_type)+ ' ' +str(order.quantity) + ' at a price of ' + str(order.price)+ ' in '+ str(order.symbol))
        with self.lock:
            #logging.debug(f"Lock acquired for adding order: {order}")
            levels = self.buy_levels if order.order_type.lower() == 'buy' else self.sell_levels
            if order.price not in levels:
                levels[order.price] = PriceLevel(order.price)
            levels[order.price].add_order(order)

    def update_last_price(self, executed_price):
        self.last_price = executed_price
        
    def exchange_modify_order(self, order, executed_quantity):
        with self.lock:
            levels = self.buy_levels if order.order_type.lower() == 'buy' else self.sell_levels
            print('[EXCH] getting global resting order quantity: ',levels[order.price].get_order().get_quantity())
            levels[order.price].get_order().change_quantity(executed_quantity)
            levels[order.price].modify_total_quantity(executed_quantity)
                
            
            

    def cancel_order(self, order):
        if order.order_type == 'buy':
            self.buy_levels[order.price].remove_order(order)
            if self.buy_levels[order.price].get_order_array_length() == 0:
                self.buy_levels.pop(order.price)
            
        elif order.order_type == 'sell':
            self.sell_levels[order.price].remove_order(order)
            if self.sell_levels[order.price].get_order_array_length() == 0:
                self.sell_levels.pop(order.price)
    
        
    def get_best_bid(self):
        if self.buy_levels:
            best_bid_price = self.buy_levels.peekitem(0)[0]
            return best_bid_price, self.buy_levels[best_bid_price].total_quantity
        return None, None

    def get_best_ask(self):
        if self.sell_levels:
            best_ask_price = self.sell_levels.peekitem(0)[0]
            return best_ask_price, self.sell_levels[best_ask_price].total_quantity
        return None, None
    
    
    def get_bbo(self):
        """Retrieve the best bid and offer from the order book."""
        
        best_bid, best_bid_quantity = self.get_best_bid() or (None, None)
        best_offer, best_offer_quantity = self.get_best_ask() or (None, None)
        # print('[EXCH]',best_bid, best_bid_quantity, best_offer, best_offer_quantity)
        return best_bid, best_offer

    def get_full_book(self):
        """Return a snapshot of the full order book."""
        return {'bids': [(self.buy_levels[level].price, self.buy_levels[level].total_quantity) for level in list(self.buy_levels.keys())],
                'offers': [(self.sell_levels[level].price, self.sell_levels[level].total_quantity) for level in list(self.sell_levels.keys())]}
                
    def get_last_traded_price(self):
        return self.last_price
        

class Exchange:
    def __init__(self, symbols, initial_prices):
        with open('config.json', 'r') as f:
            config = json.load(f)
        self.order_books = {symbol: OrderBook(price) for symbol, price in config.items()}
        
        self.order_id_counter = itertools.count(1000)  # Start order IDs at 1000
        
        self.trade_history = []

        self.exchange_lock = Lock()

    def add_order(self, order):
        order.order_id = next(self.order_id_counter)
        print('[EXCH] trying to add an order from', order.bot_id, ' to ', order.order_type, order.quantity, ' in ', order.symbol, ' at ', order.price)
        executed_trade, remaining_order = self._match_orders(order, self.order_books[order.symbol])
        if remaining_order.quantity > 0:
            self.order_books[remaining_order.symbol].add_order(remaining_order)


    def cancel_order(self, order):
        if order.symbol in self.order_books:
            self.order_books[order.symbol].cancel_order(order)
    
    def exchange_modify_order(self, order, executed_quantity):
        self.order_books[order.symbol].exchange_modify_order(order, executed_quantity)

    def _match_orders(self, order, book):

        with book.lock:
            BBO = self.get_bbo(order.symbol)
            print('The BBO for '+str(order.symbol) + ' is', BBO)
            while book.buy_levels or book.sell_levels:
        
                if order.order_type.lower() == "buy" and len(book.sell_levels) < 1:
                    return None, order
                    
                if order.order_type.lower() == "sell" and len(book.buy_levels) < 1:
                    return None, order
                
                try:
                    best_bid_price = book.buy_levels.peekitem(0)[0]
                except:
                    print('no buy levels in the book')
                
                try:
                    best_ask_price = book.sell_levels.peekitem(0)[0]
                except:
                    print('no ask levels in the book')
                
                
                ## check if order crosses bbo/any levels
                if (order.order_type.lower() == "buy" and order.price >= best_ask_price) or (order.order_type.lower() == "sell" and order.price <= best_bid_price):
                    
                    buy_level = book.buy_levels[best_bid_price]
                    sell_level = book.sell_levels[best_ask_price]
                    
                    buy_order = buy_level.orders[0]
                    sell_order = sell_level.orders[0]
                    
                    # check for self trade prevention
                    if order.order_type.lower =="buy":
                        # check against resting sells
                        if sell_order.bot_it == order.bot_id:
                            # cancel sell_order
                            book.lock.release()
                            self.cancel_order(sell_order)
                            book.lock.acquire()
                            continue
                            
                    elif order.order_type.lower == "sell":
                        if buy_order.bot_id == order.bot_id:
                            book.lock.release()
                            self.cancel_order(buy_order)
                            book.lock.acquire()
                            continue
                            # cancel buy_order
                        
                    
                    # Handle Order Matching
                    resting_order =  sell_order if order.order_type.lower() == "buy" else buy_order
                    executed_price = resting_order.price
                    resting_order_qty = resting_order.quantity
                    print('executed_price', executed_price)
                    
                    executed_quantity = min(resting_order_qty, order.quantity)
                    print('executed quantity: ', executed_quantity)

                    
                    # Record Trades and update last price
                    book.update_last_price(executed_price)
                    
                    current_time = datetime.datetime.now()
                    # record resting trade
                    self.trade_history.append([current_time, resting_order.bot_id, resting_order.symbol, resting_order.order_type, executed_quantity, executed_price])
                    
                    # record aggressing trade
                    self.trade_history.append([current_time, order.bot_id, order.symbol, order.order_type, executed_quantity, executed_price])
                    
                    
                    # modify resting quantity
                    self.exchange_modify_order(resting_order, executed_quantity)

                    # modify order quantity
                    book.lock.release()
                    order.quantity -= executed_quantity
                    book.lock.acquire()
                    
                    if resting_order.quantity == 0:
                        book.lock.release()
                        self.cancel_order(resting_order)
                        book.lock.acquire()
                        continue
                        
                    # matching should stop after the newest orders quantity gets to 0
                    if order.quantity == 0:
                        
                        break
                    
                    

                    if resting_order.quantity == 0 and order.quantity == 0:
                        break

                else:
                    return None, order
                    break
            return None, order
                
                
               
    
    def get_symbols(self):
        # Provide a method to safely access available symbols - this is not totally necessary since in this simulation all symbols are known
        return list(self.order_books.keys())
        
    def get_current_orders(self, bot_id, symbol):
        # This is a function to pass in your own bot_id and a symbol and return your existing orders in the orderbook
        if symbol in self.order_books:
            buy_orders = []
            for price_level_object in self.order_books[symbol].buy_levels.values():
                for order in price_level_object.orders:
                    if order.bot_id == bot_id:
                        buy_orders.append([order.order_id, order.symbol, order.order_type, order.quantity, order.price, order.added_time])

            sell_orders = []
            for price_level_object in self.order_books[symbol].sell_levels.values():
                for order in price_level_object.orders:
                    if order.bot_id == bot_id:
                        sell_orders.append([order.order_id, order.symbol, order.order_type, order.quantity, order.price, order.added_time])
                          
        return buy_orders, sell_orders
    
        
    def get_bbo(self, symbol):
        with self.exchange_lock:
            """Returns the Best Bid and Offer for a given symbol."""
            if symbol in self.order_books:
                return self.order_books[symbol].get_bbo()
            return None

    def get_full_book(self, symbol):
        with self.exchange_lock:
            """Returns the full order book for a given symbol."""
            if symbol in self.order_books:
                return self.order_books[symbol].get_full_book()
            return None

    def get_last_traded_price(self, symbol):
        with self.exchange_lock:
            """Returns the last traded price for a specific symbol."""
            if symbol in self.order_books:
                #return D(self.order_books[symbol].get_last_traded_price()),2)
                last_price = self.order_books[symbol].last_price
                return Decimal(last_price) if last_price is not None else None
            else:
                return None
                    
    
    def get_recent_trades_involving_bot(self, bot_id, num_trades=10):
        """Get recent trades involving a specific bot."""
        columns = ['timestamp', 'bot_id', 'symbol', 'side', 'quantity', 'execution_price']
        trades_df = pd.DataFrame(self.trade_history, columns=columns)
        returnable_trades_df = trades_df[trades_df['bot_id']==bot_id].copy()
            
        return returnable_trades_df.head(num_trades)
        
    def get_trade_history(self, bot_id):
        columns = ['timestamp', 'bot_id', 'symbol', 'side', 'quantity', 'execution_price']
        trades_df = pd.DataFrame(self.trade_history, columns=columns)
        returnable_trades_df = trades_df[trades_df['bot_id']==bot_id].copy()
        

        return returnable_trades_df
    
        
        
