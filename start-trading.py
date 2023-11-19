import logging
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import os
from dotenv import load_dotenv
import pandas as pd
from openpyxl import load_workbook
import csv
from datetime import datetime
import math
from distutils.util import strtobool


load_dotenv()

DEVELOPMENT = os.getenv('DEVELOPMENT', 'FALSE').lower()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ALGO_TRADING = os.getenv('ALGO_TRADING', 'FALSE').lower()

EXCHANGE = os.getenv('EXCHANGE')
INDEX = os.getenv('INDEX')
TODAY_DATE = os.getenv('TODAY_DATE')
EXPIRY_DATE = os.getenv('EXPIRY_DATE')

CE_INSTRUMENT = int(os.getenv('CE_INSTRUMENT'))
PE_INSTRUMENT = int(os.getenv('PE_INSTRUMENT'))
INSTRUMENTS = [CE_INSTRUMENT, PE_INSTRUMENT]

CAPITAL = int(os.getenv('CAPITAL'))
STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE'))
QUANTITY_PER_LOT_SIZE = int(os.getenv('QUANTITY_PER_LOT_SIZE'))
MAXIMUM_QUANTITY_PER_TRADE_SIZE = int(os.getenv('MAXIMUM_QUANTITY_PER_TRADE_SIZE'))
MINIMUM_QUANTITY_PER_TRADE_SIZE = int(os.getenv('MINIMUM_QUANTITY_PER_TRADE_SIZE'))

# Setup the Kite API client
kite = KiteConnect(api_key=API_KEY)

ceDataArray = []
peDataArray = []

transactions = []
currentTransaction = None
currentInstrumentType = 'CE'
ceLastPrice = None
peLastPrice = None
isPreStart = True

# Read access token from file
accessToken=open('./configuration/access-token.txt', 'r').read()

# Initialise
kws = KiteTicker(api_key=API_KEY, access_token=accessToken)

# Check ALGO TRADING is on
def is_development():
    return strtobool(DEVELOPMENT)

# Check ALGO TRADING is on
def is_algo_trading_on():
    return strtobool(ALGO_TRADING)

# Writing Every tick CE and PE data to file for futher backtesting
def write_instruments_data():
    if is_development():
        with open('./output/CE_DATA.txt', 'w') as wr:
            wr.write(str(ceDataArray))
        with open('./output/PE_DATA.txt', 'w') as wr:
            wr.write(str(peDataArray))  

# Write all transactions in a excel
def write_transactions_to_excel():
    global transactions
    global currentTransaction
    transactions_excel = transactions
    if currentTransaction is not None:
        transactions_excel = transactions + [currentTransaction]
    fileName = TODAY_DATE+'_SL_'+str(STOP_LOSS_PERCENTAGE)+'.xlsx'
    transactions_dataframe = pd.DataFrame(transactions_excel)
    transactions_dataframe.to_excel("./output/"+fileName)

# Algomojo Buy REST API Call 
def algomojo_buy(transaction):
    if is_algo_trading_on():
        if transaction['pre_start'] is not True:
            print('CALL ALGOMOJO REST API')

# Algomojo Sell REST API Call 
def algomojo_sell(transaction):
    if is_algo_trading_on():
        if transaction['pre_start'] is not True:
            print('CALL ALGOMOJO REST API')

