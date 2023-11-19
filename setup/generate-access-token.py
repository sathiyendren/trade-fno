import os
from kiteconnect import KiteConnect
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

kite = KiteConnect(api_key=API_KEY)

requestToken=open('./../configuration/request-token.txt', 'r').read()
accessToken=open('./../configuration/access-token.txt', 'r').read()

if accessToken:
    generateSession=kite.generate_session(request_token=requestToken,api_secret=API_SECRET)
    accessToken= generateSession['access_token']
    with open('./../configuration/access-token.txt', 'w') as wr:
        wr.write(accessToken)
    print(accessToken) 