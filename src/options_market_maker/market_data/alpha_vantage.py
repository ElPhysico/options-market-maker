import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'
RAW_DATA_DIR = Path('/Users/kklein/Dropbox/shared/finance_projects/options-market-maker/data/raw_data/options')

def get_historical_options(symbol, date):
    """Fetches a snapshot of all options data for a given symbol on a specific
    date.

    Parameters:
        symbol (str): Stock ticker symbol (e.g. 'AAPL')
        date (str): Date in 'YYYY-MM-DD' format

    Returns:
        dict: JSON response containing all option data for the given symbol and
            date.
    """
    symbol_path = RAW_DATA_DIR / f'{symbol}'
    symbol_path.mkdir(parents=True, exist_ok=True)

    filename = symbol_path / f'{symbol}_{date}'
    
    if filename.exists():
        print(f'Loading cached data from {filename}')
        return json.loads(filename.read_text())
    
    if not ALPHA_VANTAGE_API_KEY:
        raise ValueError('API key is missing. Set it in the .env file.')
    
    params = {
        'function': 'HISTORICAL_OPTIONS',
        'symbol': symbol,
        'date': date,
        'datatype': 'json',
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    r = requests.get(BASE_URL, params)
    data = r.json()

    if data.get('message', '') != 'success':
        raise ValueError(f'Error fetching data: {data.get("message", "Unknown Error")}')

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

    return data
    