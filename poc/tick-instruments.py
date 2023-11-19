import logging
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import os
from dotenv import load_dotenv
import pandas as pd
from openpyxl import load_workbook
import csv

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
CE_INSTRUMENT = int(os.getenv('CE_INSTRUMENT'))
PE_INSTRUMENT = int(os.getenv('PE_INSTRUMENT'))
INSTRUMENTS = [CE_INSTRUMENT, PE_INSTRUMENT]
kite = KiteConnect(api_key=API_KEY)


class StockData(object):
    def __init__(self, token, ltp):
        self.token = token
        self.ltp = ltp

ceDataArray = []
peDataArray = []
print(CE_INSTRUMENT)
accessToken=open('./../configuration/access-token.txt', 'r').read()

# Initialise
kws = KiteTicker(api_key=API_KEY, access_token=accessToken)

#load excel file
workbook = load_workbook(filename="./../output/tick-ltp.xlsx")
 
#open workbook
sheet = workbook.active
 
 #modify the desired cell
# sheet["A1"] = "Full Name"
 
# #save the file
# workbook.save(filename="./tick-ltp.xlsx")

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    # logging.debug("Ticks: {}".format(ticks))
    # print(ticks)
    for row in ticks:
        if row['instrument_token'] == CE_INSTRUMENT:
            # row['instrument_type'] = 'C'
            sheet["C2"] = row['last_price']
            instrument_token = row['instrument_token']
            last_price = row['last_price']
            ceDataArray.append(last_price)
        else:
            # row['instrument_type'] = 'P'
            sheet["C3"] = row['last_price']
            instrument_token = row['instrument_token']
            last_price = row['last_price']
            peDataArray.append(last_price)
    #save the file
    workbook.save(filename="./tick-ltp.xlsx")
    print(ceDataArray)
    print(peDataArray)
    # ticks_dataframe = pd.DataFrame(ticks, columns=['instrument_token', 'last_price', 'lot_size', 'instrument_type'])
    # ticks_dataframe.index = ticks_dataframe.index+1
    # ticks_dataframe.to_excel("./tick-ltp.xlsx", index=True)

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
