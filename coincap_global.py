from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from prettytable import PrettyTable
from datetime import datetime
from colorama import Fore, Back, Style, init
import config
import json

init()

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

parameters = {
    'start':'1',
    'limit':'100',
    'convert':'USD'
}

convert = parameters['convert']
url_end = '?structure=array&convert=' + convert

headers = {
    'Accepts': 'application.json',
    'X-CMC_PRO_API_KEY': config.coin_marketcap_api_key
}

session = Session()
session.headers.update(headers)


def format_number(value, places, type):
    if type == 'non_percent':   
        formatted_value =  '{:,}'.format(round(value, places))
        return formatted_value
    else:
        if value <= 0:
            formatted_value = Back.RED + str(value) + '%' + Style.RESET_ALL
        else:
            formatted_value = Back.GREEN + str(value) + '%' + Style.RESET_ALL
        return formatted_value

def add_table_row(table, name, symbol, amount, value, price, hour_change, day_change, week_change):
    table.add_row([name + ' (' + symbol + ')',
                            str(amount),
                            '$' + str(format_number(value, 2, 'non_percent')),
                            '$' + str(format_number(price, 2, 'non_percent')),
                            str(format_number(hour_change, 3, 'percent')),
                            str(format_number(day_change, 3, 'percent')),
                            str(format_number(week_change, 3, 'percent'))])
    return table

try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    data = data['data']


    ticker_url_pairs = {}
    for currency in data:
        id = currency ['id']
        symbol = currency['symbol']
        ticker_url_pairs[symbol] = id

    print()
    print("MY PORTFOLIO")
    print()

    portfolio_value = 0.00
    last_updated = 0

    table = PrettyTable(['Asset', 'Amount Owned', convert + ' Value', 'Price', '1h', '24h', '7d'])

    with open("portfolio.txt") as input:
        for line in input:
            ticker, amount = line.split()
            ticker = ticker.upper()

            ticker_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id='+ str(ticker_url_pairs[ticker])

            request = session.get(ticker_url)
            results = request.json()

            currency = results['data'][str(ticker_url_pairs[ticker])]
            id = currency['id']
            name = currency['name']
            last_updated = currency['last_updated']
            symbol = currency['symbol']
            quotes = currency['quote'][convert]
            hour_change = round(quotes['percent_change_1h'],1)
            day_change = round(quotes['percent_change_24h'],1)
            week_change = round(quotes['percent_change_7d'],1)
            price = quotes['price']

            value = float(price) * float(amount)

            portfolio_value += value

            table = add_table_row(table, name, symbol, amount, value, price, hour_change, day_change, week_change)
            
    print(table)
    print()
    
    portfolio_value_string = '{:,}'.format(round(portfolio_value,2))
    date = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ")
    print("Total Portfolio Value: " + portfolio_value_string)
    print("Last Updated: " + str(date))
    
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