# Buy transaction
def buy_transaction():
    # datetime object containing current date and time
    now = datetime.now()
    capital = None
    quantity = None
    lastPrice = None
    transaction = None
    global currentTransaction
    global isPreStart

    if currentInstrumentType == 'CE':
        # print('BUY CE INSTRUMENT')
        lastPrice = ceLastPrice
        quantity = math.floor(CAPITAL / (QUANTITY_PER_LOT_SIZE * lastPrice)) * QUANTITY_PER_LOT_SIZE
        capital = lastPrice * quantity
        instrument = CE_INSTRUMENT
    else:
        # print('BUY PE INSTRUMENT')
        lastPrice = peLastPrice
        quantity = math.floor(CAPITAL / (QUANTITY_PER_LOT_SIZE * lastPrice)) * QUANTITY_PER_LOT_SIZE
        capital = lastPrice * quantity
        instrument = PE_INSTRUMENT

    print('Buy => '+ str(instrument) + ' ' + currentInstrumentType + ' at Rs. ' + str(lastPrice))
    transaction = {
          "instrument": instrument,
          "instrument_type": currentInstrumentType,
          "expiry_date": EXPIRY_DATE,
          "index": INDEX,
          "trade_date": TODAY_DATE,
          "capital": capital,
          "quantity": quantity,
          "buy_price": lastPrice,
          "highest_price": lastPrice,
          "lowest_price": lastPrice,
          "sell_price": 0,
          "profit": 0,
          "active": True,
          "pre_start": isPreStart,
          "last_price": lastPrice,
          "created_datetime": now.strftime("%d/%m/%Y %H:%M:%S"),
          "updated_datetime": now.strftime("%d/%m/%Y %H:%M:%S"),
          "brokerage": 0,
          "net_profit": 0
        }

    currentTransaction = transaction
    isPreStart = False
    write_transactions_to_excel()
    algomojo_buy(currentTransaction)

# Sell transaction
def sell_transaction(transaction):
    print('SELL => '+ str(transaction['instrument']) + ' at Rs. ' + str(transaction['sell_price']))
    print('\n')
    global currentTransaction
    currentTransaction['active'] = False
    write_transactions_to_excel()
    algomojo_sell(transaction)
    transactions.append(currentTransaction)
    currentTransaction = None
    global currentInstrumentType
    if currentInstrumentType == 'CE':
        currentInstrumentType = 'PE'
    else:
        currentInstrumentType = 'CE'
    on_symbol_price_change()

# Update transaction
def update_or_sell_transaction():
    global currentTransaction
    now = datetime.now()
    lastPrice = None
    if currentTransaction['instrument_type'] == 'CE':
        lastPrice = ceLastPrice
    else:
        lastPrice = peLastPrice
    currentTransaction['last_price'] = lastPrice
    highestPrice = currentTransaction['highest_price']
    if lastPrice > highestPrice:
        currentTransaction['highest_price'] = lastPrice
    lowestPrice = currentTransaction['lowest_price']
    if lastPrice < lowestPrice:
        currentTransaction['lowest_price'] = lastPrice
    buyPrice = currentTransaction['buy_price']
    quantity = currentTransaction['quantity']
    capital = currentTransaction['capital']
    profit = round(float((lastPrice - buyPrice) * quantity), 2)
    currentTransaction['profit'] = profit
    currentTransaction["updated_datetime"] = now.strftime("%d/%m/%Y %H:%M:%S")
    trailingSLCaptial = (capital * STOP_LOSS_PERCENTAGE) / 100
    SLPrice = round(float((highestPrice - trailingSLCaptial / quantity)), 2)
    normalSellCondition = (lastPrice <= SLPrice and trailingSLCaptial > 0)
    if is_development():
        print('UPDATE => '+ str(currentTransaction))
    if normalSellCondition:
        currentTransaction['sell_price'] = lastPrice
        brokerage = 0
        currentTransaction['net_profit'] = profit - brokerage
        sell_transaction(currentTransaction)
    
# On symbol price change
def on_symbol_price_change():
    if is_development():
        print('CE = ' +f'{ceLastPrice:.2f}')
        print('PE = ' +f'{peLastPrice:.2f}')
    if currentTransaction is None:
        buy_transaction()
    else:
        update_or_sell_transaction()
    write_instruments_data()

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    if is_development():
        print(ticks)
    global ceLastPrice
    global peLastPrice
    for row in ticks:
        if row['instrument_token'] == CE_INSTRUMENT:
            ceLastPrice = row['last_price']
        else:
            peLastPrice = row['last_price'] 
    ceDataArray.append(ceLastPrice)
    peDataArray.append(peLastPrice)
    on_symbol_price_change()

def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens 
    ws.subscribe(INSTRUMENTS)
    # Set instrument to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, INSTRUMENTS)

def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect()
