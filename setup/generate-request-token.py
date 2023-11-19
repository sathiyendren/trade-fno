import webbrowser
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
# To get request token login to
KITE_LOGIN_ENDPOINT = "https://kite.zerodha.com/connect/login?v=3&api_key="+API_KEY

webbrowser.open(KITE_LOGIN_ENDPOINT, new=0, autoraise=True)