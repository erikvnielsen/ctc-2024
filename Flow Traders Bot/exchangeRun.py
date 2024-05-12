# This is the exchange run (the part you actually run from the terminal once all bots are loaded into the config)


import time
import importlib
import json
import threading
import matplotlib.pyplot as plt
from exchangeSimulator import Exchange
from initializer_bot import InitializerBot

def load_bot(bot_module_name):
    """Dynamically loads a bot module and returns the bot class."""
    module = importlib.import_module(bot_module_name)
    return getattr(module, 'TradingBot')  # Assumes a standardized class name -> TradingBot

    
def run_bot(bot_class, exchange, duration, symbols):
    """Function to run a bot's continuous trading loop."""
    bot_instance = bot_class(exchange, symbols)
    start_time = time.time()
    while time.time() - start_time < duration:
        bot_instance.run_trading_loop()
    
    
def run_exchange_matching(exchange, duration):
    start_time = time.time()
    """Function to continuously match orders in the exchange."""
    while time.time() - start_time < duration:
        #exchange._match_orders()
        time.sleep(.001) # There is a built in sleep otherwise this would probably crash your system

def plot_pnl(pnl_data):
    for bot_id, pnls in pnl_data.items():
        plt.plot(pnls, label = f'Bot {bot_id}')
    plt.xlabel('Time Step')
    plt.ylabel('PnL')
    plt.title('PnL Over Time')
    plt.legend()
    plt.show()
    
    
def main():    
    print("Starting market initialization...")
    
    # set the duration of the simulation in seconds
    duration = 10
    
    # define available symbols and starting prices
    symbols = ['AAPL', 'GOOG', 'MSFT', 'MAG', 'SMAG']
    initial_prices = [150.0, 2750.0, 400.0, 70.0, 70.0]
    
    exchange_instance = Exchange(symbols, initial_prices)
    init_bot = InitializerBot(exchange_instance,symbols)
    init_bot.place_orders()
    
    # Load bot configurations from a JSON file
    with open('bots_config.json', 'r') as f:
        config = json.load(f)
    
    # Start a thread for continuous order matching
    matching_thread = threading.Thread(target=run_exchange_matching, args=(exchange_instance,duration))
    matching_thread.start()
    
    
    # Creating and starting threads for each bot
    threads = []
    for bot_name in config['bots']:
        bot_class = load_bot(bot_name)
        t = threading.Thread(target=run_bot, args=(bot_class, exchange_instance, duration, symbols))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    

    
if __name__ == "__main__":
    main()