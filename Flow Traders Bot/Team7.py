# This is an erikBot bot

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
        self.bot_id = 'Team7'

        self.marketMakeBids = {}
        self.marketMakeAsks = {}
    
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
        
        # Cancel all old outstanding orders
        ''' for order in self.cancelOrders:
            self.exchange.cancel_order(order)
        
        self.cancelOrders.clear() ''' 
        symbols = ['AAPL', 'GOOG', 'MSFT', 'MAG', 'SMAG']

        ''' if(not self.first):
            for symbol in symbols: 
                currbuyOrders, currsellOrders = self.exchange.get_current_orders(self.bot_id, symbol)
                # buy_orders.append([order.order_id, order.symbol, order.order_type, order.quantity, order.price, order.added_time])
                # Order(None, self.bot_id, 'SMAG', 'sell', 100, SMAGbbo[1]) 
                for order in currbuyOrders:
                    self.exchange.cancel_order(Order(order))
                for order in currsellOrders:
                    self.exchange.cancel_order(order)
        else:
            self.first = False '''

        desiredSpread = Decimal('0.01')
        desiredQuantity = 1000

        # indices will be set to one if an entire order has been filled so we don't accidentally cancel an order that has been filled
        # AAPL = 0 GOOG = 2 MSFT = 4 MAG = 6 SMAG = 8 (INDEXES) The BUY is on the even and SELL on the odd
        # currOrders = [0,0,0,0,0,0,0,0,0,0]
        # Value of 1 indicates an order has been filled so there is no need to cancel it

    

        MAGbbo = self.exchange.get_bbo('MAG') # best bid and best offer in a vector (0 is bid and 1 is offer)
        SMAGbbo = self.exchange.get_bbo('SMAG')
        AAPLbbo = self.exchange.get_bbo('AAPL')
        GOOGbbo = self.exchange.get_bbo('GOOG')
        MSFTbbo = self.exchange.get_bbo('MSFT')

        stocksBidTotal = (300 * AAPLbbo[0]) + (20 * GOOGbbo[0]) + (100 * MSFTbbo[0])
        stocksAskTotal = (300 * AAPLbbo[1]) + (20 * GOOGbbo[1]) + (100 * MSFTbbo[1])

        # MAGTotal = 2000 * MAGtheoPrice
        MAGBuyTotal = 2000 * MAGbbo[0]
        MAGSellTotal = 2000 *  MAGbbo[1]

        # MAG ETF ARBITRAGE
        if(stocksAskTotal < MAGBuyTotal): 
            SELL_ORDER = (Order(None, self.bot_id, 'MAG', 'sell', 2000, MAGbbo[1]))
            self.exchange.add_order(SELL_ORDER)

            APPL_BUY = (Order(None, self.bot_id, 'AAPL', 'buy', 300, AAPLbbo[0]))
            GOOG_BUY = (Order(None, self.bot_id, 'GOOG', 'buy', 20, GOOGbbo[0]))
            MSFT_BUY = (Order(None, self.bot_id, 'MSFT', 'buy', 100, MSFTbbo[0]))

            self.exchange.add_order(APPL_BUY)
            self.exchange.add_order(GOOG_BUY)
            self.exchange.add_order(MSFT_BUY)

        elif(stocksBidTotal > MAGSellTotal):
            BUY_ORDER = (Order(None, self.bot_id, 'MAG', 'buy', 2000, MAGbbo[0]))
            self.exchange.add_order(BUY_ORDER)

            APPL_SELL = (Order(None, self.bot_id, 'AAPL', 'sell', 300, AAPLbbo[1]))
            GOOG_SELL = (Order(None, self.bot_id, 'GOOG', 'sell', 20, GOOGbbo[1]))
            MSFT_SELL = (Order(None, self.bot_id, 'MSFT', 'sell', 100, MSFTbbo[1]))

            self.exchange.add_order(APPL_SELL)
            self.exchange.add_order(GOOG_SELL)
            self.exchange.add_order(MSFT_SELL)


        MAGbbo = self.exchange.get_bbo('MAG') # best bid and best offer in a vector (0 is bid and 1 is offer)
        SMAGbbo = self.exchange.get_bbo('SMAG')
        AAPLbbo = self.exchange.get_bbo('AAPL')
        GOOGbbo = self.exchange.get_bbo('GOOG')
        MSFTbbo = self.exchange.get_bbo('MSFT')

        # STOCK MARKET MAKING
        stockList = [['AAPL', AAPLbbo], ['GOOG', GOOGbbo], ['MSFT', MSFTbbo], ['MAG', MAGbbo]]
        for i in range(4):
            stock = stockList[i]
            buyPrice = stock[1][0] + desiredSpread
            sellPrice = stock[1][1] - desiredSpread
            if buyPrice < sellPrice:
                BUY_ORDER = (Order(None, self.bot_id, stock[0], 'buy', desiredQuantity, buyPrice))
                SELL_ORDER = (Order(None, self.bot_id, stock[0], 'sell', desiredQuantity, sellPrice))

                self.exchange.add_order(BUY_ORDER)
                self.exchange.add_order(SELL_ORDER)

                if stock[0] in self.marketMakeBids:
                    prevBuy = self.marketMakeBids[stock[0]]

                    if prevBuy.price in self.exchange.order_books[stock[0]].buy_levels:
                        self.exchange.cancel_order(prevBuy)

                if stock[0] in self.marketMakeAsks:
                    prevSell = self.marketMakeAsks[stock[0]]

                    if prevSell.price in self.exchange.order_books[stock[0]].sell_levels:
                        self.exchange.cancel_order(prevSell)

                self.marketMakeBids[stock[0]] = BUY_ORDER
                self.marketMakeAsks[stock[0]] = SELL_ORDER

        