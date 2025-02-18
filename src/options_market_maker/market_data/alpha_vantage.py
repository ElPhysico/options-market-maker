import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime


load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'
RAW_DATA_DIR = Path('/Users/kklein/Dropbox/shared/finance_projects/options-market-maker/data/raw_data/')
SAMPLE_DATA_DIR = Path('/Users/kklein/Dropbox/shared/finance_projects/options-market-maker/data/samples/')

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
    symbol_path = RAW_DATA_DIR / f'options/{symbol}'
    symbol_path.mkdir(parents=True, exist_ok=True)

    filename = symbol_path / f'{symbol}_{date}.json'
    
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


def get_daily_time_series_stocks(symbol, outputsize='full'):
    """Fetches a daily time series for a given symbol.

    Parameters:
        symbol (str): Stock ticker symbol (e.g. 'AAPL')
        outputsize (str): 'full' or 'compact' for only last 100 days

    Returns:
        dict: JSON response containing the time series for the symbol.
    """
    path = RAW_DATA_DIR / f'stocks/'
    path.mkdir(parents=True, exist_ok=True)

    filename = path / f'{symbol}.json'

    if filename.exists():
        print(f'Loading cached data from {filename}')
        return json.loads(filename.read_text())
    
    if outputsize not in ['full', 'compact']:
        raise ValueError('outputsize needs to be either "full" or "compact".')

    if not ALPHA_VANTAGE_API_KEY:
        raise ValueError('API key is missing. Set it in the .env file.')
    
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': outputsize,
        'datatype': 'json',
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    r = requests.get(BASE_URL, params)
    data = r.json()

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

    return data


def extract_sample_market_data(symbol, date):
    """Processes raw data into a sample format that can be used with other
    functions.

    Parameters:
        symbol (str): Stock ticker symbol (e.g. 'AAPL')
        date (str): Date in 'YYYY-MM-DD' format

    Returns:
        dict: JSON response containing the option data in sample format.
    """
    symbol_path = SAMPLE_DATA_DIR / f'options/{symbol}'
    symbol_path.mkdir(parents=True, exist_ok=True)

    filename = symbol_path / f'{symbol}_{date}.json'

    data = get_historical_options(symbol, date)
    ts = get_daily_time_series_stocks(symbol, 'full')

    samples = {
        'symbol': symbol,
        'date': date,
        'symbol_open': float(ts['Time Series (Daily)'][date]['1. open']),
        'symbol_close': float(ts['Time Series (Daily)'][date]['4. close']),
        'ncalls': 0,
        'nputs': 0,
        'calls': [],
        'puts': []
    }

    for option in data['data']:
        t_date = datetime.strptime(date, '%Y-%m-%d')
        T_expiry_date = datetime.strptime(option['expiration'], '%Y-%m-%d')
        T = (T_expiry_date - t_date).days / 365.0

        sample = {
            'expiration': option['expiration'],
            'time-to-expiry': T,
            'strike': float(option['strike']),
            'bid': float(option['bid']),
            'ask': float(option['ask']),
            'implied_volatility': float(option['implied_volatility']),
            'Delta': float(option['delta']),
            'Gamma': float(option['gamma']),
            'Theta': float(option['theta']),
            'Vega': float(option['vega']),
            'Rho': float(option['rho'])
        }
        if option['type'] == 'call':
            samples['ncalls'] += 1
            samples['calls'].append(sample)
        elif option['type'] == 'put':
            samples['nputs'] += 1
            samples['puts'].append(sample)

    with open(filename, 'w') as file:
        json.dump(samples, file, indent=4)

    return samples