# This is the initializer bot to populate the exchange with orders before any other bots place orders

from exchangeSimulator import Exchange, Order, OrderBook
import random
from decimal import Decimal, getcontext

class InitializerBot:
    def __init__(self, exchange, symbols):
        self.exchange = exchange
        self.symbols = symbols
        self.bot_id = 'Initializer'

    def place_orders(self):
        print('Sending Initial Orders to the exchange')
        # This method will create and place a series of initializing orders on the exchange
        symbols = ['AAPL', 'GOOG', 'MSFT', 'MAG', 'SMAG']
        # AAPL price = 150
        # GOOG price = 2750
        # MSFT price = 400
        # MAG price = 70
        # SMAG price = 70
        
        
        for symbol in symbols:
            last_price = self.exchange.get_last_traded_price(symbol)
            
            for _ in range(100):  # Create 100 initial orders per symbol
                
                # buy orders
                order_type = 'BUY'
                quantity = random.randint(1, 100) * 100
                
                buy_price = round(last_price  * (Decimal('1.0')-(Decimal(random.randint(1, 500)/1000.0))),2)
                
            
                order = Order(None, bot_id=self.bot_id, symbol=symbol, order_type='BUY', quantity=quantity, price=buy_price)
                self.exchange.add_order(order)
                #print(f"{self.bot_id} Placed a buy order for {quantity} shares at ${buy_price:.2f} in {symbol}")
                
                
                # sell orders
                order_type = 'SELL'
                quantity = random.randint(1, 100) * 100
                sell_price = round(last_price  * (Decimal('1.0')+ Decimal((random.randint(1, 500)/1000.0))),2)
                order = Order(None, bot_id=self.bot_id, symbol=symbol, order_type='SELL', quantity=quantity, price=sell_price)
                self.exchange.add_order(order)
                #print(f"{self.bot_id} Placed a SELL order for {quantity} shares at ${sell_price:.2f} in {symbol}")


