#To exract Binance Prices
#pip install websocket-client
#pip install websocket-client==1.2.0
#pip install lodash-py
#pip install shared_memory_dict
import pymongo
from datetime import datetime
from shared_memory_dict import SharedMemoryDict
import websocket
import json
import time
import requests
from urllib.request import urlopen
import numpy as np
import gc
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# List of pairs and product IDs
ourpairs = [
    "ETH/USDT", "BTC/USDT", "ETH/BTC", "LTC/USDT", "LTC/BTC",
    "LTC/USD", "BCH/USDT", "BTC/USD", "ETH/USD", "BCH/BTC",
    "XRP/USDT", "BNB/USDT", "USDC/USDT", "FIL/USDT", "SOL/USDT",
    "LDO/USDT", "ARB/USDT", "UNI/USDT", "MATIC/USDT", "ATOM/USDT",
    "SHIB/USDT", "DOGE/USDT", "TRX/USDT", "ADA/USDT", "GRT/USDT",
    "AVAX/USDT", "AAVE/USDT", "XLM/USDT", "ALGO/USDT", "ETC/USDT",
    "LINK/USDT", "NEAR/USDT", "DOT/USDT", "WBTC/USDT", "DAI/USDT",
    "UNIQ/USD", "BCH/USD"
]

productids = [
    "ETH-USDT", "BTC-USDT", "ETH-BTC", "LTC-USDT", "LTC-BTC",
    "LTC-USD", "BCH-USDT", "BTC-USD", "ETH-USD", "BCH-BTC",
    "XRP-USDT", "BNB-USDT", "USDC-USDT", "FIL-USDT", "SOL-USDT",
    "LDO-USDT", "ARB-USDT", "UNI-USDT", "MATIC-USDT", "ATOM-USDT",
    "SHIB-USDT", "DOGE-USDT", "TRX-USDT", "ADA-USDT", "GRT-USDT",
    "AVAX-USDT", "AAVE-USDT", "XLM-USDT", "ALGO-USDT", "ETC-USDT",
    "LINK-USDT", "NEAR-USDT", "DOT-USDT", "WBTC-USDT", "DAI-USDT",
    "UNIQ-USD", "BCH-USD"
]

# Initialize price_array
price_array = [['' for _ in range(5)] for _ in range(len(ourpairs))]
for i, pair in enumerate(ourpairs):
    price_array[i][0] = pair

# Convert price_array to a NumPy array
np_price_array = np.array(price_array)

# Initialize SharedMemoryDict
smd_prices = SharedMemoryDict(name='price_array', size=8192)

# WebSocket subscription message
subscribe_msg = {
    'type': 'subscribe',
    'channels': [
        {
            'name': 'ticker',
            'product_ids': productids,
        },
    ],
}
messtext = 'This is a test message for coinbase WebSocket'
    send_the_mail()


# Define callback functions for WebSocket events
def on_open(ws):
    print('WebSocket connection coinbase opened - Please do not close this window or kill this process')
    wsapp.send(json.dumps(subscribe_msg))

def on_message(wsapp, message):
    coinbase_data = json.loads(message)
    if coinbase_data['product_id'] in productids:
        product_id_with_slash = coinbase_data['product_id'].replace('-', '/')
        where_in_array = list(zip(*np.where(np_price_array == product_id_with_slash)))
        for value in where_in_array:
            the_row = value[0]
        price_array[the_row][1] = coinbase_data['price']
        price_array[the_row][2] = coinbase_data['best_ask']
        price_array[the_row][3] = coinbase_data['best_bid']

    smd_prices["coinbase_feed"] = price_array
    gc.collect()
    messtext = 'This is a test message for WebSocket'
    send_the_mail()

def send_the_mail():
    global messtext, mess_subject
    receiver = "madhana@kappsoft.com"
    message = MIMEMultipart()
    message['From'] = "deepika@kappsoft.com"
    message['To'] = receiver
    message['Subject'] =  "Test websocket"
    sender = "deepika@gmail.com"
    empassword = "Deepik@2117"
    message.attach(MIMEText(messtext, 'plain'))
    smtp_done = False
    starttls_done = False
    login_done = False
    sendmail_done = False
    try:
        mailsession = smtplib.SMTP('smtp.gmail.com', 587, timeout=360)
        smtp_done = True
    except Exception as e:
        print(f"SMTP connection error: {e}")

    if smtp_done:
        try:
            mailsession.starttls()
            starttls_done = True
        except Exception as e:
            print(f"StartTLS error: {e}")

    if starttls_done:
        try:
            mailsession.login(sender, empassword)
            login_done = True
        except Exception as e:
            print(f"Login error: {e}")

    if login_done:
        text = message.as_string()
        try:
            mailsession.sendmail(sender, receiver, text)
            sendmail_done = True
        except Exception as e:
            print(f"Sendmail error: {e}")
    
    if sendmail_done:
        mailsession.quit()

if __name__ == "__main__":
    wsapp = websocket.WebSocketApp('wss://ws-feed.exchange.coinbase.com', on_open=on_open, on_message=on_message)
    wsapp.run_forever()

'''
{'type': 'ticker', 'sequence': 9015199026, 'product_id': 'BTC-USDT', 'price': '26479.15', 'open_24h': '28621.5', 
'volume_24h': '3525.43370625', 'low_24h': '25122.13', 'high_24h': '28633.94', 'volume_30d': '36903.98242331', 
'best_bid': '26479.15', 'best_bid_size': '0.00000405', 'best_ask': '26479.71', 'best_ask_size': '0.09280000', 
'side': 'sell', 'time': '2023-08-18T07:40:05.768672Z', 'trade_id': 14728449, 'last_size': '0.05666'}
'''

