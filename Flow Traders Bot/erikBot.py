# This is an example bot

import random
import time
import math
from decimal import Decimal, getcontext
from exchangeSimulator import Exchange, Order, OrderBook

# code must all live inside the same TradingBot classname
class TradingBot:
    
    def __init__(self, exchange, symbols):
        """Initialize the bot with an instance of the Exchange.
        """
        self.exchange = exchange
        self.symbols = symbols
        self.bot_id = 'ErikBot'

        # GOAL SET INITIAL BUY/SELL TO TIGHTEST SPREAD POSSIBLE TO GET ALL THE JUICY PRICES
        # AAPL = 0 GOOG = 1 MSFT = 2 MAG = 3 SMAG = 4 (INDEXES)
        # Track all orders placed to manage them later
        # Change Initial Orders Later Maybe
        self.orders_placed = [[Order(None, self.bot_id, 'AAPL', 'buy', 100, 149.99),Order(None, self.bot_id, 'AAPL', 'sell', 100, 150.01)], 
                              [Order(None, self.bot_id, 'GOOG', 'buy', 100, 2749.99),Order(None, self.bot_id, 'GOOG', 'sell', 100, 2750.01)],
                              [Order(None, self.bot_id, 'MSFT', 'buy', 100, 399.99),Order(None, self.bot_id, 'MSFT', 'sell', 100, 400.01)],
                              [Order(None, self.bot_id, 'MAG', 'buy', 100, 69.99),Order(None, self.bot_id, 'MAG', 'sell', 100, 70.01)],
                              [Order(None, self.bot_id, 'SMAG', 'buy', 100, 69.99),Order(None, self.bot_id, 'SMAG', 'sell', 100, 70.01)]]  
        # First Index is that for current buy order, second index for current sell order for each asset
        
        # Used to place initial orders quicker than other teams
        self.first = True
        
        # self.AAPLorders = [Order(None, self.bot_id, 'AAPL', 'buy', 0),Order(None, self.bot_id, 'AAPL', 'sell', 100000)] 
        # self.GOOGorders = [Order(None, self.bot_id, 'GOOG', 'buy', 0),Order(None, self.bot_id, 'GOOG', 'sell', 100000)] 
        # self.MSFTorders = [Order(None, self.bot_id, 'MSFT', 'buy', 0),Order(None, self.bot_id, 'MSFT', 'sell', 100000)] 
        # self.MAGorders = [Order(None, self.bot_id, 'MAG', 'buy', 0),Order(None, self.bot_id, 'MAG', 'sell', 100000)] 
        # self.SMAGorders = [Order(None, self.bot_id, 'SMAG', 'buy', 0),Order(None, self.bot_id, 'SMAG', 'sell', 100000)] 
        
        self.outstanding_orders = {symbol: [] for symbol in symbols}
        self.completed_trades = {symbol: [] for symbol in symbols}
    
    def place_orders(self, order):
        self.exchange.add_order(order)


    def cancel_order(self, order):
        """Cancels an order that was placed on the exchange.
        This method demonstrates how to cancel orders from the exchange.
        """
        self.exchange.cancel_order(order)

    def run_trading_loop(self):

        # INTIAL PRICES
        # AAPL price = 150
        # GOOG price = 2750
        # MSFT price = 400
        # MAG price = 70
        # SMAG price = 70

        symbols = ['AAPL', 'GOOG', 'MSFT', 'MAG', 'SMAG']
        desiredSpread = Decimal('0.02')
        desiredQuantity = 1000

        # indices will be set to one if an entire order has been filled so we don't accidentally cancel an order that has been filled
        # AAPL = 0 GOOG = 2 MSFT = 4 MAG = 6 SMAG = 8 (INDEXES) The BUY is on the even and SELL on the odd
        currOrders = [1,1,1,1,1,1,1,1,1,1]
        # Value of 1 indicates an order has been filled so there is no need to cancel it

        if(not self.first):
            for i in range(0,10,2):
                buy_order, sell_order = self.exchange.get_current_orders(self.bot_id,symbols[math.floor(i/2)])
                if(len(buy_order) != 1):
                    currOrders[i] = 1
                else:
                    currOrders[i] = 0
                if(len(sell_order) != 1):
                    currOrders[i+1] = 1
                else:
                    currOrders[i+1] = 0
        else:
            self.first = False
        
        # if(self.first):
            # self.first = False
            # Place Initial Orders
            # for entry in self.orders_placed:
                # self.exchange.add_order(entry[0])
                # self.exchange.add_order(entry[1])

        MAGbbo = self.exchange.get_bbo('MAG') # best bid and best offer in a vector (0 is bid and 1 is offer)
        SMAGbbo = self.exchange.get_bbo('SMAG')
        AAPLbbo = self.exchange.get_bbo('AAPL')
        GOOGbbo = self.exchange.get_bbo('GOOG')
        MSFTbbo = self.exchange.get_bbo('MSFT')

        MAGtheoPrice = (MAGbbo[0] + MAGbbo[1]) / Decimal('2.0')
        SMAGtheoPrice = (SMAGbbo[0] + SMAGbbo[1]) / Decimal('2.0')
        AAPLtheoPrice = (AAPLbbo[0] + AAPLbbo[1]) / Decimal('2.0')
        GOOGtheoPrice = (GOOGbbo[0] + GOOGbbo[1]) / Decimal('2.0')
        MSFTtheoPrice = (MSFTbbo[0] + MSFTbbo[1]) / Decimal('2.0')

        stocksTotal = (300 * AAPLtheoPrice) + (20 * GOOGtheoPrice) + (100 * MSFTtheoPrice)
        MAGTotal = 2000 * MAGtheoPrice
        SMAGTotal = 2000 * SMAGtheoPrice

        # MAG ETF ARBITRAGE
        if(stocksTotal < MAGTotal): 
            price = MAGbbo[0]+desiredSpread
            if(price < MAGtheoPrice):
                BUY_ORDER = (Order(None, self.bot_id, 'MAG', 'buy', desiredQuantity, price))
                self.exchange.add_order(BUY_ORDER)
                if(currOrders[6] == 0):
                    self.exchange.cancel_order(self.orders_placed[3][0])
                    # self.etf_last_order[0] = 0
                self.orders_placed[3][0] = BUY_ORDER
        else:
            price = MAGbbo[1]-desiredSpread
            if(price > MAGtheoPrice):
                SELL_ORDER = (Order(None, self.bot_id, 'MAG', 'sell', desiredQuantity, price))
                self.exchange.add_order(SELL_ORDER)
                if(currOrders[7] == 0):
                    self.exchange.cancel_order(self.orders_placed[3][1])
                    # self.etf_last_order[0] = 1
                self.orders_placed[3][1] = SELL_ORDER

        # SMAG ETF ARBITRAGE
        if(stocksTotal < SMAGTotal):
            price = SMAGbbo[1]-desiredSpread
            if(price < SMAGtheoPrice):
                SELL_ORDER = (Order(None, self.bot_id, 'SMAG', 'sell', desiredQuantity, price))
                self.exchange.add_order(SELL_ORDER)
                if(currOrders[8] == 0):
                    self.exchange.cancel_order(self.orders_placed[4][1])
                    # self.etf_last_order[0] = 1
                self.orders_placed[4][1] = SELL_ORDER
        else:
            price = SMAGbbo[0]+desiredSpread
            if(price > SMAGtheoPrice):
                BUY_ORDER = (Order(None, self.bot_id, 'SMAG', 'buy', desiredQuantity, price))
                self.exchange.add_order(BUY_ORDER)
                if(currOrders[9] == 0):
                    self.exchange.cancel_order(self.orders_placed[4][0])
                    # self.etf_last_order[0] = 0
                self.orders_placed[4][0] = BUY_ORDER

        # STOCK MARKET MAKING
        stockList = [['AAPL', AAPLtheoPrice, AAPLbbo], ['GOOG', GOOGtheoPrice, GOOGbbo], ['MSFT', MSFTtheoPrice, MSFTbbo]]
        for i in range(3):
            stock = stockList[i]
            buyPrice = stock[2][0] + desiredSpread
            sellPrice = stock[2][1] - desiredSpread
            if(buyPrice < stock[1]):
                BUY_ORDER = (Order(None, self.bot_id, stock[0], 'buy', desiredQuantity, buyPrice))
                self.exchange.add_order(BUY_ORDER)
                if(currOrders[i*2] == 0):
                    self.exchange.cancel_order(self.orders_placed[i][0])
                self.orders_placed[i][0] = BUY_ORDER
            if(sellPrice > stock[1]):
                SELL_ORDER = (Order(None, self.bot_id, stock[0], 'sell', desiredQuantity, sellPrice))
                self.exchange.add_order(SELL_ORDER)
                if(currOrders[(i*2)+1] == 0):
                    self.exchange.cancel_order(self.orders_placed[i][1])
                self.orders_placed[i][1] = SELL_ORDER

        