from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
EXCHANGE = os.getenv('EXCHANGE')
SELECTED_INDEX = os.getenv('INDEX')
EXPIRY_DATE= str(os.getenv('EXPIRY_DATE'))

kite = KiteConnect(api_key=API_KEY)

requestToken=open('./../configuration/request-token.txt', 'r').read()
accessToken=open('./../configuration/access-token.txt', 'r').read()

instruments = kite.instruments(EXCHANGE)
instruments_dataframe = pd.DataFrame(instruments)
instruments_dataframe = instruments_dataframe.loc[(instruments_dataframe['name'] == SELECTED_INDEX)]
# instruments_dataframe = instruments_dataframe.loc[(instruments_dataframe['expiry'].isin(EXPIRY_DATE))]
instruments_dataframe.to_excel("./../output/instruments.xlsx")
# print(instruments_dataframe)
