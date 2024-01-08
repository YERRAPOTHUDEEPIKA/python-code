#pip install shared_memory_dict
from shared_memory_dict import SharedMemoryDict
import time
from time import sleep

#smd_config = SharedMemoryDict(name='config', size=1024)
smd_prices = SharedMemoryDict(name='price_array', size=1024)

if __name__ == "__main__":
    while True:
    	print('binance feed:',smd_prices["binance_feed"])
    	print('kraken feed :',smd_prices["kraken_feed"])
    	sleep(1)