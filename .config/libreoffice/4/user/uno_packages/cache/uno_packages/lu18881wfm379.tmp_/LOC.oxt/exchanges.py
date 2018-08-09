# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017 Igor Kroitor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# -----------------------------------------------------------------------------

# Python 2 & 3
import base64
import json
import hashlib
import math

# -----------------------------------------------------------------------------

from errors import ExchangeNotAvailable
from errors import DDoSProtection
from errors import ExchangeError
from errors import NotSupported
from errors import AuthenticationError
from errors import InsufficientFunds
from errors import InvalidOrder    # noqa: F401
from errors import OrderNotFound   # noqa: F401
from errors import OrderNotCached  # noqa: F401

# -----------------------------------------------------------------------------

from exchange import Exchange

# -----------------------------------------------------------------------------

exchanges = [
    '_1broker',
    '_1btcxe',
    'acx',
    'allcoin',
    'anxpro',
    'binance',
    'bit2c',
    'bitbay',
    'bitcoincoid',
    'bitfinex',
    'bitfinex2',
    'bitflyer',
    'bithumb',
    'bitlish',
    'bitmarket',
    'bitmex',
    'bitso',
    'bitstamp1',
    'bitstamp',
    'bittrex',
    'bl3p',
    'bleutrade',
    'btcbox',
    'btcchina',
    'btcexchange',
    'btcmarkets',
    'btctradeua',
    'btcturk',
    'btcx',
    'bter',
    'bxinth',
    'ccex',
    'cex',
    'chbtc',
    'chilebit',
    'coincheck',
    'coinfloor',
    'coingi',
    'coinmarketcap',
    'coinmate',
    'coinsecure',
    'coinspot',
    'cryptopia',
    'dsx',
    'exmo',
    'flowbtc',
    'foxbit',
    'fybse',
    'fybsg',
    'gatecoin',
    'gateio',
    'gdax',
    'gemini',
    'hitbtc',
    'hitbtc2',
    'huobi',
    'huobicny',
    'huobipro',
    'independentreserve',
    'itbit',
    'jubi',
    'kraken',
    'kuna',
    'lakebtc',
    'livecoin',
    'liqui',
    'luno',
    'mercado',
    'mixcoins',
    'nova',
    'okcoincny',
    'okcoinusd',
    'okex',
    'paymium',
    'poloniex',
    'quadrigacx',
    'qryptos',
    'quoine',
    'southxchange',
    'surbitcoin',
    'tidex',
    'therock',
    'urdubit',
    'vaultoro',
    'vbtc',
    'virwox',
    'wex',
    'xbtce',
    'yobit',
    'yunbi',
    'zaif',
]

# -----------------------------------------------------------------------------

__all__ = exchanges + [
    'exchanges',
]

# =============================================================================


class _1broker (Exchange):

    def __init__(self, config={}):
        params = {
            'id': '_1broker',
            'name': '1Broker',
            'countries': 'US',
            'rateLimit': 1500,
            'version': 'v2',
            'hasPublicAPI': False,
            'hasCORS': True,
            'hasFetchTrades': False,
            'hasFetchOHLCV': True,
            'timeframes': {
                '1m': '60',
                '15m': '900',
                '1h': '3600',
                '1d': '86400',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766021-420bd9fc-5ecb-11e7-8ed6-56d0081efed2.jpg',
                'api': 'https://1broker.com/api',
                'www': 'https://1broker.com',
                'doc': 'https://1broker.com/?c=en/content/api-documentation',
            },
            'api': {
                'private': {
                    'get': [
                        'market/bars',
                        'market/categories',
                        'market/details',
                        'market/list',
                        'market/quotes',
                        'market/ticks',
                        'order/cancel',
                        'order/create',
                        'order/open',
                        'position/close',
                        'position/close_cancel',
                        'position/edit',
                        'position/history',
                        'position/open',
                        'position/shared/get',
                        'social/profile_statistics',
                        'social/profile_trades',
                        'user/bitcoin_deposit_address',
                        'user/details',
                        'user/overview',
                        'user/quota_status',
                        'user/transaction_log',
                    ],
                },
            },
        }
        params.update(config)
        super(_1broker, self).__init__(params)

    def fetchCategories(self):
        response = self.privateGetMarketCategories()
        # they return an empty string among their categories, wtf?
        categories = response['response']
        result = []
        for i in range(0, len(categories)):
            if categories[i]:
                result.append(categories[i])
        return result

    def fetch_markets(self):
        self_ = self  # workaround for Babel bug(not passing `self` to _recursive() call)
        categories = self.fetchCategories()
        result = []
        for c in range(0, len(categories)):
            category = categories[c]
            markets = self_.privateGetMarketList({
                'category': category.lower(),
            })
            for p in range(0, len(markets['response'])):
                market = markets['response'][p]
                id = market['symbol']
                symbol = None
                base = None
                quote = None
                if (category == 'FOREX') or (category == 'CRYPTO'):
                    symbol = market['name']
                    parts = symbol.split('/')
                    base = parts[0]
                    quote = parts[1]
                else:
                    base = id
                    quote = 'USD'
                    symbol = base + '/' + quote
                base = self_.common_currency_code(base)
                quote = self_.common_currency_code(quote)
                result.append({
                    'id': id,
                    'symbol': symbol,
                    'base': base,
                    'quote': quote,
                    'info': market,
                })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balance = self.privateGetUserOverview()
        response = balance['response']
        result = {
            'info': response,
        }
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            result[currency] = self.account()
        total = float(response['balance'])
        result['BTC']['free'] = total
        result['BTC']['total'] = total
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        response = self.privateGetMarketQuotes(self.extend({
            'symbols': self.market_id(symbol),
        }, params))
        orderbook = response['response'][0]
        timestamp = self.parse8601(orderbook['updated'])
        bidPrice = float(orderbook['bid'])
        askPrice = float(orderbook['ask'])
        bid = [bidPrice, None]
        ask = [askPrice, None]
        return {
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'bids': [bid],
            'asks': [ask],
        }

    def fetch_trades(self, symbol):
        raise ExchangeError(self.id + ' fetchTrades() method not implemented yet')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        result = self.privateGetMarketBars(self.extend({
            'symbol': self.market_id(symbol),
            'resolution': 60,
            'limit': 1,
        }, params))
        orderbook = self.fetch_order_book(symbol)
        ticker = result['response'][0]
        timestamp = self.parse8601(ticker['date'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['h']),
            'low': float(ticker['l']),
            'bid': orderbook['bids'][0][0],
            'ask': orderbook['asks'][0][0],
            'vwap': None,
            'open': float(ticker['o']),
            'close': float(ticker['c']),
            'first': None,
            'last': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': None,
        }

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            self.parse8601(ohlcv['date']),
            float(ohlcv['o']),
            float(ohlcv['h']),
            float(ohlcv['l']),
            float(ohlcv['c']),
            None,
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'resolution': self.timeframes[timeframe],
        }
        if since:
            request['date_start'] = self.iso8601(since)  # they also support date_end
        if limit:
            request['limit'] = limit
        result = self.privateGetMarketBars(self.extend(request, params))
        return self.parse_ohlcvs(result['response'], market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'symbol': self.market_id(symbol),
            'margin': amount,
            'direction': 'short' if (side == 'sell') else 'long',
            'leverage': 1,
            'type': side,
        }
        if type == 'limit':
            order['price'] = price
        else:
            order['type'] += '_market'
        result = self.privateGetOrderCreate(self.extend(order, params))
        return {
            'info': result,
            'id': result['response']['order_id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostOrderCancel({'order_id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        if not self.apiKey:
            raise AuthenticationError(self.id + ' requires apiKey for all requests')
        url = self.urls['api'] + '/' + self.version + '/' + path + '.php'
        query = self.extend({'token': self.apiKey}, params)
        url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'warning' in response:
            if response['warning']:
                raise ExchangeError(self.id + ' ' + self.json(response))
        if 'error' in response:
            if response['error']:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class cryptocapital (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'cryptocapital',
            'name': 'Crypto Capital',
            'comment': 'Crypto Capital API',
            'countries': 'PA',  # Panama
            'hasFetchOHLCV': True,
            'hasWithdraw': True,
            'timeframes': {
                '1d': '1year',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27993158-7a13f140-64ac-11e7-89cc-a3b441f0b0f8.jpg',
                'www': 'https://cryptocapital.co',
                'doc': 'https://github.com/cryptocap',
            },
            'api': {
                'public': {
                    'get': [
                        'stats',
                        'historical-prices',
                        'order-book',
                        'transactions',
                    ],
                },
                'private': {
                    'post': [
                        'balances-and-info',
                        'open-orders',
                        'user-transactions',
                        'btc-deposit-address/get',
                        'btc-deposit-address/new',
                        'deposits/get',
                        'withdrawals/get',
                        'orders/new',
                        'orders/edit',
                        'orders/cancel',
                        'orders/status',
                        'withdrawals/new',
                    ],
                },
            },
        }
        params.update(config)
        super(cryptocapital, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privatePostBalancesAndInfo()
        balance = response['balances-and-info']
        result = {'info': balance}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            account['free'] = self.safe_float(balance['available'], currency, 0.0)
            account['used'] = self.safe_float(balance['on_hold'], currency, 0.0)
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        response = self.publicGetOrderBook(self.extend({
            'currency': self.market_id(symbol),
        }, params))
        return self.parse_order_book(response['order-book'], None, 'bid', 'ask', 'price', 'order_amount')

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetStats(self.extend({
            'currency': self.market_id(symbol),
        }, params))
        ticker = response['stats']
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['max']),
            'low': float(ticker['min']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['last_price']),
            'change': float(ticker['daily_change']),
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['total_btc_traded']),
        }

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1d', since=None, limit=None):
        return [
            self.parse8601(ohlcv['date'] + ' 00:00:00'),
            None,
            None,
            None,
            float(ohlcv['price']),
            None,
        ]

    def fetch_ohlcv(self, symbol, timeframe='1d', since=None, limit=None, params={}):
        market = self.market(symbol)
        response = self.publicGetHistoricalPrices(self.extend({
            'currency': market['id'],
            'timeframe': self.timeframes[timeframe],
        }, params))
        ohlcvs = self.omit(response['historical-prices'], 'request_currency')
        return self.parse_ohlcvs(ohlcvs, market, timeframe, since, limit)

    def parse_trade(self, trade, market):
        timestamp = int(trade['timestamp']) * 1000
        return {
            'id': trade['id'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': None,
            'type': None,
            'side': trade['maker_type'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTransactions(self.extend({
            'currency': market['id'],
        }, params))
        trades = self.omit(response['transactions'], 'request_currency')
        return self.parse_trades(trades, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        order = {
            'side': side,
            'type': type,
            'currency': self.market_id(symbol),
            'amount': amount,
        }
        if type == 'limit':
            order['limit_price'] = price
        result = self.privatePostOrdersNew(self.extend(order, params))
        return {
            'info': result,
            'id': result,
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostOrdersCancel({'id': id})

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        response = self.privatePostWithdrawalsNew(self.extend({
            'currency': currency,
            'amount': float(amount),
            'address': address,
        }, params))
        return {
            'info': response,
            'id': response['result']['uuid'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        if self.id == 'cryptocapital':
            raise ExchangeError(self.id + ' is an abstract base API for _1btcxe')
        url = self.urls['api'] + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            query = self.extend({
                'api_key': self.apiKey,
                'nonce': self.nonce(),
            }, params)
            request = self.json(query)
            query['signature'] = self.hmac(self.encode(request), self.encode(self.secret))
            body = self.json(query)
            headers = {'Content-Type': 'application/json'}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'errors' in response:
            errors = []
            for e in range(0, len(response['errors'])):
                error = response['errors'][e]
                errors.append(error['code'] + ': ' + error['message'])
            errors = ' '.join(errors)
            raise ExchangeError(self.id + ' ' + errors)
        return response

# -----------------------------------------------------------------------------


class _1btcxe (cryptocapital):

    def __init__(self, config={}):
        params = {
            'id': '_1btcxe',
            'name': '1BTCXE',
            'countries': 'PA',  # Panama
            'comment': 'Crypto Capital API',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766049-2b294408-5ecc-11e7-85cc-adaff013dc1a.jpg',
                'api': 'https://1btcxe.com/api',
                'www': 'https://1btcxe.com',
                'doc': 'https://1btcxe.com/api-docs.php',
            },
            'markets': {
                'BTC/USD': {'id': 'USD', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'BTC/EUR': {'id': 'EUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                'BTC/CNY': {'id': 'CNY', 'symbol': 'BTC/CNY', 'base': 'BTC', 'quote': 'CNY'},
                'BTC/RUB': {'id': 'RUB', 'symbol': 'BTC/RUB', 'base': 'BTC', 'quote': 'RUB'},
                'BTC/CHF': {'id': 'CHF', 'symbol': 'BTC/CHF', 'base': 'BTC', 'quote': 'CHF'},
                'BTC/JPY': {'id': 'JPY', 'symbol': 'BTC/JPY', 'base': 'BTC', 'quote': 'JPY'},
                'BTC/GBP': {'id': 'GBP', 'symbol': 'BTC/GBP', 'base': 'BTC', 'quote': 'GBP'},
                'BTC/CAD': {'id': 'CAD', 'symbol': 'BTC/CAD', 'base': 'BTC', 'quote': 'CAD'},
                'BTC/AUD': {'id': 'AUD', 'symbol': 'BTC/AUD', 'base': 'BTC', 'quote': 'AUD'},
                'BTC/AED': {'id': 'AED', 'symbol': 'BTC/AED', 'base': 'BTC', 'quote': 'AED'},
                'BTC/BGN': {'id': 'BGN', 'symbol': 'BTC/BGN', 'base': 'BTC', 'quote': 'BGN'},
                'BTC/CZK': {'id': 'CZK', 'symbol': 'BTC/CZK', 'base': 'BTC', 'quote': 'CZK'},
                'BTC/DKK': {'id': 'DKK', 'symbol': 'BTC/DKK', 'base': 'BTC', 'quote': 'DKK'},
                'BTC/HKD': {'id': 'HKD', 'symbol': 'BTC/HKD', 'base': 'BTC', 'quote': 'HKD'},
                'BTC/HRK': {'id': 'HRK', 'symbol': 'BTC/HRK', 'base': 'BTC', 'quote': 'HRK'},
                'BTC/HUF': {'id': 'HUF', 'symbol': 'BTC/HUF', 'base': 'BTC', 'quote': 'HUF'},
                'BTC/ILS': {'id': 'ILS', 'symbol': 'BTC/ILS', 'base': 'BTC', 'quote': 'ILS'},
                'BTC/INR': {'id': 'INR', 'symbol': 'BTC/INR', 'base': 'BTC', 'quote': 'INR'},
                'BTC/MUR': {'id': 'MUR', 'symbol': 'BTC/MUR', 'base': 'BTC', 'quote': 'MUR'},
                'BTC/MXN': {'id': 'MXN', 'symbol': 'BTC/MXN', 'base': 'BTC', 'quote': 'MXN'},
                'BTC/NOK': {'id': 'NOK', 'symbol': 'BTC/NOK', 'base': 'BTC', 'quote': 'NOK'},
                'BTC/NZD': {'id': 'NZD', 'symbol': 'BTC/NZD', 'base': 'BTC', 'quote': 'NZD'},
                'BTC/PLN': {'id': 'PLN', 'symbol': 'BTC/PLN', 'base': 'BTC', 'quote': 'PLN'},
                'BTC/RON': {'id': 'RON', 'symbol': 'BTC/RON', 'base': 'BTC', 'quote': 'RON'},
                'BTC/SEK': {'id': 'SEK', 'symbol': 'BTC/SEK', 'base': 'BTC', 'quote': 'SEK'},
                'BTC/SGD': {'id': 'SGD', 'symbol': 'BTC/SGD', 'base': 'BTC', 'quote': 'SGD'},
                'BTC/THB': {'id': 'THB', 'symbol': 'BTC/THB', 'base': 'BTC', 'quote': 'THB'},
                'BTC/TRY': {'id': 'TRY', 'symbol': 'BTC/TRY', 'base': 'BTC', 'quote': 'TRY'},
                'BTC/ZAR': {'id': 'ZAR', 'symbol': 'BTC/ZAR', 'base': 'BTC', 'quote': 'ZAR'},
            },
        }
        params.update(config)
        super(_1btcxe, self).__init__(params)

# -----------------------------------------------------------------------------


class acx (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'acx',
            'name': 'ACX',
            'countries': 'AU',
            'rateLimit': 1000,
            'version': 'v2',
            'hasCORS': True,
            'hasFetchTickers': True,
            'hasFetchOHLCV': True,
            'hasWithdraw': True,
            'timeframes': {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '2h': '120',
                '4h': '240',
                '12h': '720',
                '1d': '1440',
                '3d': '4320',
                '1w': '10080',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30247614-1fe61c74-9621-11e7-9e8c-f1a627afa279.jpg',
                'extension': '.json',
                'api': 'https://acx.io/api',
                'www': 'https://acx.io',
                'doc': 'https://acx.io/documents/api_v2',
            },
            'api': {
                'public': {
                    'get': [
                        'markets',  # Get all available markets
                        'tickers',  # Get ticker of all markets
                        'tickers/{market}',  # Get ticker of specific market
                        'trades',  # Get recent trades on market, each trade is included only once Trades are sorted in reverse creation order.
                        'order_book',  # Get the order book of specified market
                        'depth',  # Get depth or specified market Both asks and bids are sorted from highest price to lowest.
                        'k',  # Get OHLC(k line) of specific market
                        'k_with_pending_trades',  # Get K data with pending trades, which are the trades not included in K data yet, because there's delay between trade generated and processed by K data generator
                        'timestamp',  # Get server current time, in seconds since Unix epoch
                    ],
                },
                'private': {
                    'get': [
                        'members/me',  # Get your profile and accounts info
                        'deposits',  # Get your deposits history
                        'deposit',  # Get details of specific deposit
                        'deposit_address',  # Where to deposit The address field could be empty when a new address is generating (e.g. for bitcoin), you should try again later in that case.
                        'orders',  # Get your orders, results is paginated
                        'order',  # Get information of specified order
                        'trades/my',  # Get your executed trades Trades are sorted in reverse creation order.
                        'withdraws',  # Get your cryptocurrency withdraws
                        'withdraw',  # Get your cryptocurrency withdraw
                    ],
                    'post': [
                        'orders',  # Create a Sell/Buy order
                        'orders/multi',  # Create multiple sell/buy orders
                        'orders/clear',  # Cancel all my orders
                        'order/delete',  # Cancel an order
                        'withdraw',  # Create a withdraw
                    ],
                },
            },
        }
        params.update(config)
        super(acx, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetMarkets()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['id']
            symbol = market['name']
            base, quote = symbol.split('/')
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetMembersMe()
        balances = response['accounts']
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            uppercase = currency.upper()
            account = {
                'free': float(balance['balance']),
                'used': float(balance['locked']),
                'total': 0.0,
            }
            account['total'] = self.sum(account['free'], account['used'])
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        orderbook = self.publicGetDepth(self.extend({
            'market': market['id'],
            'limit': 300,
        }, params))
        timestamp = orderbook['timestamp'] * 1000
        result = self.parse_order_book(orderbook, timestamp)
        result['bids'] = self.sort_by(result['bids'], 0, True)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['at'] * 1000
        ticker = ticker['ticker']
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high', None),
            'low': self.safe_float(ticker, 'low', None),
            'bid': self.safe_float(ticker, 'buy', None),
            'ask': self.safe_float(ticker, 'sell', None),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': self.safe_float(ticker, 'last', None),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': self.safe_float(ticker, 'vol', None),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTickers(params)
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = None
            symbol = id
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            else:
                base = id[0:3]
                quote = id[3:6]
                base = base.upper()
                quote = quote.upper()
                base = self.common_currency_code(base)
                quote = self.common_currency_code(quote)
                symbol = base + '/' + quote
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTickersMarket(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_ticker(response, market)

    def parse_trade(self, trade, market=None):
        timestamp = trade['timestamp'] * 1000
        side = 'buy' if (trade['type'] == 'bid') else 'sell'
        return {
            'info': trade,
            'id': str(trade['tid']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'market': market['id'],
        }, params))
        # looks like they switched self endpoint off
        # it returns 503 Service Temporarily Unavailable always
        # return self.parse_trades(response, market)
        return response

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv[0] * 1000,
            ohlcv[1],
            ohlcv[2],
            ohlcv[3],
            ohlcv[4],
            ohlcv[5],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        if not limit:
            limit = 500  # default is 30
        request = {
            'market': market['id'],
            'period': self.timeframes[timeframe],
            'limit': limit,
        }
        if since:
            request['timestamp'] = since
        response = self.publicGetK(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'market': self.market_id(symbol),
            'side': side,
            'volume': str(amount),
            'ord_type': type,
        }
        if type == 'limit':
            order['price'] = str(price)
        response = self.privatePostOrders(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostOrderDelete({'id': id})

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        result = self.privatePostWithdraw(self.extend({
            'currency': currency.lower(),
            'sum': amount,
            'address': address,
        }, params))
        return {
            'info': result,
            'id': None,
        }

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = '/api' + '/' + self.version + '/' + self.implode_params(path, params)
        if 'extension' in self.urls:
            request += self.urls['extension']
        query = self.omit(params, self.extract_params(path))
        url = self.urls['api'] + request
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = str(self.nonce())
            query = self.urlencode(self.keysort(self.extend({
                'access_key': self.apiKey,
                'tonce': nonce,
            }, params)))
            auth = method + '|' + request + '|' + query
            signature = self.hmac(self.encode(auth), self.encode(self.secret))
            suffix = query + '&signature=' + signature
            if method == 'GET':
                url += '?' + suffix
            else:
                body = suffix
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class okcoin (Exchange):

    def __init__(self, config={}):
        params = {
            'version': 'v1',
            'rateLimit': 1000,  # up to 3000 requests per 5 minutes ≈ 600 requests per minute ≈ 10 requests per second ≈ 100 ms
            'hasFetchOHLCV': True,
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'extension': '.do',  # appended to endpoint URL
            'timeframes': {
                '1m': '1min',
                '3m': '3min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '1h': '1hour',
                '2h': '2hour',
                '4h': '4hour',
                '6h': '6hour',
                '12h': '12hour',
                '1d': '1day',
                '3d': '3day',
                '1w': '1week',
            },
            'api': {
                'public': {
                    'get': [
                        'depth',
                        'exchange_rate',
                        'future_depth',
                        'future_estimated_price',
                        'future_hold_amount',
                        'future_index',
                        'future_kline',
                        'future_price_limit',
                        'future_ticker',
                        'future_trades',
                        'kline',
                        'otcs',
                        'ticker',
                        'trades',
                    ],
                },
                'private': {
                    'post': [
                        'account_records',
                        'batch_trade',
                        'borrow_money',
                        'borrow_order_info',
                        'borrows_info',
                        'cancel_borrow',
                        'cancel_order',
                        'cancel_otc_order',
                        'cancel_withdraw',
                        'future_batch_trade',
                        'future_cancel',
                        'future_devolve',
                        'future_explosive',
                        'future_order_info',
                        'future_orders_info',
                        'future_position',
                        'future_position_4fix',
                        'future_trade',
                        'future_trades_history',
                        'future_userinfo',
                        'future_userinfo_4fix',
                        'lend_depth',
                        'order_fee',
                        'order_history',
                        'order_info',
                        'orders_info',
                        'otc_order_history',
                        'otc_order_info',
                        'repayment',
                        'submit_otc_order',
                        'trade',
                        'trade_history',
                        'trade_otc_order',
                        'withdraw',
                        'withdraw_info',
                        'unrepayments_info',
                        'userinfo',
                    ],
                },
            },
        }
        params.update(config)
        super(okcoin, self).__init__(params)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = 'publicGet'
        request = {
            'symbol': market['id'],
        }
        if market['future']:
            method += 'Future'
            request['contract_type'] = 'this_week'  # next_week, quarter
        method += 'Depth'
        orderbook = getattr(self, method)(self.extend(request, params))
        timestamp = self.milliseconds()
        return {
            'bids': orderbook['bids'],
            'asks': self.sort_by(orderbook['asks'], 0),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
        }

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['timestamp']
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['vol']),
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = 'publicGet'
        request = {
            'symbol': market['id'],
        }
        if market['future']:
            method += 'Future'
            request['contract_type'] = 'this_week'  # next_week, quarter
        method += 'Ticker'
        response = getattr(self, method)(self.extend(request, params))
        timestamp = int(response['date']) * 1000
        ticker = self.extend(response['ticker'], {'timestamp': timestamp})
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market=None):
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'info': trade,
            'timestamp': trade['date_ms'],
            'datetime': self.iso8601(trade['date_ms']),
            'symbol': symbol,
            'id': trade['tid'],
            'order': None,
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = 'publicGet'
        request = {
            'symbol': market['id'],
        }
        if market['future']:
            method += 'Future'
            request['contract_type'] = 'this_week'  # next_week, quarter
        method += 'Trades'
        response = getattr(self, method)(self.extend(request, params))
        return self.parse_trades(response, market)

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=1440, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = 'publicGet'
        request = {
            'symbol': market['id'],
            'type': self.timeframes[timeframe],
        }
        if market['future']:
            method += 'Future'
            request['contract_type'] = 'this_week'  # next_week, quarter
        method += 'Kline'
        if limit:
            request['size'] = int(limit)
        if since:
            request['since'] = since
        else:
            request['since'] = self.milliseconds() - 86400000  # last 24 hours
        response = getattr(self, method)(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostUserinfo()
        balances = response['info']['funds']
        result = {'info': response}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = self.account()
            account['free'] = self.safe_float(balances['free'], lowercase, 0.0)
            account['used'] = self.safe_float(balances['freezed'], lowercase, 0.0)
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = 'privatePost'
        order = {
            'symbol': market['id'],
            'type': side,
        }
        if market['future']:
            method += 'Future'
            order = self.extend(order, {
                'contract_type': 'this_week',  # next_week, quarter
                'match_price': 0,  # match best counter party price? 0 or 1, ignores price if 1
                'lever_rate': 10,  # leverage rate value: 10 or 20(10 by default)
                'price': price,
                'amount': amount,
            })
        else:
            if type == 'limit':
                order['price'] = price
                order['amount'] = amount
            else:
                order['type'] += '_market'
                if side == 'buy':
                    order['price'] = self.safe_float(params, 'cost')
                    if not order['price']:
                        raise ExchangeError(self.id + ' market buy orders require an additional cost parameter, cost = price * amount')
                else:
                    order['amount'] = amount
        params = self.omit(params, 'cost')
        method += 'Trade'
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['order_id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' cancelOrder() requires a symbol argument')
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'order_id': id,
        }
        method = 'privatePost'
        if market['future']:
            method += 'FutureCancel'
            request['contract_type'] = 'this_week'  # next_week, quarter
        else:
            method += 'CancelOrder'
        response = getattr(self, method)(self.extend(request, params))
        return response

    def getOrderStatus(self, status):
        if status == -1:
            return 'canceled'
        if status == 0:
            return 'open'
        if status == 1:
            return 'partial'
        if status == 2:
            return 'closed'
        if status == 4:
            return 'canceled'
        return status

    def parse_order(self, order, market=None):
        side = None
        type = None
        if 'type' in order:
            if (order['type'] == 'buy') or (order['type'] == 'sell'):
                side = order['type']
                type = 'limit'
            else:
                side = 'buy' if (order['type'] == 'buy_market') else 'sell'
                type = 'market'
        status = self.getOrderStatus(order['status'])
        symbol = None
        if not market:
            if 'symbol' in order:
                if order['symbol'] in self.markets_by_id:
                    market = self.markets_by_id[order['symbol']]
        if market:
            symbol = market['symbol']
        timestamp = None
        if 'create_date' in order:
            timestamp = order['create_date']
        amount = order['amount']
        filled = order['deal_amount']
        remaining = amount - filled
        average = order['avg_price']
        cost = average * filled
        result = {
            'info': order,
            'id': order['order_id'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': order['price'],
            'average': average,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'status': status,
            'fee': None,
        }
        return result

    def fetch_order(self, id, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + 'fetchOrders requires a symbol parameter')
        self.load_markets()
        market = self.market(symbol)
        method = 'privatePost'
        request = {
            'order_id': id,
            'symbol': market['id'],
            # 'status': 0,  # 0 for unfilled orders, 1 for filled orders
            # 'current_page': 1,  # current page number
            # 'page_length': 200,  # number of orders returned per page, maximum 200
        }
        if market['future']:
            method += 'Future'
            request['contract_type'] = 'this_week'  # next_week, quarter
        method += 'OrderInfo'
        response = getattr(self, method)(self.extend(request, params))
        return self.parse_order(response['orders'][0])

    def fetch_orders(self, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + 'fetchOrders requires a symbol parameter')
        self.load_markets()
        market = self.market(symbol)
        method = 'privatePost'
        request = {
            'symbol': market['id'],
        }
        order_id_in_params = ('order_id' in list(params.keys()))
        if market['future']:
            method += 'FutureOrdersInfo'
            request['contract_type'] = 'this_week'  # next_week, quarter
            if not order_id_in_params:
                raise ExchangeError(self.id + ' fetchOrders() requires order_id param for futures market ' + symbol + '(a string of one or more order ids, comma-separated)')
        else:
            type = self.safe_value(params, 'type')
            status = self.safe_value(params, 'status')
            if type:
                status = params['type']
            elif status:
                status = params['status']
            else:
                raise ExchangeError(self.id + ' fetchOrders() requires type param or status param for spot market ' + symbol + '(0 or "open" for unfilled orders, 1 or "closed" for filled orders)')
            if status == 'open':
                status = 0
            if status == 'closed':
                status = 1
            if order_id_in_params:
                method += 'OrdersInfo'
                request = self.extend(request, {
                    'type': status,
                })
            else:
                method += 'OrderHistory'
                request = self.extend(request, {
                    'status': status,
                    'current_page': 1,  # current page number
                    'page_length': 200,  # number of orders returned per page, maximum 200
                })
            params = self.omit(params, ['type', 'status'])
        response = getattr(self, method)(self.extend(request, params))
        return self.parse_orders(response['orders'], market)

    def fetch_open_orders(self, symbol=None, params={}):
        open = 0  # 0 for unfilled orders, 1 for filled orders
        return self.fetch_orders(symbol, self.extend({
            'status': open,
        }, params))

    def fetchClosedOrders(self, symbol=None, params={}):
        closed = 1  # 0 for unfilled orders, 1 for filled orders
        return self.fetch_orders(symbol, self.extend({
            'status': closed,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = '/'
        if api != 'web':
            url += self.version + '/'
        url += path + self.extension
        if api == 'private':
            query = self.keysort(self.extend({
                'api_key': self.apiKey,
            }, params))
            # secret key must be at the end of query
            queryString = self.rawencode(query) + '&secret_key=' + self.secret
            query['sign'] = self.hash(self.encode(queryString)).upper()
            body = self.urlencode(query)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        else:
            if params:
                url += '?' + self.urlencode(params)
        url = self.urls['api'][api] + url
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'result' in response:
            if not response['result']:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class allcoin (okcoin):

    def __init__(self, config={}):
        params = {
            'id': 'allcoin',
            'name': 'Allcoin',
            'countries': 'CA',
            'hasCORS': False,
            'extension': '',
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/31561809-c316b37c-b061-11e7-8d5a-b547b4d730eb.jpg',
                'api': {
                    'web': 'https://allcoin.com',
                    'public': 'https://api.allcoin.com/api',
                    'private': 'https://api.allcoin.com/api',
                },
                'www': 'https://allcoin.com',
                'doc': 'https://allcoin.com/About/APIReference',
            },
            'api': {
                'web': {
                    'get': [
                        'marketoverviews/',
                    ],
                },
                'public': {
                    'get': [
                        'depth',
                        'kline',
                        'ticker',
                        'trades',
                    ],
                },
                'private': {
                    'post': [
                        'batch_trade',
                        'cancel_order',
                        'order_history',
                        'order_info',
                        'orders_info',
                        'repayment',
                        'trade',
                        'trade_history',
                        'userinfo',
                    ],
                },
            },
        }
        params.update(config)
        super(allcoin, self).__init__(params)

    def fetch_markets(self):
        currencies = ['BTC', 'ETH', 'USD', 'QTUM']
        result = []
        for i in range(0, len(currencies)):
            currency = currencies[i]
            response = self.webGetMarketoverviews({
                'type': 'full',
                'secondary': currency,
            })
            markets = response['Markets']
            for k in range(0, len(markets)):
                market = markets[k]
                base = market['Primary']
                quote = market['Secondary']
                id = base.lower() + '_' + quote.lower()
                symbol = base + '/' + quote
                result.append({
                    'id': id,
                    'symbol': symbol,
                    'base': base,
                    'quote': quote,
                    'type': 'spot',
                    'spot': True,
                    'future': False,
                    'info': market,
                })
        return result

    def getOrderStatus(self, status):
        if status == -1:
            return 'canceled'
        if status == 0:
            return 'open'
        if status == 1:
            return 'partial'
        if status == 2:
            return 'closed'
        if status == 10:
            return 'canceled'
        return status

# -----------------------------------------------------------------------------


class anxpro (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'anxpro',
            'name': 'ANXPro',
            'countries': ['JP', 'SG', 'HK', 'NZ'],
            'version': '2',
            'rateLimit': 1500,
            'hasCORS': False,
            'hasFetchTrades': False,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27765983-fd8595da-5ec9-11e7-82e3-adb3ab8c2612.jpg',
                'api': 'https://anxpro.com/api',
                'www': 'https://anxpro.com',
                'doc': [
                    'http://docs.anxv2.apiary.io',
                    'https://anxpro.com/pages/api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        '{currency_pair}/money/ticker',
                        '{currency_pair}/money/depth/full',
                        '{currency_pair}/money/trade/fetch',  # disabled by ANXPro
                    ],
                },
                'private': {
                    'post': [
                        '{currency_pair}/money/order/add',
                        '{currency_pair}/money/order/cancel',
                        '{currency_pair}/money/order/quote',
                        '{currency_pair}/money/order/result',
                        '{currency_pair}/money/orders',
                        'money/{currency}/address',
                        'money/{currency}/send_simple',
                        'money/info',
                        'money/trade/list',
                        'money/wallet/history',
                    ],
                },
            },
            'markets': {
                'BTC/USD': {'id': 'BTCUSD', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'BTC/HKD': {'id': 'BTCHKD', 'symbol': 'BTC/HKD', 'base': 'BTC', 'quote': 'HKD'},
                'BTC/EUR': {'id': 'BTCEUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                'BTC/CAD': {'id': 'BTCCAD', 'symbol': 'BTC/CAD', 'base': 'BTC', 'quote': 'CAD'},
                'BTC/AUD': {'id': 'BTCAUD', 'symbol': 'BTC/AUD', 'base': 'BTC', 'quote': 'AUD'},
                'BTC/SGD': {'id': 'BTCSGD', 'symbol': 'BTC/SGD', 'base': 'BTC', 'quote': 'SGD'},
                'BTC/JPY': {'id': 'BTCJPY', 'symbol': 'BTC/JPY', 'base': 'BTC', 'quote': 'JPY'},
                'BTC/GBP': {'id': 'BTCGBP', 'symbol': 'BTC/GBP', 'base': 'BTC', 'quote': 'GBP'},
                'BTC/NZD': {'id': 'BTCNZD', 'symbol': 'BTC/NZD', 'base': 'BTC', 'quote': 'NZD'},
                'LTC/BTC': {'id': 'LTCBTC', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'DOGE/BTC': {'id': 'DOGEBTC', 'symbol': 'DOGE/BTC', 'base': 'DOGE', 'quote': 'BTC'},
                'STR/BTC': {'id': 'STRBTC', 'symbol': 'STR/BTC', 'base': 'STR', 'quote': 'BTC'},
                'XRP/BTC': {'id': 'XRPBTC', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(anxpro, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privatePostMoneyInfo()
        balance = response['data']
        currencies = list(balance['Wallets'].keys())
        result = {'info': balance}
        for c in range(0, len(currencies)):
            currency = currencies[c]
            account = self.account()
            if currency in balance['Wallets']:
                wallet = balance['Wallets'][currency]
                account['free'] = float(wallet['Available_Balance']['value'])
                account['total'] = float(wallet['Balance']['value'])
                account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        response = self.publicGetCurrencyPairMoneyDepthFull(self.extend({
            'currency_pair': self.market_id(symbol),
        }, params))
        orderbook = response['data']
        t = int(orderbook['dataUpdateTime'])
        timestamp = int(t / 1000)
        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetCurrencyPairMoneyTicker(self.extend({
            'currency_pair': self.market_id(symbol),
        }, params))
        ticker = response['data']
        t = int(ticker['dataUpdateTime'])
        timestamp = int(t / 1000)
        bid = self.safe_float(ticker['buy'], 'value')
        ask = self.safe_float(ticker['sell'], 'value')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']['value']),
            'low': float(ticker['low']['value']),
            'bid': bid,
            'ask': ask,
            'vwap': float(ticker['vwap']['value']),
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']['value']),
            'change': None,
            'percentage': None,
            'average': float(ticker['avg']['value']),
            'baseVolume': None,
            'quoteVolume': float(ticker['vol']['value']),
        }

    def fetch_trades(self, market, params={}):
        raise ExchangeError(self.id + ' switched off the trades endpoint, see their docs at http://docs.anxv2.apiary.io/reference/market-data/currencypairmoneytradefetch-disabled')
        return self.publicGetCurrencyPairMoneyTradeFetch(self.extend({
            'currency_pair': self.market_id(market),
        }, params))

    def create_order(self, market, type, side, amount, price=None, params={}):
        order = {
            'currency_pair': self.market_id(market),
            'amount_int': int(amount * 100000000),  # 10^8
            'type': side,
        }
        if type == 'limit':
            order['price_int'] = int(price * 100000)  # 10^5
        result = self.privatePostCurrencyPairOrderAdd(self.extend(order, params))
        return {
            'info': result,
            'id': result['data']
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCurrencyPairOrderCancel({'oid': id})

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        response = self.privatePostMoneyCurrencySendSimple(self.extend({
            'currency': currency,
            'amount_int': int(amount * 100000000),  # 10^8
            'address': address,
        }, params))
        return {
            'info': response,
            'id': response['data']['transactionId'],
        }

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        url = self.urls['api'] + '/' + self.version + '/' + request
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            body = self.urlencode(self.extend({'nonce': nonce}, query))
            secret = base64.b64decode(self.secret)
            auth = request + "\0" + body
            signature = self.hmac(self.encode(auth), secret, hashlib.sha512, 'base64')
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Rest-Key': self.apiKey,
                'Rest-Sign': self.decode(signature),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'result' in response:
            if response['result'] == 'success':
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class binance (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'binance',
            'name': 'Binance',
            'countries': 'CN',  # China
            'rateLimit': 1000,
            'version': 'v1',
            'hasCORS': False,
            'hasFetchOHLCV': True,
            'hasFetchMyTrades': True,
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'timeframes': {
                '1m': '1m',
                '3m': '3m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '2h': '2h',
                '4h': '4h',
                '6h': '6h',
                '8h': '8h',
                '12h': '12h',
                '1d': '1d',
                '3d': '3d',
                '1w': '1w',
                '1M': '1M',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/29604020-d5483cdc-87ee-11e7-94c7-d1a8d9169293.jpg',
                'api': {
                    'web': 'https://www.binance.com',
                    'public': 'https://www.binance.com/api',
                    'private': 'https://www.binance.com/api',
                },
                'www': 'https://www.binance.com',
                'doc': 'https://www.binance.com/restapipub.html',
                'fees': 'https://binance.zendesk.com/hc/en-us/articles/115000429332',
            },
            'api': {
                'web': {
                    'get': [
                        'exchange/public/product',
                    ],
                },
                'public': {
                    'get': [
                        'ping',
                        'time',
                        'depth',
                        'aggTrades',
                        'klines',
                        'ticker/24hr',
                    ],
                },
                'private': {
                    'get': [
                        'order',
                        'openOrders',
                        'allOrders',
                        'account',
                        'myTrades',
                    ],
                    'post': [
                        'order',
                        'order/test',
                        'userDataStream',
                    ],
                    'put': [
                        'userDataStream'
                    ],
                    'delete': [
                        'order',
                        'userDataStream',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'taker': 0.001,
                    'maker': 0.001,
                },
                'funding': {
                    'withdraw': {
                        'BNB': 1.0,
                        'BTC': 0.0005,
                        'ETH': 0.005,
                        'LTC': 0.001,
                        'NEO': 0.0,
                        'QTUM': 0.1,
                        'SNT': 1.0,
                        'EOS': 0.1,
                        'BCC': None,
                        'GAS': 0.0,
                        'USDT': 5.0,
                        'HSR': 0.0001,
                        'OAX': 0.1,
                        'DNT': 1.0,
                        'MCO': 0.1,
                        'ICN': 0.1,
                        'WTC': 0.1,
                        'OMG': 0.1,
                        'ZRX': 1.0,
                        'STRAT': 0.1,
                        'SNGLS': 1.0,
                        'BQX': 1.0,
                    },
                },
            },
            'precision': {
                'amount': 6,
                'price': 6,
            },
            'markets': {
                'ETH/BTC': {'id': 'ETHBTC', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC', 'lot': 0.001, 'limits': {'amount': {'min': 0.001, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'LTC/BTC': {'id': 'LTCBTC', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'BNB/BTC': {'id': 'BNBBTC', 'symbol': 'BNB/BTC', 'base': 'BNB', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'NEO/BTC': {'id': 'NEOBTC', 'symbol': 'NEO/BTC', 'base': 'NEO', 'quote': 'BTC', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'GAS/BTC': {'id': 'GASBTC', 'symbol': 'GAS/BTC', 'base': 'GAS', 'quote': 'BTC', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'BCC/BTC': {'id': 'BCCBTC', 'symbol': 'BCC/BTC', 'base': 'BCC', 'quote': 'BTC', 'lot': 0.001, 'limits': {'amount': {'min': 0.001, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'MCO/BTC': {'id': 'MCOBTC', 'symbol': 'MCO/BTC', 'base': 'MCO', 'quote': 'BTC', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'WTC/BTC': {'id': 'WTCBTC', 'symbol': 'WTC/BTC', 'base': 'WTC', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'OMG/BTC': {'id': 'OMGBTC', 'symbol': 'OMG/BTC', 'base': 'OMG', 'quote': 'BTC', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'ZRX/BTC': {'id': 'ZRXBTC', 'symbol': 'ZRX/BTC', 'base': 'ZRX', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'BQX/BTC': {'id': 'BQXBTC', 'symbol': 'BQX/BTC', 'base': 'BQX', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'KNC/BTC': {'id': 'KNCBTC', 'symbol': 'KNC/BTC', 'base': 'KNC', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'FUN/BTC': {'id': 'FUNBTC', 'symbol': 'FUN/BTC', 'base': 'FUN', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'SNM/BTC': {'id': 'SNMBTC', 'symbol': 'SNM/BTC', 'base': 'SNM', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'XVG/BTC': {'id': 'XVGBTC', 'symbol': 'XVG/BTC', 'base': 'XVG', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'CTR/BTC': {'id': 'CTRBTC', 'symbol': 'CTR/BTC', 'base': 'CTR', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'BNB/ETH': {'id': 'BNBETH', 'symbol': 'BNB/ETH', 'base': 'BNB', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'SNT/ETH': {'id': 'SNTETH', 'symbol': 'SNT/ETH', 'base': 'SNT', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'BNT/ETH': {'id': 'BNTETH', 'symbol': 'BNT/ETH', 'base': 'BNT', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'EOS/ETH': {'id': 'EOSETH', 'symbol': 'EOS/ETH', 'base': 'EOS', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'OAX/ETH': {'id': 'OAXETH', 'symbol': 'OAX/ETH', 'base': 'OAX', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'DNT/ETH': {'id': 'DNTETH', 'symbol': 'DNT/ETH', 'base': 'DNT', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'MCO/ETH': {'id': 'MCOETH', 'symbol': 'MCO/ETH', 'base': 'MCO', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'ICN/ETH': {'id': 'ICNETH', 'symbol': 'ICN/ETH', 'base': 'ICN', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'WTC/ETH': {'id': 'WTCETH', 'symbol': 'WTC/ETH', 'base': 'WTC', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'OMG/ETH': {'id': 'OMGETH', 'symbol': 'OMG/ETH', 'base': 'OMG', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'ZRX/ETH': {'id': 'ZRXETH', 'symbol': 'ZRX/ETH', 'base': 'ZRX', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'BQX/ETH': {'id': 'BQXETH', 'symbol': 'BQX/ETH', 'base': 'BQX', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.0000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'KNC/ETH': {'id': 'KNCETH', 'symbol': 'KNC/ETH', 'base': 'KNC', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.0000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'FUN/ETH': {'id': 'FUNETH', 'symbol': 'FUN/ETH', 'base': 'FUN', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'SNM/ETH': {'id': 'SNMETH', 'symbol': 'SNM/ETH', 'base': 'SNM', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'NEO/ETH': {'id': 'NEOETH', 'symbol': 'NEO/ETH', 'base': 'NEO', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'XVG/ETH': {'id': 'XVGETH', 'symbol': 'XVG/ETH', 'base': 'XVG', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'CTR/ETH': {'id': 'CTRETH', 'symbol': 'CTR/ETH', 'base': 'CTR', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.0000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'QTUM/BTC': {'id': 'QTUMBTC', 'symbol': 'QTUM/BTC', 'base': 'QTUM', 'quote': 'BTC', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'LINK/BTC': {'id': 'LINKBTC', 'symbol': 'LINK/BTC', 'base': 'LINK', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'SALT/BTC': {'id': 'SALTBTC', 'symbol': 'SALT/BTC', 'base': 'SALT', 'quote': 'BTC', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'IOTA/BTC': {'id': 'IOTABTC', 'symbol': 'IOTA/BTC', 'base': 'IOTA', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'QTUM/ETH': {'id': 'QTUMETH', 'symbol': 'QTUM/ETH', 'base': 'QTUM', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'LINK/ETH': {'id': 'LINKETH', 'symbol': 'LINK/ETH', 'base': 'LINK', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'SALT/ETH': {'id': 'SALTETH', 'symbol': 'SALT/ETH', 'base': 'SALT', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'IOTA/ETH': {'id': 'IOTAETH', 'symbol': 'IOTA/ETH', 'base': 'IOTA', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'BTC/USDT': {'id': 'BTCUSDT', 'symbol': 'BTC/USDT', 'base': 'BTC', 'quote': 'USDT', 'lot': 0.000001, 'limits': {'amount': {'min': 0.000001, 'max': None}, 'price': {'min': 0.01, 'max': None}, 'cost': {'min': 1, 'max': None}}},
                'ETH/USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT', 'base': 'ETH', 'quote': 'USDT', 'lot': 0.00001, 'limits': {'amount': {'min': 0.00001, 'max': None}, 'price': {'min': 0.01, 'max': None}, 'cost': {'min': 1, 'max': None}}},
                'STRAT/ETH': {'id': 'STRATETH', 'symbol': 'STRAT/ETH', 'base': 'STRAT', 'quote': 'ETH', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'SNGLS/ETH': {'id': 'SNGLSETH', 'symbol': 'SNGLS/ETH', 'base': 'SNGLS', 'quote': 'ETH', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.01, 'max': None}}},
                'STRAT/BTC': {'id': 'STRATBTC', 'symbol': 'STRAT/BTC', 'base': 'STRAT', 'quote': 'BTC', 'lot': 0.01, 'limits': {'amount': {'min': 0.01, 'max': None}, 'price': {'min': 0.000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
                'SNGLS/BTC': {'id': 'SNGLSBTC', 'symbol': 'SNGLS/BTC', 'base': 'SNGLS', 'quote': 'BTC', 'lot': 1, 'limits': {'amount': {'min': 1, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': 0.001, 'max': None}}},
            },
        }
        params.update(config)
        super(binance, self).__init__(params)

    def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='taker', params={}):
        market = self.markets[symbol]
        key = 'quote'
        rate = market[takerOrMaker]
        cost = float(self.cost_to_precision(symbol, amount * rate))
        if side == 'sell':
            cost *= price
        else:
            key = 'base'
        return {
            'currency': market[key],
            'rate': rate,
            'cost': float(self.fee_to_precision(symbol, cost)),
        }

    def fetch_balance(self, params={}):
        response = self.privateGetAccount(params)
        result = {'info': response}
        balances = response['balances']
        for i in range(0, len(balances)):
            balance = balances[i]
            asset = balance['asset']
            currency = self.common_currency_code(asset)
            account = {
                'free': float(balance['free']),
                'used': float(balance['locked']),
                'total': 0.0,
            }
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderbook = self.publicGetDepth(self.extend({
            'symbol': market['id'],
            'limit': 100,  # default = maximum = 100
        }, params))
        return self.parse_order_book(orderbook)

    def parse_ticker(self, ticker, market):
        timestamp = ticker['closeTime']
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['highPrice']),
            'low': float(ticker['lowPrice']),
            'bid': float(ticker['bidPrice']),
            'ask': float(ticker['askPrice']),
            'vwap': float(ticker['weightedAvgPrice']),
            'open': float(ticker['openPrice']),
            'close': float(ticker['prevClosePrice']),
            'first': None,
            'last': float(ticker['lastPrice']),
            'change': float(ticker['priceChangePercent']),
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['volume']),
            'quoteVolume': float(ticker['quoteVolume']),
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTicker24hr(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_ticker(response, market)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv[0],
            float(ohlcv[1]),
            float(ohlcv[2]),
            float(ohlcv[3]),
            float(ohlcv[4]),
            float(ohlcv[5]),
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'interval': self.timeframes[timeframe],
        }
        request['limit'] = limit if (limit) else 500  # default == max == 500
        if since:
            request['startTime'] = since
        response = self.publicGetKlines(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def parse_trade(self, trade, market=None):
        timestampField = 'T' if ('T' in list(trade.keys())) else 'time'
        timestamp = trade[timestampField]
        priceField = 'p' if ('p' in list(trade.keys())) else 'price'
        price = float(trade[priceField])
        amountField = 'q' if ('q' in list(trade.keys())) else 'qty'
        amount = float(trade[amountField])
        idField = 'a' if ('a' in list(trade.keys())) else 'id'
        id = str(trade[idField])
        side = None
        order = None
        if 'orderId' in trade:
            order = str(trade['orderId'])
        if 'm' in trade:
            side = 'sell'
            if trade['m']:
                side = 'buy'
        else:
            side = 'buy' if (trade['isBuyer']) else 'sell'
        fee = None
        if 'commission' in trade:
            fee = {
                'cost': float(trade['commission']),
                'currency': trade['commissionAsset'],
            }
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': id,
            'order': order,
            'type': None,
            'side': side,
            'price': price,
            'cost': price * amount,
            'amount': amount,
            'fee': fee,
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetAggTrades(self.extend({
            'symbol': market['id'],
            # 'fromId': 123,    # ID to get aggregate trades from INCLUSIVE.
            # 'startTime': 456,  # Timestamp in ms to get aggregate trades from INCLUSIVE.
            # 'endTime': 789,   # Timestamp in ms to get aggregate trades until INCLUSIVE.
            'limit': 500,        # default = maximum = 500
        }, params))
        return self.parse_trades(response, market)

    def parse_order_status(self, status):
        if status == 'NEW':
            return 'open'
        if status == 'PARTIALLY_FILLED':
            return 'partial'
        if status == 'FILLED':
            return 'closed'
        if status == 'CANCELED':
            return 'canceled'
        return status.lower()

    def parse_order(self, order, market=None):
        status = self.parse_order_status(order['status'])
        symbol = None
        if market:
            symbol = market['symbol']
        else:
            id = order['symbol']
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
        timestamp = order['time']
        price = float(order['price'])
        amount = float(order['origQty'])
        filled = self.safe_float(order, 'executedQty', 0.0)
        remaining = max(amount - filled, 0.0)
        result = {
            'info': order,
            'id': str(order['orderId']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': order['type'].lower(),
            'side': order['side'].lower(),
            'price': price,
            'amount': amount,
            'cost': price * amount,
            'filled': filled,
            'remaining': remaining,
            'status': status,
            'fee': None,
        }
        return result

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        market = self.market(symbol)
        order = {
            'symbol': market['id'],
            'quantity': self.amount_to_precision(symbol, amount),
            'type': type.upper(),
            'side': side.upper(),
        }
        if type == 'limit':
            order = self.extend(order, {
                'price': self.price_to_precision(symbol, price),
                'timeInForce': 'GTC',  # 'GTC' = Good To Cancel(default), 'IOC' = Immediate Or Cancel
            })
        response = self.privatePostOrder(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['orderId']),
        }

    def fetch_order(self, id, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOrder requires a symbol param')
        market = self.market(symbol)
        response = self.privateGetOrder(self.extend({
            'symbol': market['id'],
            'orderId': int(id),
        }, params))
        return self.parse_order(response, market)

    def fetch_orders(self, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOrders requires a symbol param')
        market = self.market(symbol)
        response = self.privateGetAllOrders(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_orders(response, market)

    def fetch_open_orders(self, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOpenOrders requires a symbol param')
        market = self.market(symbol)
        response = self.privateGetOpenOrders(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_orders(response, market)

    def cancel_order(self, id, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' cancelOrder requires a symbol param')
        market = self.market(symbol)
        response = None
        try:
            response = self.privateDeleteOrder(self.extend({
                'symbol': market['id'],
                'orderId': int(id),
                # 'origClientOrderId': id,
            }, params))
        except Exception as e:
            if self.last_http_response.find('UNKNOWN_ORDER') >= 0:
                raise OrderNotFound(self.id + ' cancelOrder() error: ' + self.last_http_response)
            raise e
        return response

    def nonce(self):
        return self.milliseconds()

    def fetch_my_trades(self, symbol=None, params={}):
        self.load_markets()
        if not symbol:
            raise ExchangeError(self.id + ' fetchMyTrades requires a symbol')
        market = self.market(symbol)
        response = self.privateGetMyTrades(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        if api != 'web':
            url += '/' + self.version
        url += '/' + path
        if api == 'private':
            nonce = self.nonce()
            query = self.urlencode(self.extend({'timestamp': nonce}, params))
            auth = self.secret + '|' + query
            signature = self.hash(self.encode(auth), 'sha256')
            query += '&' + 'signature=' + signature
            headers = {
                'X-MBX-APIKEY': self.apiKey,
            }
            if method == 'GET':
                url += '?' + query
            else:
                body = query
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
        else:
            if params:
                url += '?' + self.urlencode(params)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'code' in response:
            if response['code'] < 0:
                if response['code'] == -2010:
                    raise InsufficientFunds(self.id + ' ' + self.json(response))
                if response['code'] == -2011:
                    raise OrderNotFound(self.id + ' ' + self.json(response))
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class bit2c (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bit2c',
            'name': 'Bit2C',
            'countries': 'IL',  # Israel
            'rateLimit': 3000,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766119-3593220e-5ece-11e7-8b3a-5a041f6bcc3f.jpg',
                'api': 'https://www.bit2c.co.il',
                'www': 'https://www.bit2c.co.il',
                'doc': [
                    'https://www.bit2c.co.il/home/api',
                    'https://github.com/OferE/bit2c',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'Exchanges/{pair}/Ticker',
                        'Exchanges/{pair}/orderbook',
                        'Exchanges/{pair}/trades',
                    ],
                },
                'private': {
                    'post': [
                        'Account/Balance',
                        'Account/Balance/v2',
                        'Merchant/CreateCheckout',
                        'Order/AccountHistory',
                        'Order/AddCoinFundsRequest',
                        'Order/AddFund',
                        'Order/AddOrder',
                        'Order/AddOrderMarketPriceBuy',
                        'Order/AddOrderMarketPriceSell',
                        'Order/CancelOrder',
                        'Order/MyOrders',
                        'Payment/GetMyId',
                        'Payment/Send',
                    ],
                },
            },
            'markets': {
                'BTC/NIS': {'id': 'BtcNis', 'symbol': 'BTC/NIS', 'base': 'BTC', 'quote': 'NIS'},
                'BCH/NIS': {'id': 'BchNis', 'symbol': 'BCH/NIS', 'base': 'BCH', 'quote': 'NIS'},
                'LTC/NIS': {'id': 'LtcNis', 'symbol': 'LTC/NIS', 'base': 'LTC', 'quote': 'NIS'},
            },
        }
        params.update(config)
        super(bit2c, self).__init__(params)

    def fetch_balance(self, params={}):
        balance = self.privatePostAccountBalanceV2()
        result = {'info': balance}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in balance:
                available = 'AVAILABLE_' + currency
                account['free'] = balance[available]
                account['total'] = balance[currency]
                account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetExchangesPairOrderbook(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetExchangesPairTicker(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['h']),
            'ask': float(ticker['l']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['ll']),
            'change': None,
            'percentage': None,
            'average': float(ticker['av']),
            'baseVolume': None,
            'quoteVolume': float(ticker['a']),
        }

    def parse_trade(self, trade, market=None):
        timestamp = int(trade['date']) * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'id': str(trade['tid']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': None,
            'type': None,
            'side': None,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetExchangesPairTrades(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        method = 'privatePostOrderAddOrder'
        order = {
            'Amount': amount,
            'Pair': self.market_id(symbol),
        }
        if type == 'market':
            method += 'MarketPrice' + self.capitalize(side)
        else:
            order['Price'] = price
            order['Total'] = amount * price
            order['IsBid'] = (side == 'buy')
        result = getattr(self, method)(self.extend(order, params))
        return {
            'info': result,
            'id': result['NewOrder']['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostOrderCancelOrder({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        if api == 'public':
            url += '.json'
        else:
            nonce = self.nonce()
            query = self.extend({'nonce': nonce}, params)
            body = self.urlencode(query)
            signature = self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512, 'base64')
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'key': self.apiKey,
                'sign': self.decode(signature),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class bitbay (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitbay',
            'name': 'BitBay',
            'countries': ['PL', 'EU'],  # Poland
            'rateLimit': 1000,
            'hasCORS': True,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766132-978a7bd8-5ece-11e7-9540-bc96d1e9bbb8.jpg',
                'www': 'https://bitbay.net',
                'api': {
                    'public': 'https://bitbay.net/API/Public',
                    'private': 'https://bitbay.net/API/Trading/tradingApi.php',
                },
                'doc': [
                    'https://bitbay.net/public-api',
                    'https://bitbay.net/account/tab-api',
                    'https://github.com/BitBayNet/API',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        '{id}/all',
                        '{id}/market',
                        '{id}/orderbook',
                        '{id}/ticker',
                        '{id}/trades',
                    ],
                },
                'private': {
                    'post': [
                        'info',
                        'trade',
                        'cancel',
                        'orderbook',
                        'orders',
                        'transfer',
                        'withdraw',
                        'history',
                        'transactions',
                    ],
                },
            },
            'markets': {
                'BTC/USD': {'id': 'BTCUSD', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'BTC/EUR': {'id': 'BTCEUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                'BTC/PLN': {'id': 'BTCPLN', 'symbol': 'BTC/PLN', 'base': 'BTC', 'quote': 'PLN'},
                'LTC/USD': {'id': 'LTCUSD', 'symbol': 'LTC/USD', 'base': 'LTC', 'quote': 'USD'},
                'LTC/EUR': {'id': 'LTCEUR', 'symbol': 'LTC/EUR', 'base': 'LTC', 'quote': 'EUR'},
                'LTC/PLN': {'id': 'LTCPLN', 'symbol': 'LTC/PLN', 'base': 'LTC', 'quote': 'PLN'},
                'LTC/BTC': {'id': 'LTCBTC', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'ETH/USD': {'id': 'ETHUSD', 'symbol': 'ETH/USD', 'base': 'ETH', 'quote': 'USD'},
                'ETH/EUR': {'id': 'ETHEUR', 'symbol': 'ETH/EUR', 'base': 'ETH', 'quote': 'EUR'},
                'ETH/PLN': {'id': 'ETHPLN', 'symbol': 'ETH/PLN', 'base': 'ETH', 'quote': 'PLN'},
                'ETH/BTC': {'id': 'ETHBTC', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
                'LSK/USD': {'id': 'LSKUSD', 'symbol': 'LSK/USD', 'base': 'LSK', 'quote': 'USD'},
                'LSK/EUR': {'id': 'LSKEUR', 'symbol': 'LSK/EUR', 'base': 'LSK', 'quote': 'EUR'},
                'LSK/PLN': {'id': 'LSKPLN', 'symbol': 'LSK/PLN', 'base': 'LSK', 'quote': 'PLN'},
                'LSK/BTC': {'id': 'LSKBTC', 'symbol': 'LSK/BTC', 'base': 'LSK', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(bitbay, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privatePostInfo()
        if 'balances' in response:
            balance = response['balances']
            result = {'info': balance}
            for c in range(0, len(self.currencies)):
                currency = self.currencies[c]
                account = self.account()
                if currency in balance:
                    account['free'] = float(balance[currency]['available'])
                    account['used'] = float(balance[currency]['locked'])
                    account['total'] = self.sum(account['free'], account['used'])
                result[currency] = account
            return self.parse_balance(result)
        raise ExchangeError(self.id + ' empty balance response ' + self.json(response))

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetIdOrderbook(self.extend({
            'id': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetIdTicker(self.extend({
            'id': self.market_id(symbol),
        }, params))
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['max']),
            'low': float(ticker['min']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': float(ticker['vwap']),
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': float(ticker['average']),
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'id': trade['tid'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetIdTrades(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        market = self.market(symbol)
        return self.privatePostTrade(self.extend({
            'type': side,
            'currency': market['base'],
            'amount': amount,
            'payment_currency': market['quote'],
            'rate': price,
        }, params))

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancel({'id': id})

    def isFiat(self, currency):
        fiatCurrencies = {
            'USD': True,
            'EUR': True,
            'PLN': True,
        }
        if currency in fiatCurrencies:
            return True
        return False

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        method = None
        request = {
            'currency': currency,
            'quantity': amount,
        }
        if self.isFiat(currency):
            method = 'privatePostWithdraw'
            # request['account'] = params['account']  # they demand an account number
            # request['express'] = params['express']  # whatever it means, they don't explain
            # request['bic'] = ''
        else:
            method = 'privatePostTransfer'
            request['address'] = address
        response = getattr(self, method)(self.extend(request, params))
        return {
            'info': response,
            'id': None,
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        if api == 'public':
            url += '/' + self.implode_params(path, params) + '.json'
        else:
            body = self.urlencode(self.extend({
                'method': path,
                'moment': self.nonce(),
            }, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'API-Key': self.apiKey,
                'API-Hash': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class bitcoincoid (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitcoincoid',
            'name': 'Bitcoin.co.id',
            'countries': 'ID',  # Indonesia
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766138-043c7786-5ecf-11e7-882b-809c14f38b53.jpg',
                'api': {
                    'public': 'https://vip.bitcoin.co.id/api',
                    'private': 'https://vip.bitcoin.co.id/tapi',
                },
                'www': 'https://www.bitcoin.co.id',
                'doc': [
                    'https://vip.bitcoin.co.id/downloads/BITCOINCOID-API-DOCUMENTATION.pdf',
                    'https://vip.bitcoin.co.id/trade_api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        '{pair}/ticker',
                        '{pair}/trades',
                        '{pair}/depth',
                    ],
                },
                'private': {
                    'post': [
                        'getInfo',
                        'transHistory',
                        'trade',
                        'tradeHistory',
                        'openOrders',
                        'cancelOrder',
                    ],
                },
            },
            'markets': {
                'BTC/IDR': {'id': 'btc_idr', 'symbol': 'BTC/IDR', 'base': 'BTC', 'quote': 'IDR', 'baseId': 'btc', 'quoteId': 'idr'},
                'BCH/IDR': {'id': 'bch_idr', 'symbol': 'BCH/IDR', 'base': 'BCH', 'quote': 'IDR', 'baseId': 'bch', 'quoteId': 'idr'},
                'ETH/IDR': {'id': 'eth_idr', 'symbol': 'ETH/IDR', 'base': 'ETH', 'quote': 'IDR', 'baseId': 'eth', 'quoteId': 'idr'},
                'ETC/IDR': {'id': 'etc_idr', 'symbol': 'ETC/IDR', 'base': 'ETC', 'quote': 'IDR', 'baseId': 'etc', 'quoteId': 'idr'},
                'XRP/IDR': {'id': 'xrp_idr', 'symbol': 'XRP/IDR', 'base': 'XRP', 'quote': 'IDR', 'baseId': 'xrp', 'quoteId': 'idr'},
                'XZC/IDR': {'id': 'xzc_idr', 'symbol': 'XZC/IDR', 'base': 'XZC', 'quote': 'IDR', 'baseId': 'xzc', 'quoteId': 'idr'},
                'BTS/BTC': {'id': 'bts_btc', 'symbol': 'BTS/BTC', 'base': 'BTS', 'quote': 'BTC', 'baseId': 'bts', 'quoteId': 'btc'},
                'DASH/BTC': {'id': 'drk_btc', 'symbol': 'DASH/BTC', 'base': 'DASH', 'quote': 'BTC', 'baseId': 'drk', 'quoteId': 'btc'},
                'DOGE/BTC': {'id': 'doge_btc', 'symbol': 'DOGE/BTC', 'base': 'DOGE', 'quote': 'BTC', 'baseId': 'doge', 'quoteId': 'btc'},
                'ETH/BTC': {'id': 'eth_btc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC', 'baseId': 'eth', 'quoteId': 'btc'},
                'LTC/BTC': {'id': 'ltc_btc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC', 'baseId': 'ltc', 'quoteId': 'btc'},
                'NXT/BTC': {'id': 'nxt_btc', 'symbol': 'NXT/BTC', 'base': 'NXT', 'quote': 'BTC', 'baseId': 'nxt', 'quoteId': 'btc'},
                'XLM/BTC': {'id': 'str_btc', 'symbol': 'XLM/BTC', 'base': 'XLM', 'quote': 'BTC', 'baseId': 'str', 'quoteId': 'btc'},
                'XEM/BTC': {'id': 'nem_btc', 'symbol': 'XEM/BTC', 'base': 'XEM', 'quote': 'BTC', 'baseId': 'nem', 'quoteId': 'btc'},
                'XRP/BTC': {'id': 'xrp_btc', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC', 'baseId': 'xrp', 'quoteId': 'btc'},
            },
        }
        params.update(config)
        super(bitcoincoid, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privatePostGetInfo()
        balance = response['return']
        result = {'info': balance}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = self.account()
            account['free'] = self.safe_float(balance['balance'], lowercase, 0.0)
            account['used'] = self.safe_float(balance['balance_hold'], lowercase, 0.0)
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetPairDepth(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'buy', 'sell')

    def fetch_ticker(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetPairTicker(self.extend({
            'pair': market['id'],
        }, params))
        ticker = response['ticker']
        timestamp = float(ticker['server_time']) * 1000
        baseVolume = 'vol_' + market['baseId'].lower()
        quoteVolume = 'vol_' + market['quoteId'].lower()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker[baseVolume]),
            'quoteVolume': float(ticker[quoteVolume]),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = int(trade['date']) * 1000
        return {
            'id': trade['tid'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetPairTrades(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        market = self.market(symbol)
        order = {
            'pair': market['id'],
            'type': side,
            'price': price,
        }
        base = market['baseId']
        order[base] = amount
        result = self.privatePostTrade(self.extend(order, params))
        return {
            'info': result,
            'id': str(result['return']['order_id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder(self.extend({
            'order_id': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        if api == 'public':
            url += '/' + self.implode_params(path, params)
        else:
            body = self.urlencode(self.extend({
                'method': path,
                'nonce': self.nonce(),
            }, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + response['error'])
        return response

# -----------------------------------------------------------------------------


class bitfinex (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitfinex',
            'name': 'Bitfinex',
            'countries': 'US',
            'version': 'v1',
            'rateLimit': 1500,
            'hasCORS': False,
            'hasFetchOrder': True,
            'hasFetchTickers': False,
            'hasDeposit': True,
            'hasWithdraw': True,
            'hasFetchOHLCV': True,
            'timeframes': {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '3h': '3h',
                '6h': '6h',
                '12h': '12h',
                '1d': '1D',
                '1w': '7D',
                '2w': '14D',
                '1M': '1M',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766244-e328a50c-5ed2-11e7-947b-041416579bb3.jpg',
                'api': 'https://api.bitfinex.com',
                'www': 'https://www.bitfinex.com',
                'doc': [
                    'https://bitfinex.readme.io/v1/docs',
                    'https://github.com/bitfinexcom/bitfinex-api-node',
                ],
            },
            'api': {
                'v2': {
                    'get': [
                        'candles/trade:{timeframe}:{symbol}/{section}',
                        'candles/trade:{timeframe}:{symbol}/last',
                        'candles/trade:{timeframe}:{symbol}/hist',
                    ],
                },
                'public': {
                    'get': [
                        'book/{symbol}',
                        # 'candles/{symbol}',
                        'lendbook/{currency}',
                        'lends/{currency}',
                        'pubticker/{symbol}',
                        'stats/{symbol}',
                        'symbols',
                        'symbols_details',
                        'today',
                        'trades/{symbol}',
                    ],
                },
                'private': {
                    'post': [
                        'account_infos',
                        'balances',
                        'basket_manage',
                        'credits',
                        'deposit/new',
                        'funding/close',
                        'history',
                        'history/movements',
                        'key_info',
                        'margin_infos',
                        'mytrades',
                        'mytrades_funding',
                        'offer/cancel',
                        'offer/new',
                        'offer/status',
                        'offers',
                        'offers/hist',
                        'order/cancel',
                        'order/cancel/all',
                        'order/cancel/multi',
                        'order/cancel/replace',
                        'order/new',
                        'order/new/multi',
                        'order/status',
                        'orders',
                        'orders/hist',
                        'position/claim',
                        'positions',
                        'summary',
                        'taken_funds',
                        'total_taken_funds',
                        'transfer',
                        'unused_taken_funds',
                        'withdraw',
                    ],
                },
            },
        }
        params.update(config)
        super(bitfinex, self).__init__(params)

    def common_currency_code(self, currency):
        # issue  #4 Bitfinex names Dash as DSH, instead of DASH
        if currency == 'DSH':
            return 'DASH'
        if currency == 'QTM':
            return 'QTUM'
        return currency

    def fetch_markets(self):
        markets = self.publicGetSymbolsDetails()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['pair'].upper()
            baseId = id[0:3]
            quoteId = id[3:6]
            base = self.common_currency_code(baseId)
            quote = self.common_currency_code(quoteId)
            symbol = base + '/' + quote
            precision = {
                'price': market['price_precision'],
            }
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'info': market,
                'precision': precision,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privatePostBalances()
        result = {'info': balances}
        for i in range(0, len(balances)):
            balance = balances[i]
            if balance['type'] == 'exchange':
                currency = balance['currency']
                uppercase = currency.upper()
                uppercase = self.common_currency_code(uppercase)
                account = self.account()
                account['free'] = float(balance['available'])
                account['total'] = float(balance['amount'])
                account['used'] = account['total'] - account['free']
                result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetBookSymbol(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        ticker = self.publicGetPubtickerSymbol(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        timestamp = float(ticker['timestamp']) * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last_price']),
            'change': None,
            'percentage': None,
            'average': float(ticker['mid']),
            'baseVolume': float(ticker['volume']),
            'quoteVolume': None,
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['timestamp'] * 1000
        return {
            'id': str(trade['tid']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTradesSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        orderType = type
        if (type == 'limit') or (type == 'market'):
            orderType = 'exchange ' + type
        order = {
            'symbol': self.market_id(symbol),
            'amount': str(amount),
            'side': side,
            'type': orderType,
            'ocoorder': False,
            'buy_price_oco': 0,
            'sell_price_oco': 0,
        }
        if type == 'market':
            order['price'] = str(self.nonce())
        else:
            order['price'] = str(price)
        result = self.privatePostOrderNew(self.extend(order, params))
        return {
            'info': result,
            'id': str(result['order_id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostOrderCancel({'order_id': int(id)})

    def parse_order(self, order, market=None):
        side = order['side']
        open = order['is_live']
        canceled = order['is_cancelled']
        status = None
        if open:
            status = 'open'
        elif canceled:
            status = 'canceled'
        else:
            status = 'closed'
        symbol = None
        if not market:
            exchange = order['symbol'].upper()
            if exchange in self.markets_by_id:
                market = self.markets_by_id[exchange]
        if market:
            symbol = market['symbol']
        orderType = order['type']
        exchange = orderType.find('exchange ') >= 0
        if exchange:
            prefix, orderType = order['type'].split(' ')
        timestamp = int(float(order['timestamp']) * 1000)
        result = {
            'info': order,
            'id': str(order['id']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': orderType,
            'side': side,
            'price': float(order['price']),
            'average': float(order['avg_execution_price']),
            'amount': float(order['original_amount']),
            'remaining': float(order['remaining_amount']),
            'filled': float(order['executed_amount']),
            'status': status,
            'fee': None,
        }
        return result

    def fetch_open_orders(self, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostOrders(params)
        return self.parse_orders(response)

    def fetchClosedOrders(self, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostOrdersHist(self.extend({
            'limit': 100,  # default 100
        }, params))
        return self.parse_orders(response)

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostOrderStatus(self.extend({
            'order_id': int(id),
        }, params))
        return self.parse_order(response)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv[0],
            ohlcv[1],
            ohlcv[3],
            ohlcv[4],
            ohlcv[2],
            ohlcv[5],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        market = self.market(symbol)
        v2id = 't' + market['id']
        request = {
            'symbol': v2id,
            'timeframe': self.timeframes[timeframe],
        }
        if limit:
            request['limit'] = limit
        if since:
            request['start'] = since
        request = self.extend(request, params)
        response = self.v2GetCandlesTradeTimeframeSymbolHist(request)
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def getCurrencyName(self, currency):
        if currency == 'BTC':
            return 'bitcoin'
        elif currency == 'LTC':
            return 'litecoin'
        elif currency == 'ETH':
            return 'ethereum'
        elif currency == 'ETC':
            return 'ethereumc'
        elif currency == 'OMNI':
            return 'mastercoin'  # ???
        elif currency == 'ZEC':
            return 'zcash'
        elif currency == 'XMR':
            return 'monero'
        elif currency == 'USD':
            return 'wire'
        elif currency == 'DASH':
            return 'dash'
        elif currency == 'XRP':
            return 'ripple'
        elif currency == 'EOS':
            return 'eos'
        raise NotSupported(self.id + ' ' + currency + ' not supported for withdrawal')

    def deposit(self, currency, params={}):
        self.load_markets()
        name = self.getCurrencyName(currency)
        request = {
            'method': name,
            'wallet_name': 'exchange',
            'renew': 0,  # a value of 1 will generate a new address
        }
        response = self.privatePostDepositNew(self.extend(request, params))
        return {
            'info': response,
            'address': response['address'],
        }

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        name = self.getCurrencyName(currency)
        request = {
            'withdraw_type': name,
            'walletselected': 'exchange',
            'amount': str(amount),
            'address': address,
        }
        responses = self.privatePostWithdraw(self.extend(request, params))
        response = responses[0]
        return {
            'info': response,
            'id': response['withdrawal_id'],
        }

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = '/' + self.implode_params(path, params)
        if api == 'v2':
            request = '/' + api + request
        else:
            request = '/' + self.version + request
        query = self.omit(params, self.extract_params(path))
        url = self.urls['api'] + request
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            query = self.extend({
                'nonce': str(nonce),
                'request': request,
            }, query)
            query = self.json(query)
            query = self.encode(query)
            payload = base64.b64encode(query)
            secret = self.encode(self.secret)
            signature = self.hmac(payload, secret, hashlib.sha384)
            headers = {
                'X-BFX-APIKEY': self.apiKey,
                'X-BFX-PAYLOAD': self.decode(payload),
                'X-BFX-SIGNATURE': signature,
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'message' in response:
            if response['message'].find('not enough exchange balance') >= 0:
                raise InsufficientFunds(self.id + ' ' + self.json(response))
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class bitfinex2 (bitfinex):

    def __init__(self, config={}):
        params = {
            'id': 'bitfinex2',
            'name': 'Bitfinex v2',
            'countries': 'US',
            'version': 'v2',
            'hasCORS': True,
            'hasFetchTickers': False,  # True but at least one pair is required
            'hasFetchOHLCV': True,
            'timeframes': {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '3h': '3h',
                '6h': '6h',
                '12h': '12h',
                '1d': '1D',
                '1w': '7D',
                '2w': '14D',
                '1M': '1M',
            },
            'rateLimit': 1500,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766244-e328a50c-5ed2-11e7-947b-041416579bb3.jpg',
                'api': 'https://api.bitfinex.com',
                'www': 'https://www.bitfinex.com',
                'doc': [
                    'https://bitfinex.readme.io/v2/docs',
                    'https://github.com/bitfinexcom/bitfinex-api-node',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'platform/status',
                        'tickers',  # replies with an empty list :\
                        'ticker/{symbol}',
                        'trades/{symbol}/hist',
                        'book/{symbol}/{precision}',
                        'book/{symbol}/P0',
                        'book/{symbol}/P1',
                        'book/{symbol}/P2',
                        'book/{symbol}/P3',
                        'book/{symbol}/R0',
                        'symbols_details',
                        'stats1/{key}:{size}:{symbol}/{side}/{section}',
                        'stats1/{key}:{size}:{symbol}/long/last',
                        'stats1/{key}:{size}:{symbol}/long/hist',
                        'stats1/{key}:{size}:{symbol}/short/last',
                        'stats1/{key}:{size}:{symbol}/short/hist',
                        'candles/trade:{timeframe}:{symbol}/{section}',
                        'candles/trade:{timeframe}:{symbol}/last',
                        'candles/trade:{timeframe}:{symbol}/hist',
                    ],
                    'post': [
                        'calc/trade/avg',
                    ],
                },
                'private': {
                    'post': [
                        'auth/r/wallets',
                        'auth/r/orders/{symbol}',
                        'auth/r/orders/{symbol}/new',
                        'auth/r/orders/{symbol}/hist',
                        'auth/r/order/{symbol}:{id}/trades',
                        'auth/r/trades/{symbol}/hist',
                        'auth/r/funding/offers/{symbol}',
                        'auth/r/funding/offers/{symbol}/hist',
                        'auth/r/funding/loans/{symbol}',
                        'auth/r/funding/loans/{symbol}/hist',
                        'auth/r/funding/credits/{symbol}',
                        'auth/r/funding/credits/{symbol}/hist',
                        'auth/r/funding/trades/{symbol}/hist',
                        'auth/r/info/margin/{key}',
                        'auth/r/info/funding/{key}',
                        'auth/r/movements/{currency}/hist',
                        'auth/r/stats/perf:{timeframe}/hist',
                        'auth/r/alerts',
                        'auth/w/alert/set',
                        'auth/w/alert/{type}:{symbol}:{price}/del',
                        'auth/calc/order/avail',
                    ],
                },
            },
            'markets': {
                'BCC/BTC': {'id': 'tBCCBTC', 'symbol': 'BCC/BTC', 'base': 'BCC', 'quote': 'BTC'},
                'BCC/USD': {'id': 'tBCCUSD', 'symbol': 'BCC/USD', 'base': 'BCC', 'quote': 'USD'},
                'BCH/BTC': {'id': 'tBCHBTC', 'symbol': 'BCH/BTC', 'base': 'BCH', 'quote': 'BTC'},
                'BCH/ETH': {'id': 'tBCHETH', 'symbol': 'BCH/ETH', 'base': 'BCH', 'quote': 'ETH'},
                'BCH/USD': {'id': 'tBCHUSD', 'symbol': 'BCH/USD', 'base': 'BCH', 'quote': 'USD'},
                'BCU/BTC': {'id': 'tBCUBTC', 'symbol': 'BCU/BTC', 'base': 'BCU', 'quote': 'BTC'},
                'BCU/USD': {'id': 'tBCUUSD', 'symbol': 'BCU/USD', 'base': 'BCU', 'quote': 'USD'},
                'BTC/USD': {'id': 'tBTCUSD', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'DASH/BTC': {'id': 'tDSHBTC', 'symbol': 'DASH/BTC', 'base': 'DASH', 'quote': 'BTC'},
                'DASH/USD': {'id': 'tDSHUSD', 'symbol': 'DASH/USD', 'base': 'DASH', 'quote': 'USD'},
                'EOS/BTC': {'id': 'tEOSBTC', 'symbol': 'EOS/BTC', 'base': 'EOS', 'quote': 'BTC'},
                'EOS/ETH': {'id': 'tEOSETH', 'symbol': 'EOS/ETH', 'base': 'EOS', 'quote': 'ETH'},
                'EOS/USD': {'id': 'tEOSUSD', 'symbol': 'EOS/USD', 'base': 'EOS', 'quote': 'USD'},
                'ETC/BTC': {'id': 'tETCBTC', 'symbol': 'ETC/BTC', 'base': 'ETC', 'quote': 'BTC'},
                'ETC/USD': {'id': 'tETCUSD', 'symbol': 'ETC/USD', 'base': 'ETC', 'quote': 'USD'},
                'ETH/BTC': {'id': 'tETHBTC', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
                'ETH/USD': {'id': 'tETHUSD', 'symbol': 'ETH/USD', 'base': 'ETH', 'quote': 'USD'},
                'IOT/BTC': {'id': 'tIOTBTC', 'symbol': 'IOT/BTC', 'base': 'IOT', 'quote': 'BTC'},
                'IOT/ETH': {'id': 'tIOTETH', 'symbol': 'IOT/ETH', 'base': 'IOT', 'quote': 'ETH'},
                'IOT/USD': {'id': 'tIOTUSD', 'symbol': 'IOT/USD', 'base': 'IOT', 'quote': 'USD'},
                'LTC/BTC': {'id': 'tLTCBTC', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'LTC/USD': {'id': 'tLTCUSD', 'symbol': 'LTC/USD', 'base': 'LTC', 'quote': 'USD'},
                'OMG/BTC': {'id': 'tOMGBTC', 'symbol': 'OMG/BTC', 'base': 'OMG', 'quote': 'BTC'},
                'OMG/ETH': {'id': 'tOMGETH', 'symbol': 'OMG/ETH', 'base': 'OMG', 'quote': 'ETH'},
                'OMG/USD': {'id': 'tOMGUSD', 'symbol': 'OMG/USD', 'base': 'OMG', 'quote': 'USD'},
                'RRT/BTC': {'id': 'tRRTBTC', 'symbol': 'RRT/BTC', 'base': 'RRT', 'quote': 'BTC'},
                'RRT/USD': {'id': 'tRRTUSD', 'symbol': 'RRT/USD', 'base': 'RRT', 'quote': 'USD'},
                'SAN/BTC': {'id': 'tSANBTC', 'symbol': 'SAN/BTC', 'base': 'SAN', 'quote': 'BTC'},
                'SAN/ETH': {'id': 'tSANETH', 'symbol': 'SAN/ETH', 'base': 'SAN', 'quote': 'ETH'},
                'SAN/USD': {'id': 'tSANUSD', 'symbol': 'SAN/USD', 'base': 'SAN', 'quote': 'USD'},
                'XMR/BTC': {'id': 'tXMRBTC', 'symbol': 'XMR/BTC', 'base': 'XMR', 'quote': 'BTC'},
                'XMR/USD': {'id': 'tXMRUSD', 'symbol': 'XMR/USD', 'base': 'XMR', 'quote': 'USD'},
                'XRP/BTC': {'id': 'tXRPBTC', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC'},
                'XRP/USD': {'id': 'tXRPUSD', 'symbol': 'XRP/USD', 'base': 'XRP', 'quote': 'USD'},
                'ZEC/BTC': {'id': 'tZECBTC', 'symbol': 'ZEC/BTC', 'base': 'ZEC', 'quote': 'BTC'},
                'ZEC/USD': {'id': 'tZECUSD', 'symbol': 'ZEC/USD', 'base': 'ZEC', 'quote': 'USD'},
            },
        }
        params.update(config)
        super(bitfinex2, self).__init__(params)

    def common_currency_code(self, currency):
        # issue  #4 Bitfinex names Dash as DSH, instead of DASH
        if currency == 'DSH':
            return 'DASH'
        if currency == 'QTM':
            return 'QTUM'
        return currency

    def fetch_balance(self, params={}):
        response = self.privatePostAuthRWallets()
        result = {'info': response}
        for b in range(0, len(response)):
            balance = response[b]
            type, currency, total, interest, available = balance
            if currency[0] == 't':
                currency = currency[1:]
            uppercase = currency.upper()
            uppercase = self.common_currency_code(uppercase)
            account = self.account()
            account['free'] = available
            account['total'] = total
            if account['free']:
                account['used'] = account['total'] - account['free']
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetBookSymbolPrecision(self.extend({
            'symbol': self.market_id(symbol),
            'precision': 'R0',
        }, params))
        timestamp = self.milliseconds()
        result = {
            'bids': [],
            'asks': [],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
        }
        for i in range(0, len(orderbook)):
            order = orderbook[i]
            price = order[1]
            amount = order[2]
            side = 'bids' if (amount > 0) else 'asks'
            amount = abs(amount)
            result[side].append([price, amount])
        result['bids'] = self.sort_by(result['bids'], 0, True)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetTickerSymbol(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        timestamp = self.milliseconds()
        bid, bidSize, ask, askSize, change, percentage, last, volume, high, low = ticker
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': high,
            'low': low,
            'bid': bid,
            'ask': ask,
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': last,
            'change': change,
            'percentage': percentage,
            'average': None,
            'baseVolume': volume,
            'quoteVolume': None,
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        id, timestamp, amount, price = trade
        side = 'sell' if (amount < 0) else 'buy'
        return {
            'id': str(id),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': side,
            'price': price,
            'amount': amount,
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTradesSymbolHist(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'timeframe': self.timeframes[timeframe],
        }
        if limit:
            request['limit'] = limit
        if since:
            request['start'] = since
        request = self.extend(request, params)
        response = self.publicGetCandlesTradeTimeframeSymbolHist(request)
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        raise NotSupported(self.id + ' createOrder not implemented yet')

    def cancel_order(self, id, symbol=None, params={}):
        raise NotSupported(self.id + ' cancelOrder not implemented yet')

    def fetch_order(self, id, symbol=None, params={}):
        raise NotSupported(self.id + ' fetchOrder not implemented yet')

    def withdraw(self, currency, amount, address, params={}):
        raise NotSupported(self.id + ' withdraw not implemented yet')

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        url = self.urls['api'] + '/' + request
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = str(self.nonce())
            body = self.json(query)
            auth = '/api' + '/' + request + nonce + body
            signature = self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha384)
            headers = {
                'bfx-nonce': nonce,
                'bfx-apikey': self.apiKey,
                'bfx-signature': signature,
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if response:
            if 'message' in response:
                if response['message'].find('not enough exchange balance') >= 0:
                    raise InsufficientFunds(self.id + ' ' + self.json(response))
                raise ExchangeError(self.id + ' ' + self.json(response))
            return response
        raise ExchangeError(self.id + ' returned empty response')

# -----------------------------------------------------------------------------


class bitflyer (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitflyer',
            'name': 'bitFlyer',
            'countries': 'JP',
            'version': 'v1',
            'rateLimit': 500,
            'hasCORS': False,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28051642-56154182-660e-11e7-9b0d-6042d1e6edd8.jpg',
                'api': 'https://api.bitflyer.jp',
                'www': 'https://bitflyer.jp',
                'doc': 'https://bitflyer.jp/API',
            },
            'api': {
                'public': {
                    'get': [
                        'getmarkets',    # or 'markets'
                        'getboard',      # or 'board'
                        'getticker',     # or 'ticker'
                        'getexecutions',  # or 'executions'
                        'gethealth',
                        'getchats',
                    ],
                },
                'private': {
                    'get': [
                        'getpermissions',
                        'getbalance',
                        'getcollateral',
                        'getcollateralaccounts',
                        'getaddresses',
                        'getcoinins',
                        'getcoinouts',
                        'getbankaccounts',
                        'getdeposits',
                        'getwithdrawals',
                        'getchildorders',
                        'getparentorders',
                        'getparentorder',
                        'getexecutions',
                        'getpositions',
                        'gettradingcommission',
                    ],
                    'post': [
                        'sendcoin',
                        'withdraw',
                        'sendchildorder',
                        'cancelchildorder',
                        'sendparentorder',
                        'cancelparentorder',
                        'cancelallchildorders',
                    ],
                },
            },
        }
        params.update(config)
        super(bitflyer, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetMarkets()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['product_code']
            currencies = id.split('_')
            base = None
            quote = None
            symbol = id
            numCurrencies = len(currencies)
            if numCurrencies == 1:
                base = symbol[0:3]
                quote = symbol[3:6]
            elif numCurrencies == 2:
                base = currencies[0]
                quote = currencies[1]
                symbol = base + '/' + quote
            else:
                base = currencies[1]
                quote = currencies[2]
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalance()
        balances = {}
        for b in range(0, len(response)):
            account = response[b]
            currency = account['currency_code']
            balances[currency] = account
        result = {'info': response}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in balances:
                account['total'] = balances[currency]['amount']
                account['free'] = balances[currency]['available']
                account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetBoard(self.extend({
            'product_code': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'size')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        ticker = self.publicGetTicker(self.extend({
            'product_code': self.market_id(symbol),
        }, params))
        timestamp = self.parse8601(ticker['timestamp'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['best_bid']),
            'ask': float(ticker['best_ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['ltp']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['volume_by_product']),
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        side = None
        order = None
        if 'side' in trade:
            if trade['side']:
                side = trade['side'].lower()
                id = side + '_child_order_acceptance_id'
                if id in trade:
                    order = trade[id]
        timestamp = self.parse8601(trade['exec_date'])
        return {
            'id': str(trade['id']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': order,
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['size'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetExecutions(self.extend({
            'product_code': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'product_code': self.market_id(symbol),
            'child_order_type': type.upper(),
            'side': side.upper(),
            'price': price,
            'size': amount,
        }
        result = self.privatePostSendchildorder(self.extend(order, params))
        return {
            'info': result,
            'id': result['child_order_acceptance_id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostCancelchildorder(self.extend({
            'parent_order_id': id,
        }, params))

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        response = self.privatePostWithdraw(self.extend({
            'currency_code': currency,
            'amount': amount,
            # 'bank_account_id': 1234,
        }, params))
        return {
            'info': response,
            'id': response['message_id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = '/' + self.version + '/'
        if api == 'private':
            request += 'me/'
        request += path
        if method == 'GET':
            if params:
                request += '?' + self.urlencode(params)
        url = self.urls['api'] + request
        if api == 'private':
            nonce = str(self.nonce())
            body = self.json(params)
            auth = ''.join([nonce, method, request, body])
            headers = {
                'ACCESS-KEY': self.apiKey,
                'ACCESS-TIMESTAMP': nonce,
                'ACCESS-SIGN': self.hmac(self.encode(auth), self.encode(self.secret)),
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class bithumb (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bithumb',
            'name': 'Bithumb',
            'countries': 'KR',  # South Korea
            'rateLimit': 500,
            'hasCORS': True,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30597177-ea800172-9d5e-11e7-804c-b9d4fa9b56b0.jpg',
                'api': {
                    'public': 'https://api.bithumb.com/public',
                    'private': 'https://api.bithumb.com',
                },
                'www': 'https://www.bithumb.com',
                'doc': 'https://www.bithumb.com/u1/US127',
            },
            'api': {
                'public': {
                    'get': [
                        'ticker/{currency}',
                        'ticker/all',
                        'orderbook/{currency}',
                        'orderbook/all',
                        'recent_transactions/{currency}',
                        'recent_transactions/all',
                    ],
                },
                'private': {
                    'post': [
                        'info/account',
                        'info/balance',
                        'info/wallet_address',
                        'info/ticker',
                        'info/orders',
                        'info/user_transactions',
                        'trade/place',
                        'info/order_detail',
                        'trade/cancel',
                        'trade/btc_withdrawal',
                        'trade/krw_deposit',
                        'trade/krw_withdrawal',
                        'trade/market_buy',
                        'trade/market_sell',
                    ],
                },
            },
            'markets': {
                'BTC/KRW': {'id': 'BTC', 'symbol': 'BTC/KRW', 'base': 'BTC', 'quote': 'KRW'},
                'ETH/KRW': {'id': 'ETH', 'symbol': 'ETH/KRW', 'base': 'ETH', 'quote': 'KRW'},
                'LTC/KRW': {'id': 'LTC', 'symbol': 'LTC/KRW', 'base': 'LTC', 'quote': 'KRW'},
                'ETC/KRW': {'id': 'ETC', 'symbol': 'ETC/KRW', 'base': 'ETC', 'quote': 'KRW'},
                'XRP/KRW': {'id': 'XRP', 'symbol': 'XRP/KRW', 'base': 'XRP', 'quote': 'KRW'},
                'BCH/KRW': {'id': 'BCH', 'symbol': 'BCH/KRW', 'base': 'BCH', 'quote': 'KRW'},
                'XMR/KRW': {'id': 'XMR', 'symbol': 'XMR/KRW', 'base': 'XMR', 'quote': 'KRW'},
                'ZEC/KRW': {'id': 'ZEC', 'symbol': 'ZEC/KRW', 'base': 'ZEC', 'quote': 'KRW'},
                'DASH/KRW': {'id': 'DASH', 'symbol': 'DASH/KRW', 'base': 'DASH', 'quote': 'KRW'},
                'QTUM/KRW': {'id': 'QTUM', 'symbol': 'QTUM/KRW', 'base': 'QTUM', 'quote': 'KRW'},
            },
        }
        params.update(config)
        super(bithumb, self).__init__(params)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostInfoBalance(self.extend({
            'currency': 'ALL',
        }, params))
        result = {'info': response}
        balances = response['data']
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            lowercase = currency.lower()
            account['total'] = self.safe_float(balances, 'total_' + lowercase)
            account['used'] = self.safe_float(balances, 'in_use_' + lowercase)
            account['free'] = self.safe_float(balances, 'available_' + lowercase)
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetOrderbookCurrency(self.extend({
            'count': 50,  # max = 50
            'currency': market['base'],
        }, params))
        orderbook = response['data']
        timestamp = int(orderbook['timestamp'])
        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'quantity')

    def parse_ticker(self, ticker, market=None):
        timestamp = int(ticker['date'])
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'max_price'),
            'low': self.safe_float(ticker, 'min_price'),
            'bid': self.safe_float(ticker, 'buy_price'),
            'ask': self.safe_float(ticker, 'sell_price'),
            'vwap': None,
            'open': self.safe_float(ticker, 'opening_price'),
            'close': self.safe_float(ticker, 'closing_price'),
            'first': None,
            'last': self.safe_float(ticker, 'last_trade'),
            'change': None,
            'percentage': None,
            'average': self.safe_float(ticker, 'average_price'),
            'baseVolume': None,
            'quoteVolume': self.safe_float(ticker, 'volume_1day'),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        response = self.publicGetTickerAll(params)
        result = {}
        timestamp = response['data']['date']
        tickers = self.omit(response['data'], 'date')
        ids = list(tickers.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            ticker['date'] = timestamp
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTickerCurrency(self.extend({
            'currency': market['base'],
        }, params))
        return self.parse_ticker(response['data'], market)

    def parse_trade(self, trade, market):
        # a workaround for their bug in date format, hours are not 0-padded
        transaction_date, transaction_time = trade['transaction_date'].split(' ')
        transaction_time_short = len(transaction_time) < 8
        if transaction_time_short:
            transaction_time = '0' + transaction_time
        timestamp = self.parse8601(transaction_date + ' ' + transaction_time)
        side = 'sell' if (trade['type'] == 'ask') else 'buy'
        return {
            'id': None,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': None,
            'type': None,
            'side': side,
            'price': float(trade['price']),
            'amount': float(trade['units_traded']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetRecentTransactionsCurrency(self.extend({
            'currency': market['base'],
            'count': 100,  # max = 100
        }, params))
        return self.parse_trades(response['data'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        raise NotSupported(self.id + ' private API not implemented yet')
        #     prefix = ''
        #     if type == 'market':
        #         prefix = 'market_'
        #     order = {
        #         'pair': self.market_id(symbol),
        #         'quantity': amount,
        #         'price': price or 0,
        #         'type': prefix + side,
        #     }
        #     response = self.privatePostOrderCreate(self.extend(order, params))
        #     return {
        #         'info': response,
        #         'id': str(response['order_id']),
        #     }

    def cancel_order(self, id, symbol=None, params={}):
        side = ('side' in list(params.keys()))
        if not side:
            raise ExchangeError(self.id + ' cancelOrder requires a side parameter(sell or buy)')
        side = 'purchase' if (side == 'buy') else 'sales'
        currency = ('currency' in list(params.keys()))
        if not currency:
            raise ExchangeError(self.id + ' cancelOrder requires a currency parameter')
        return self.privatePostTradeCancel({
            'order_id': id,
            'type': params['side'],
            'currency': params['currency'],
        })

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        endpoint = '/' + self.implode_params(path, params)
        url = self.urls['api'][api] + endpoint
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            body = self.urlencode(self.extend({
                'endpoint': endpoint,
            }, query))
            nonce = str(self.nonce())
            auth = endpoint + "\0" + body + "\0" + nonce
            signature = self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha512)
            headers = {
                'Api-Key': self.apiKey,
                'Api-Sign': base64.b64encode(self.encode(signature)),
                'Api-Nonce': nonce,
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] == '0000':
                return response
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class bitlish (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitlish',
            'name': 'bitlish',
            'countries': ['GB', 'EU', 'RU'],
            'rateLimit': 1500,
            'version': 'v1',
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasFetchOHLCV': True,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766275-dcfc6c30-5ed3-11e7-839d-00a846385d0b.jpg',
                'api': 'https://bitlish.com/api',
                'www': 'https://bitlish.com',
                'doc': 'https://bitlish.com/api',
            },
            'api': {
                'public': {
                    'get': [
                        'instruments',
                        'ohlcv',
                        'pairs',
                        'tickers',
                        'trades_depth',
                        'trades_history',
                    ],
                    'post': [
                        'instruments',
                        'ohlcv',
                        'pairs',
                        'tickers',
                        'trades_depth',
                        'trades_history',
                    ],
                },
                'private': {
                    'post': [
                        'accounts_operations',
                        'balance',
                        'cancel_trade',
                        'cancel_trades_by_ids',
                        'cancel_all_trades',
                        'create_bcode',
                        'create_template_wallet',
                        'create_trade',
                        'deposit',
                        'list_accounts_operations_from_ts',
                        'list_active_trades',
                        'list_bcodes',
                        'list_my_matches_from_ts',
                        'list_my_trades',
                        'list_my_trads_from_ts',
                        'list_payment_methods',
                        'list_payments',
                        'redeem_code',
                        'resign',
                        'signin',
                        'signout',
                        'trade_details',
                        'trade_options',
                        'withdraw',
                        'withdraw_by_id',
                    ],
                },
            },
        }
        params.update(config)
        super(bitlish, self).__init__(params)

    def common_currency_code(self, currency):
        if not self.substituteCommonCurrencyCodes:
            return currency
        if currency == 'XBT':
            return 'BTC'
        if currency == 'BCC':
            return 'BCH'
        if currency == 'DRK':
            return 'DASH'
        if currency == 'DSH':
            currency = 'DASH'
        return currency

    def fetch_markets(self):
        markets = self.publicGetPairs()
        result = []
        keys = list(markets.keys())
        for p in range(0, len(keys)):
            market = markets[keys[p]]
            id = market['id']
            symbol = market['name']
            base, quote = symbol.split('/')
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def parse_ticker(self, ticker, market):
        timestamp = self.milliseconds()
        return {
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['max']),
            'low': float(ticker['min']),
            'bid': float(ticker['min']),
            'ask': float(ticker['max']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': float(ticker['first']),
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTickers(params)
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        tickers = self.publicGetTickers(params)
        ticker = tickers[market['id']]
        return self.parse_ticker(ticker, market)

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        # market = self.market(symbol)
        now = self.seconds()
        start = now - 86400 * 30  # last 30 days
        interval = [str(start), None]
        return self.publicPostOhlcv(self.extend({
            'time_range': interval,
        }, params))

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetTradesDepth(self.extend({
            'pair_id': self.market_id(symbol),
        }, params))
        timestamp = int(int(orderbook['last']) / 1000)
        return self.parse_order_book(orderbook, timestamp, 'bid', 'ask', 'price', 'volume')

    def parse_trade(self, trade, market=None):
        side = 'buy' if (trade['dir'] == 'bid') else 'sell'
        symbol = None
        if market:
            symbol = market['symbol']
        timestamp = int(trade['created'] / 1000)
        return {
            'id': None,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': None,
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTradesHistory(self.extend({
            'pair_id': market['id'],
        }, params))
        return self.parse_trades(response['list'], market)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostBalance()
        result = {'info': response}
        currencies = list(response.keys())
        balance = {}
        for c in range(0, len(currencies)):
            currency = currencies[c]
            account = response[currency]
            currency = currency.upper()
            # issue  #4 bitlish names Dash as DSH, instead of DASH
            if currency == 'DSH':
                currency = 'DASH'
            balance[currency] = account
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in balance:
                account['free'] = float(balance[currency]['funds'])
                account['used'] = float(balance[currency]['holded'])
                account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def sign_in(self):
        return self.privatePostSignin({
            'login': self.login,
            'passwd': self.password,
        })

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'pair_id': self.market_id(symbol),
            'dir': 'bid' if (side == 'buy') else 'ask',
            'amount': amount,
        }
        if type == 'limit':
            order['price'] = price
        result = self.privatePostCreateTrade(self.extend(order, params))
        return {
            'info': result,
            'id': result['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostCancelTrade({'id': id})

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        if currency != 'BTC':
            # they did not document other types...
            raise NotSupported(self.id + ' currently supports BTC withdrawals only, until they document other currencies...')
        response = self.privatePostWithdraw(self.extend({
            'currency': currency.lower(),
            'amount': float(amount),
            'account': address,
            'payment_method': 'bitcoin',  # they did not document other types...
        }, params))
        return {
            'info': response,
            'id': response['message_id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if method == 'GET':
                if params:
                    url += '?' + self.urlencode(params)
            else:
                body = self.json(params)
                headers = {'Content-Type': 'application/json'}
        else:
            body = self.json(self.extend({'token': self.apiKey}, params))
            headers = {'Content-Type': 'application/json'}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class bitmarket (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitmarket',
            'name': 'BitMarket',
            'countries': ['PL', 'EU'],
            'rateLimit': 1500,
            'hasCORS': False,
            'hasFetchOHLCV': True,
            'hasWithdraw': True,
            'timeframes': {
                '90m': '90m',
                '6h': '6h',
                '1d': '1d',
                '1w': '7d',
                '1M': '1m',
                '3M': '3m',
                '6M': '6m',
                '1y': '1y',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27767256-a8555200-5ef9-11e7-96fd-469a65e2b0bd.jpg',
                'api': {
                    'public': 'https://www.bitmarket.net',
                    'private': 'https://www.bitmarket.pl/api2/',  # last slash is critical
                },
                'www': [
                    'https://www.bitmarket.pl',
                    'https://www.bitmarket.net',
                ],
                'doc': [
                    'https://www.bitmarket.net/docs.php?file=api_public.html',
                    'https://www.bitmarket.net/docs.php?file=api_private.html',
                    'https://github.com/bitmarket-net/api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'json/{market}/ticker',
                        'json/{market}/orderbook',
                        'json/{market}/trades',
                        'json/ctransfer',
                        'graphs/{market}/90m',
                        'graphs/{market}/6h',
                        'graphs/{market}/1d',
                        'graphs/{market}/7d',
                        'graphs/{market}/1m',
                        'graphs/{market}/3m',
                        'graphs/{market}/6m',
                        'graphs/{market}/1y',
                    ],
                },
                'private': {
                    'post': [
                        'info',
                        'trade',
                        'cancel',
                        'orders',
                        'trades',
                        'history',
                        'withdrawals',
                        'tradingdesk',
                        'tradingdeskStatus',
                        'tradingdeskConfirm',
                        'cryptotradingdesk',
                        'cryptotradingdeskStatus',
                        'cryptotradingdeskConfirm',
                        'withdraw',
                        'withdrawFiat',
                        'withdrawPLNPP',
                        'withdrawFiatFast',
                        'deposit',
                        'transfer',
                        'transfers',
                        'marginList',
                        'marginOpen',
                        'marginClose',
                        'marginCancel',
                        'marginModify',
                        'marginBalanceAdd',
                        'marginBalanceRemove',
                        'swapList',
                        'swapOpen',
                        'swapClose',
                    ],
                },
            },
            'markets': {
                'BTC/PLN': {'id': 'BTCPLN', 'symbol': 'BTC/PLN', 'base': 'BTC', 'quote': 'PLN'},
                'BTC/EUR': {'id': 'BTCEUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                'LTC/PLN': {'id': 'LTCPLN', 'symbol': 'LTC/PLN', 'base': 'LTC', 'quote': 'PLN'},
                'LTC/BTC': {'id': 'LTCBTC', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'LiteMineX/BTC': {'id': 'LiteMineXBTC', 'symbol': 'LiteMineX/BTC', 'base': 'LiteMineX', 'quote': 'BTC'},
                'PlnX/BTC': {'id': 'PlnxBTC', 'symbol': 'PlnX/BTC', 'base': 'PlnX', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(bitmarket, self).__init__(params)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostInfo()
        data = response['data']
        balance = data['balances']
        result = {'info': data}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in balance['available']:
                account['free'] = balance['available'][currency]
            if currency in balance['blocked']:
                account['used'] = balance['blocked'][currency]
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetJsonMarketOrderbook(self.extend({
            'market': self.market_id(symbol),
        }, params))
        timestamp = self.milliseconds()
        return {
            'bids': orderbook['bids'],
            'asks': orderbook['asks'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
        }

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetJsonMarketTicker(self.extend({
            'market': self.market_id(symbol),
        }, params))
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': float(ticker['vwap']),
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        side = 'buy' if (trade['type'] == 'bid') else 'sell'
        timestamp = trade['date'] * 1000
        return {
            'id': str(trade['tid']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': None,
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetJsonMarketTrades(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='90m', since=None, limit=None):
        return [
            ohlcv['time'] * 1000,
            float(ohlcv['open']),
            float(ohlcv['high']),
            float(ohlcv['low']),
            float(ohlcv['close']),
            float(ohlcv['vol']),
        ]

    def fetch_ohlcv(self, symbol, timeframe='90m', since=None, limit=None, params={}):
        self.load_markets()
        method = 'publicGetGraphsMarket' + self.timeframes[timeframe]
        market = self.market(symbol)
        response = getattr(self, method)(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        response = self.privatePostTrade(self.extend({
            'market': self.market_id(symbol),
            'type': side,
            'amount': amount,
            'rate': price,
        }, params))
        result = {
            'info': response,
        }
        if 'id' in response['order']:
            result['id'] = response['id']
        return result

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancel({'id': id})

    def isFiat(self, currency):
        if currency == 'EUR':
            return True
        if currency == 'PLN':
            return True
        return False

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        method = None
        request = {
            'currency': currency,
            'quantity': amount,
        }
        if self.isFiat(currency):
            method = 'privatePostWithdrawFiat'
            if 'account' in params:
                request['account'] = params['account']  # bank account code for withdrawal
            else:
                raise ExchangeError(self.id + ' requires account parameter to withdraw fiat currency')
            if 'account2' in params:
                request['account2'] = params['account2']  # bank SWIFT code(EUR only)
            else:
                if currency == 'EUR':
                    raise ExchangeError(self.id + ' requires account2 parameter to withdraw EUR')
            if 'withdrawal_note' in params:
                request['withdrawal_note'] = params['withdrawal_note']  # a 10-character user-specified withdrawal note(PLN only)
            else:
                if currency == 'PLN':
                    raise ExchangeError(self.id + ' requires withdrawal_note parameter to withdraw PLN')
        else:
            method = 'privatePostWithdraw'
            request['address'] = address
        response = getattr(self, method)(self.extend(request, params))
        return {
            'info': response,
            'id': response,
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        if api == 'public':
            url += '/' + self.implode_params(path + '.json', params)
        else:
            nonce = self.nonce()
            query = self.extend({
                'tonce': nonce,
                'method': path,
            }, params)
            body = self.urlencode(query)
            headers = {
                'API-Key': self.apiKey,
                'API-Hash': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class bitmex (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitmex',
            'name': 'BitMEX',
            'countries': 'SC',  # Seychelles
            'version': 'v1',
            'rateLimit': 1500,
            'hasCORS': False,
            'hasFetchOHLCV': True,
            'hasWithdraw': True,
            'timeframes': {
                '1m': '1m',
                '5m': '5m',
                '1h': '1h',
                '1d': '1d',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766319-f653c6e6-5ed4-11e7-933d-f0bc3699ae8f.jpg',
                'api': 'https://www.bitmex.com',
                'www': 'https://www.bitmex.com',
                'doc': [
                    'https://www.bitmex.com/app/apiOverview',
                    'https://github.com/BitMEX/api-connectors/tree/master/official-http',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'announcement',
                        'announcement/urgent',
                        'funding',
                        'instrument',
                        'instrument/active',
                        'instrument/activeAndIndices',
                        'instrument/activeIntervals',
                        'instrument/compositeIndex',
                        'instrument/indices',
                        'insurance',
                        'leaderboard',
                        'liquidation',
                        'orderBook',
                        'orderBook/L2',
                        'quote',
                        'quote/bucketed',
                        'schema',
                        'schema/websocketHelp',
                        'settlement',
                        'stats',
                        'stats/history',
                        'trade',
                        'trade/bucketed',
                    ],
                },
                'private': {
                    'get': [
                        'apiKey',
                        'chat',
                        'chat/channels',
                        'chat/connected',
                        'execution',
                        'execution/tradeHistory',
                        'notification',
                        'order',
                        'position',
                        'user',
                        'user/affiliateStatus',
                        'user/checkReferralCode',
                        'user/commission',
                        'user/depositAddress',
                        'user/margin',
                        'user/minWithdrawalFee',
                        'user/wallet',
                        'user/walletHistory',
                        'user/walletSummary',
                    ],
                    'post': [
                        'apiKey',
                        'apiKey/disable',
                        'apiKey/enable',
                        'chat',
                        'order',
                        'order/bulk',
                        'order/cancelAllAfter',
                        'order/closePosition',
                        'position/isolate',
                        'position/leverage',
                        'position/riskLimit',
                        'position/transferMargin',
                        'user/cancelWithdrawal',
                        'user/confirmEmail',
                        'user/confirmEnableTFA',
                        'user/confirmWithdrawal',
                        'user/disableTFA',
                        'user/logout',
                        'user/logoutAll',
                        'user/preferences',
                        'user/requestEnableTFA',
                        'user/requestWithdrawal',
                    ],
                    'put': [
                        'order',
                        'order/bulk',
                        'user',
                    ],
                    'delete': [
                        'apiKey',
                        'order',
                        'order/all',
                    ],
                }
            },
        }
        params.update(config)
        super(bitmex, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetInstrumentActiveAndIndices()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['symbol']
            base = market['underlying']
            quote = market['quoteCurrency']
            isFuturesContract = id != (base + quote)
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = id if isFuturesContract else(base + '/' + quote)
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetUserMargin({'currency': 'all'})
        result = {'info': response}
        for b in range(0, len(response)):
            balance = response[b]
            currency = balance['currency'].upper()
            currency = self.common_currency_code(currency)
            account = {
                'free': balance['availableMargin'],
                'used': 0.0,
                'total': balance['amount'],
            }
            if currency == 'BTC':
                account['free'] = account['free'] * 0.00000001
                account['total'] = account['total'] * 0.00000001
            account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetOrderBookL2(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        timestamp = self.milliseconds()
        result = {
            'bids': [],
            'asks': [],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
        }
        for o in range(0, len(orderbook)):
            order = orderbook[o]
            side = 'asks' if (order['side'] == 'Sell') else 'bids'
            amount = order['size']
            price = order['price']
            result[side].append([price, amount])
        result['bids'] = self.sort_by(result['bids'], 0, True)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        request = self.extend({
            'symbol': self.market_id(symbol),
            'binSize': '1d',
            'partial': True,
            'count': 1,
            'reverse': True,
        }, params)
        quotes = self.publicGetQuoteBucketed(request)
        quotesLength = len(quotes)
        quote = quotes[quotesLength - 1]
        tickers = self.publicGetTradeBucketed(request)
        ticker = tickers[0]
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(quote['bidPrice']),
            'ask': float(quote['askPrice']),
            'vwap': float(ticker['vwap']),
            'open': None,
            'close': float(ticker['close']),
            'first': None,
            'last': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['homeNotional']),
            'quoteVolume': float(ticker['foreignNotional']),
            'info': ticker,
        }

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        timestamp = self.parse8601(ohlcv['timestamp'])
        return [
            timestamp,
            ohlcv['open'],
            ohlcv['high'],
            ohlcv['low'],
            ohlcv['close'],
            ohlcv['volume'],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        # send JSON key/value pairs, such as {"key": "value"}
        # filter by individual fields and do advanced queries on timestamps
        # filter = {'key': 'value'}
        # send a bare series(e.g. XBU) to nearest expiring contract in that series
        # you can also send a timeframe, e.g. XBU:monthly
        # timeframes: daily, weekly, monthly, quarterly, and biquarterly
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'binSize': self.timeframes[timeframe],
            'partial': True,     # True == include yet-incomplete current bins
            # 'filter': filter,  # filter by individual fields and do advanced queries
            # 'columns': [],    # will return all columns if omitted
            # 'start': 0,       # starting point for results(wtf?)
            # 'reverse': False,  # True == newest first
            # 'endTime': '',    # ending date filter for results
        }
        if since:
            request['startTime'] = since  # starting date filter for results
        if limit:
            request['count'] = limit  # default 100
        response = self.publicGetTradeBucketed(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(trade['timestamp'])
        symbol = None
        if not market:
            if 'symbol' in trade:
                market = self.markets_by_id[trade['symbol']]
        if market:
            symbol = market['symbol']
        return {
            'id': trade['trdMatchID'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': None,
            'type': None,
            'side': trade['side'].lower(),
            'price': trade['price'],
            'amount': trade['size'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrade(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'symbol': self.market_id(symbol),
            'side': self.capitalize(side),
            'orderQty': amount,
            'ordType': self.capitalize(type),
        }
        if type == 'limit':
            order['price'] = price
        response = self.privatePostOrder(self.extend(order, params))
        return {
            'info': response,
            'id': response['orderID'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privateDeleteOrder({'orderID': id})

    def isFiat(self, currency):
        if currency == 'EUR':
            return True
        if currency == 'PLN':
            return True
        return False

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        if currency != 'BTC':
            raise ExchangeError(self.id + ' supoprts BTC withdrawals only, other currencies coming soon...')
        request = {
            'currency': 'XBt',  # temporarily
            'amount': amount,
            'address': address,
            # 'otpToken': '123456',  # requires if two-factor auth(OTP) is enabled
            # 'fee': 0.001,  # bitcoin network fee
        }
        response = self.privatePostUserRequestWithdrawal(self.extend(request, params))
        return {
            'info': response,
            'id': response['transactID'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        query = '/api' + '/' + self.version + '/' + path
        if params:
            query += '?' + self.urlencode(params)
        url = self.urls['api'] + query
        if api == 'private':
            nonce = str(self.nonce())
            if method == 'POST':
                if params:
                    body = self.json(params)
            request = ''.join([method, query, nonce, body or ''])
            headers = {
                'Content-Type': 'application/json',
                'api-nonce': nonce,
                'api-key': self.apiKey,
                'api-signature': self.hmac(self.encode(request), self.encode(self.secret)),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class bitso (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitso',
            'name': 'Bitso',
            'countries': 'MX',  # Mexico
            'rateLimit': 2000,  # 30 requests per minute
            'version': 'v3',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766335-715ce7aa-5ed5-11e7-88a8-173a27bb30fe.jpg',
                'api': 'https://api.bitso.com',
                'www': 'https://bitso.com',
                'doc': 'https://bitso.com/api_info',
            },
            'api': {
                'public': {
                    'get': [
                        'available_books',
                        'ticker',
                        'order_book',
                        'trades',
                    ],
                },
                'private': {
                    'get': [
                        'account_status',
                        'balance',
                        'fees',
                        'fundings',
                        'fundings/{fid}',
                        'funding_destination',
                        'kyc_documents',
                        'ledger',
                        'ledger/trades',
                        'ledger/fees',
                        'ledger/fundings',
                        'ledger/withdrawals',
                        'mx_bank_codes',
                        'open_orders',
                        'order_trades/{oid}',
                        'orders/{oid}',
                        'user_trades',
                        'user_trades/{tid}',
                        'withdrawals/',
                        'withdrawals/{wid}',
                    ],
                    'post': [
                        'bitcoin_withdrawal',
                        'debit_card_withdrawal',
                        'ether_withdrawal',
                        'orders',
                        'phone_number',
                        'phone_verification',
                        'phone_withdrawal',
                        'spei_withdrawal',
                    ],
                    'delete': [
                        'orders/{oid}',
                        'orders/all',
                    ],
                }
            },
        }
        params.update(config)
        super(bitso, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetAvailableBooks()
        result = []
        for p in range(0, len(markets['payload'])):
            market = markets['payload'][p]
            id = market['book']
            symbol = id.upper().replace('_', '/')
            base, quote = symbol.split('/')
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalance()
        balances = response['payload']['balances']
        result = {'info': response}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency'].upper()
            account = {
                'free': float(balance['available']),
                'used': float(balance['locked']),
                'total': float(balance['total']),
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetOrderBook(self.extend({
            'book': self.market_id(symbol),
        }, params))
        orderbook = response['payload']
        timestamp = self.parse8601(orderbook['updated_at'])
        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetTicker(self.extend({
            'book': self.market_id(symbol),
        }, params))
        ticker = response['payload']
        timestamp = self.parse8601(ticker['created_at'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': float(ticker['vwap']),
            'open': None,
            'close': None,
            'first': None,
            'last': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(trade['created_at'])
        symbol = None
        if not market:
            if 'book' in trade:
                market = self.markets_by_id[trade['book']]
        if market:
            symbol = market['symbol']
        return {
            'id': str(trade['tid']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': None,
            'type': None,
            'side': trade['maker_side'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'book': market['id'],
        }, params))
        return self.parse_trades(response['payload'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'book': self.market_id(symbol),
            'side': side,
            'type': type,
            'major': amount,
        }
        if type == 'limit':
            order['price'] = price
        response = self.privatePostOrders(self.extend(order, params))
        return {
            'info': response,
            'id': response['payload']['oid'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privateDeleteOrders({'oid': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        query = '/' + self.version + '/' + self.implode_params(path, params)
        url = self.urls['api'] + query
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            if params:
                body = self.json(params)
            nonce = str(self.nonce())
            request = ''.join([nonce, method, query, body or ''])
            signature = self.hmac(self.encode(request), self.encode(self.secret))
            auth = self.apiKey + ':' + nonce + ':' + signature
            headers = {'Authorization': "Bitso " + auth}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'success' in response:
            if response['success']:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class bitstamp1 (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitstamp1',
            'name': 'Bitstamp v1',
            'countries': 'GB',
            'rateLimit': 1000,
            'version': 'v1',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27786377-8c8ab57e-5fe9-11e7-8ea4-2b05b6bcceec.jpg',
                'api': 'https://www.bitstamp.net/api',
                'www': 'https://www.bitstamp.net',
                'doc': 'https://www.bitstamp.net/api',
            },
            'api': {
                'public': {
                    'get': [
                        'ticker',
                        'ticker_hour',
                        'order_book',
                        'transactions',
                        'eur_usd',
                    ],
                },
                'private': {
                    'post': [
                        'balance',
                        'user_transactions',
                        'open_orders',
                        'order_status',
                        'cancel_order',
                        'cancel_all_orders',
                        'buy',
                        'sell',
                        'bitcoin_deposit_address',
                        'unconfirmed_btc',
                        'ripple_withdrawal',
                        'ripple_address',
                        'withdrawal_requests',
                        'bitcoin_withdrawal',
                    ],
                },
            },
            'markets': {
                'BTC/USD': {'id': 'btcusd', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'BTC/EUR': {'id': 'btceur', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                'EUR/USD': {'id': 'eurusd', 'symbol': 'EUR/USD', 'base': 'EUR', 'quote': 'USD'},
                'XRP/USD': {'id': 'xrpusd', 'symbol': 'XRP/USD', 'base': 'XRP', 'quote': 'USD'},
                'XRP/EUR': {'id': 'xrpeur', 'symbol': 'XRP/EUR', 'base': 'XRP', 'quote': 'EUR'},
                'XRP/BTC': {'id': 'xrpbtc', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC'},
                'LTC/USD': {'id': 'ltcusd', 'symbol': 'LTC/USD', 'base': 'LTC', 'quote': 'USD'},
                'LTC/EUR': {'id': 'ltceur', 'symbol': 'LTC/EUR', 'base': 'LTC', 'quote': 'EUR'},
                'LTC/BTC': {'id': 'ltcbtc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'ETH/USD': {'id': 'ethusd', 'symbol': 'ETH/USD', 'base': 'ETH', 'quote': 'USD'},
                'ETH/EUR': {'id': 'etheur', 'symbol': 'ETH/EUR', 'base': 'ETH', 'quote': 'EUR'},
                'ETH/BTC': {'id': 'ethbtc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(bitstamp1, self).__init__(params)

    def fetch_order_book(self, symbol, params={}):
        if symbol != 'BTC/USD':
            raise ExchangeError(self.id + ' ' + self.version + " fetchOrderBook doesn't support " + symbol + ', use it for BTC/USD only')
        orderbook = self.publicGetOrderBook(params)
        timestamp = int(orderbook['timestamp']) * 1000
        return self.parse_order_book(orderbook, timestamp)

    def fetch_ticker(self, symbol, params={}):
        if symbol != 'BTC/USD':
            raise ExchangeError(self.id + ' ' + self.version + " fetchTicker doesn't support " + symbol + ', use it for BTC/USD only')
        ticker = self.publicGetTicker(params)
        timestamp = int(ticker['timestamp']) * 1000
        vwap = float(ticker['vwap'])
        baseVolume = float(ticker['volume'])
        quoteVolume = baseVolume * vwap
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': vwap,
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        timestamp = None
        if 'date' in trade:
            timestamp = int(trade['date']) * 1000
        elif 'datetime' in trade:
            # timestamp = self.parse8601(trade['datetime'])
            timestamp = int(trade['datetime']) * 1000
        side = 'buy' if (trade['type'] == 0) else 'sell'
        order = None
        if 'order_id' in trade:
            order = str(trade['order_id'])
        if 'currency_pair' in trade:
            if trade['currency_pair'] in self.markets_by_id:
                market = self.markets_by_id[trade['currency_pair']]
        return {
            'id': str(trade['tid']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': order,
            'type': None,
            'side': side,
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        if symbol != 'BTC/USD':
            raise ExchangeError(self.id + ' ' + self.version + " fetchTrades doesn't support " + symbol + ', use it for BTC/USD only')
        market = self.market(symbol)
        response = self.publicGetTransactions(self.extend({
            'time': 'minute',
        }, params))
        return self.parse_trades(response, market)

    def fetch_balance(self, params={}):
        balance = self.privatePostBalance()
        result = {'info': balance}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            total = lowercase + '_balance'
            free = lowercase + '_available'
            used = lowercase + '_reserved'
            account = self.account()
            account['free'] = self.safe_float(balance, free, 0.0)
            account['used'] = self.safe_float(balance, used, 0.0)
            account['total'] = self.safe_float(balance, total, 0.0)
            result[currency] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type != 'limit':
            raise ExchangeError(self.id + ' ' + self.version + ' accepts limit orders only')
        method = 'privatePost' + self.capitalize(side)
        order = {
            'id': self.market_id(symbol),
            'amount': amount,
            'price': price,
        }
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder({'id': id})

    def parse_order_status(self, order):
        if (order['status'] == 'Queue') or (order['status'] == 'Open'):
            return 'open'
        if order['status'] == 'Finished':
            return 'closed'
        return order['status']

    def fetch_order_status(self, id, symbol=None):
        self.load_markets()
        response = self.privatePostOrderStatus({'id': id})
        return self.parse_order_status(response)

    def fetch_my_trades(self, symbol=None, params={}):
        self.load_markets()
        market = None
        if symbol:
            market = self.market(symbol)
        pair = market['id'] if market else 'all'
        request = self.extend({'id': pair}, params)
        response = self.privatePostOpenOrdersId(request)
        return self.parse_trades(response, market)

    def fetch_order(self, id, symbol=None, params={}):
        raise NotSupported(self.id + ' fetchOrder is not implemented yet')
        self.load_markets()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            if not self.uid:
                raise AuthenticationError(self.id + ' requires `' + self.id + '.uid` property for authentication')
            nonce = str(self.nonce())
            auth = nonce + self.uid + self.apiKey
            signature = self.encode(self.hmac(self.encode(auth), self.encode(self.secret)))
            query = self.extend({
                'key': self.apiKey,
                'signature': signature.upper(),
                'nonce': nonce,
            }, query)
            body = self.urlencode(query)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] == 'error':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class bitstamp (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bitstamp',
            'name': 'Bitstamp',
            'countries': 'GB',
            'rateLimit': 1000,
            'version': 'v2',
            'hasCORS': False,
            'hasFetchOrder': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27786377-8c8ab57e-5fe9-11e7-8ea4-2b05b6bcceec.jpg',
                'api': 'https://www.bitstamp.net/api',
                'www': 'https://www.bitstamp.net',
                'doc': 'https://www.bitstamp.net/api',
            },
            'api': {
                'public': {
                    'get': [
                        'order_book/{pair}/',
                        'ticker_hour/{pair}/',
                        'ticker/{pair}/',
                        'transactions/{pair}/',
                    ],
                },
                'private': {
                    'post': [
                        'balance/',
                        'balance/{pair}/',
                        'user_transactions/',
                        'user_transactions/{pair}/',
                        'open_orders/all/',
                        'open_orders/{pair}',
                        'order_status/',
                        'cancel_order/',
                        'buy/{pair}/',
                        'buy/market/{pair}/',
                        'sell/{pair}/',
                        'sell/market/{pair}/',
                        'ltc_withdrawal/',
                        'ltc_address/',
                        'eth_withdrawal/',
                        'eth_address/',
                        'transfer-to-main/',
                        'transfer-from-main/',
                        'xrp_withdrawal/',
                        'xrp_address/',
                        'withdrawal/open/',
                        'withdrawal/status/',
                        'withdrawal/cancel/',
                        'liquidation_address/new/',
                        'liquidation_address/info/',
                    ],
                },
                'v1': {
                    'post': [
                        'bitcoin_deposit_address/',
                        'unconfirmed_btc/',
                        'bitcoin_withdrawal/',
                    ]
                }
            },
            'markets': {
                'BTC/USD': {'id': 'btcusd', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'BTC/EUR': {'id': 'btceur', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                'EUR/USD': {'id': 'eurusd', 'symbol': 'EUR/USD', 'base': 'EUR', 'quote': 'USD'},
                'XRP/USD': {'id': 'xrpusd', 'symbol': 'XRP/USD', 'base': 'XRP', 'quote': 'USD'},
                'XRP/EUR': {'id': 'xrpeur', 'symbol': 'XRP/EUR', 'base': 'XRP', 'quote': 'EUR'},
                'XRP/BTC': {'id': 'xrpbtc', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC'},
                'LTC/USD': {'id': 'ltcusd', 'symbol': 'LTC/USD', 'base': 'LTC', 'quote': 'USD'},
                'LTC/EUR': {'id': 'ltceur', 'symbol': 'LTC/EUR', 'base': 'LTC', 'quote': 'EUR'},
                'LTC/BTC': {'id': 'ltcbtc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'ETH/USD': {'id': 'ethusd', 'symbol': 'ETH/USD', 'base': 'ETH', 'quote': 'USD'},
                'ETH/EUR': {'id': 'etheur', 'symbol': 'ETH/EUR', 'base': 'ETH', 'quote': 'EUR'},
                'ETH/BTC': {'id': 'ethbtc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(bitstamp, self).__init__(params)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetOrderBookPair(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = int(orderbook['timestamp']) * 1000
        return self.parse_order_book(orderbook, timestamp)

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetTickerPair(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = int(ticker['timestamp']) * 1000
        vwap = float(ticker['vwap'])
        baseVolume = float(ticker['volume'])
        quoteVolume = baseVolume * vwap
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': vwap,
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        timestamp = None
        if 'date' in trade:
            timestamp = int(trade['date']) * 1000
        elif 'datetime' in trade:
            # timestamp = self.parse8601(trade['datetime'])
            timestamp = int(trade['datetime']) * 1000
        side = 'buy' if (trade['type'] == 0) else 'sell'
        order = None
        if 'order_id' in trade:
            order = str(trade['order_id'])
        if 'currency_pair' in trade:
            if trade['currency_pair'] in self.markets_by_id:
                market = self.markets_by_id[trade['currency_pair']]
        return {
            'id': str(trade['tid']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': order,
            'type': None,
            'side': side,
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTransactionsPair(self.extend({
            'pair': market['id'],
            'time': 'minute',
        }, params))
        return self.parse_trades(response, market)

    def fetch_balance(self, params={}):
        balance = self.privatePostBalance()
        result = {'info': balance}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            total = lowercase + '_balance'
            free = lowercase + '_available'
            used = lowercase + '_reserved'
            account = self.account()
            if free in balance:
                account['free'] = float(balance[free])
            if used in balance:
                account['used'] = float(balance[used])
            if total in balance:
                account['total'] = float(balance[total])
            result[currency] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        method = 'privatePost' + self.capitalize(side)
        order = {
            'pair': self.market_id(symbol),
            'amount': amount,
        }
        if type == 'market':
            method += 'Market'
        else:
            order['price'] = price
        method += 'Pair'
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder({'id': id})

    def parse_order_status(self, order):
        if (order['status'] == 'Queue') or (order['status'] == 'Open'):
            return 'open'
        if order['status'] == 'Finished':
            return 'closed'
        return order['status']

    def fetch_order_status(self, id, symbol=None):
        self.load_markets()
        response = self.privatePostOrderStatus({'id': id})
        return self.parse_order_status(response)

    def fetch_my_trades(self, symbol=None, params={}):
        self.load_markets()
        market = None
        if symbol:
            market = self.market(symbol)
        pair = market['id'] if market else 'all'
        request = self.extend({'pair': pair}, params)
        response = self.privatePostOpenOrdersPair(request)
        return self.parse_trades(response, market)

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostOrderStatus({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/'
        if api != 'v1':
            url += self.version + '/'
        url += self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            if not self.uid:
                raise AuthenticationError(self.id + ' requires `' + self.id + '.uid` property for authentication')
            nonce = str(self.nonce())
            auth = nonce + self.uid + self.apiKey
            signature = self.encode(self.hmac(self.encode(auth), self.encode(self.secret)))
            query = self.extend({
                'key': self.apiKey,
                'signature': signature.upper(),
                'nonce': nonce,
            }, query)
            body = self.urlencode(query)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] == 'error':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class bittrex (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bittrex',
            'name': 'Bittrex',
            'countries': 'US',
            'version': 'v1.1',
            'rateLimit': 1500,
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasFetchOHLCV': True,
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'hasFetchMyTrades': False,
            'hasWithdraw': True,
            'timeframes': {
                '1m': 'oneMin',
                '5m': 'fiveMin',
                '30m': 'thirtyMin',
                '1h': 'hour',
                '1d': 'day',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766352-cf0b3c26-5ed5-11e7-82b7-f3826b7a97d8.jpg',
                'api': {
                    'public': 'https://bittrex.com/api',
                    'account': 'https://bittrex.com/api',
                    'market': 'https://bittrex.com/api',
                    'v2': 'https://bittrex.com/api/v2.0/pub',
                },
                'www': 'https://bittrex.com',
                'doc': [
                    'https://bittrex.com/Home/Api',
                    'https://www.npmjs.org/package/node.bittrex.api',
                ],
                'fees': [
                    'https://bittrex.com/Fees',
                    'https://support.bittrex.com/hc/en-us/articles/115000199651-What-fees-does-Bittrex-charge-',
                ],
            },
            'api': {
                'v2': {
                    'get': [
                        'currencies/GetBTCPrice',
                        'market/GetTicks',
                        'market/GetLatestTick',
                        'Markets/GetMarketSummaries',
                        'market/GetLatestTick',
                    ],
                },
                'public': {
                    'get': [
                        'currencies',
                        'markethistory',
                        'markets',
                        'marketsummaries',
                        'marketsummary',
                        'orderbook',
                        'ticker',
                    ],
                },
                'account': {
                    'get': [
                        'balance',
                        'balances',
                        'depositaddress',
                        'deposithistory',
                        'order',
                        'orderhistory',
                        'withdrawalhistory',
                        'withdraw',
                    ],
                },
                'market': {
                    'get': [
                        'buylimit',
                        'buymarket',
                        'cancel',
                        'openorders',
                        'selllimit',
                        'sellmarket',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.0025,
                    'taker': 0.0025,
                },
            },
        }
        params.update(config)
        super(bittrex, self).__init__(params)

    def cost_to_precision(self, symbol, cost):
        return self.truncate(float(cost), self.markets[symbol].precision.price)

    def fee_to_precision(self, symbol, fee):
        return self.truncate(float(fee), self.markets[symbol]['precision']['price'])

    def fetch_markets(self):
        markets = self.publicGetMarkets()
        result = []
        for p in range(0, len(markets['result'])):
            market = markets['result'][p]
            id = market['MarketName']
            base = market['MarketCurrency']
            quote = market['BaseCurrency']
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            precision = {
                'amount': 8,
                'price': 8,
            }
            amountLimits = {
                'min': market['MinTradeSize'],
                'max': None,
            }
            priceLimits = {'min': None, 'max': None}
            limits = {
                'amount': amountLimits,
                'price': priceLimits,
            }
            result.append(self.extend(self.fees['trading'], {
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
                'lot': amountLimits['min'],
                'precision': precision,
                'limits': limits,
            }))
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.accountGetBalances()
        balances = response['result']
        result = {'info': balances}
        indexed = self.index_by(balances, 'Currency')
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in indexed:
                balance = indexed[currency]
                free = float(balance['Available'])
                total = float(balance['Balance'])
                used = total - free
                account['free'] = free
                account['used'] = used
                account['total'] = total
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetOrderbook(self.extend({
            'market': self.market_id(symbol),
            'type': 'both',
            'depth': 50,
        }, params))
        orderbook = response['result']
        return self.parse_order_book(orderbook, None, 'buy', 'sell', 'Rate', 'Quantity')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.parse8601(ticker['TimeStamp'])
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['High']),
            'low': float(ticker['Low']),
            'bid': float(ticker['Bid']),
            'ask': float(ticker['Ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['Last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['Volume']),
            'quoteVolume': float(ticker['BaseVolume']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetMarketsummaries(params)
        tickers = response['result']
        result = {}
        for t in range(0, len(tickers)):
            ticker = tickers[t]
            id = ticker['MarketName']
            market = None
            symbol = id
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            else:
                quote, base = id.split('-')
                base = self.common_currency_code(base)
                quote = self.common_currency_code(quote)
                symbol = base + '/' + quote
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketsummary(self.extend({
            'market': market['id'],
        }, params))
        ticker = response['result'][0]
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(trade['TimeStamp'])
        side = None
        if trade['OrderType'] == 'BUY':
            side = 'buy'
        elif trade['OrderType'] == 'SELL':
            side = 'sell'
        id = None
        if 'Id' in trade:
            id = str(trade['Id'])
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': 'limit',
            'side': side,
            'price': trade['Price'],
            'amount': trade['Quantity'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarkethistory(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_trades(response['result'], market)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1d', since=None, limit=None):
        timestamp = self.parse8601(ohlcv['T'])
        return [
            timestamp,
            ohlcv['O'],
            ohlcv['H'],
            ohlcv['L'],
            ohlcv['C'],
            ohlcv['V'],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'tickInterval': self.timeframes[timeframe],
            'marketName': market['id'],
        }
        response = self.v2GetMarketGetTicks(self.extend(request, params))
        return self.parse_ohlcvs(response['result'], market, timeframe, since, limit)

    def fetch_open_orders(self, symbol=None, params={}):
        self.load_markets()
        request = {}
        market = None
        if symbol:
            market = self.market(symbol)
            request['market'] = market['id']
        response = self.marketGetOpenorders(self.extend(request, params))
        orders = self.parse_orders(response['result'], market)
        return self.filter_orders_by_symbol(orders, symbol)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = 'marketGet' + self.capitalize(side) + type
        order = {
            'market': market['id'],
            'quantity': self.amount_to_precision(symbol, amount),
        }
        if type == 'limit':
            order['rate'] = self.price_to_precision(symbol, price)
        response = getattr(self, method)(self.extend(order, params))
        result = {
            'info': response,
            'id': response['result']['uuid'],
        }
        return result

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = None
        try:
            response = self.marketGetCancel(self.extend({
                'uuid': id,
            }, params))
        except Exception as e:
            if self.last_json_response:
                message = self.safe_string(self.last_json_response, 'message')
                if message == 'ORDER_NOT_OPEN':
                    raise InvalidOrder(self.id + ' cancelOrder() error: ' + self.last_http_response)
                if message == 'UUID_INVALID':
                    raise OrderNotFound(self.id + ' cancelOrder() error: ' + self.last_http_response)
            raise e
        return response

    def parse_order(self, order, market=None):
        side = None
        if 'OrderType' in order:
            side = 'buy' if (order['OrderType'] == 'LIMIT_BUY') else 'sell'
        if 'Type' in order:
            side = 'buy' if (order['Type'] == 'LIMIT_BUY') else 'sell'
        status = 'open'
        if order['Closed']:
            status = 'closed'
        elif order['CancelInitiated']:
            status = 'canceled'
        symbol = None
        if not market:
            if 'Exchange' in order:
                if order['Exchange'] in self.markets_by_id:
                    market = self.markets_by_id[order['Exchange']]
        if market:
            symbol = market['symbol']
        timestamp = None
        if 'Opened' in order:
            timestamp = self.parse8601(order['Opened'])
        if 'TimeStamp' in order:
            timestamp = self.parse8601(order['TimeStamp'])
        fee = None
        commission = None
        if 'Commission' in order:
            commission = 'Commission'
        elif 'CommissionPaid' in order:
            commission = 'CommissionPaid'
        if commission:
            fee = {
                'cost': float(order[commission]),
                'currency': market['quote'],
            }
        price = self.safe_float(order, 'Limit')
        cost = self.safe_float(order, 'Price')
        amount = self.safe_float(order, 'Quantity')
        remaining = self.safe_float(order, 'QuantityRemaining', 0.0)
        filled = amount - remaining
        if not cost:
            if price and amount:
                cost = price * amount
        if not price:
            if cost and filled:
                price = cost / filled
        average = self.safe_float(order, 'PricePerUnit')
        result = {
            'info': order,
            'id': order['OrderUuid'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': 'limit',
            'side': side,
            'price': price,
            'cost': cost,
            'average': average,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'status': status,
            'fee': fee,
        }
        return result

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = None
        try:
            response = self.accountGetOrder({'uuid': id})
        except Exception as e:
            if self.last_json_response:
                message = self.safe_string(self.last_json_response, 'message')
                if message == 'UUID_INVALID':
                    raise OrderNotFound(self.id + ' fetchOrder() error: ' + self.last_http_response)
            raise e
        return self.parse_order(response['result'])

    def fetch_orders(self, symbol=None, params={}):
        self.load_markets()
        request = {}
        market = None
        if symbol:
            market = self.market(symbol)
            request['market'] = market['id']
        response = self.accountGetOrderhistory(self.extend(request, params))
        orders = self.parse_orders(response['result'], market)
        return self.filter_orders_by_symbol(orders, symbol)

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        response = self.accountGetWithdraw(self.extend({
            'currency': currency,
            'quantity': amount,
            'address': address,
        }, params))
        id = None
        if 'result' in response:
            if 'uuid' in response['result']:
                id = response['result']['uuid']
        return {
            'info': response,
            'id': id,
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/'
        if api != 'v2':
            url += self.version + '/'
        if api == 'public':
            url += api + '/' + method.lower() + path
            if params:
                url += '?' + self.urlencode(params)
        elif api == 'v2':
            url += path
            if params:
                url += '?' + self.urlencode(params)
        else:
            nonce = self.nonce()
            url += api + '/'
            if ((api == 'account') and(path != 'withdraw')) or (path == 'openorders'):
                url += method.lower()
            url += path + '?' + self.urlencode(self.extend({
                'nonce': nonce,
                'apikey': self.apiKey,
            }, params))
            signature = self.hmac(self.encode(url), self.encode(self.secret), hashlib.sha512)
            headers = {'apisign': signature}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'success' in response:
            if response['success']:
                return response
        if 'message' in response:
            if response['message'] == "INSUFFICIENT_FUNDS":
                raise InsufficientFunds(self.id + ' ' + self.json(response))
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class blinktrade (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'blinktrade',
            'name': 'BlinkTrade',
            'countries': ['US', 'VE', 'VN', 'BR', 'PK', 'CL'],
            'rateLimit': 1000,
            'version': 'v1',
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27990968-75d9c884-6470-11e7-9073-46756c8e7e8c.jpg',
                'api': {
                    'public': 'https://api.blinktrade.com/api',
                    'private': 'https://api.blinktrade.com/tapi',
                },
                'www': 'https://blinktrade.com',
                'doc': 'https://blinktrade.com/docs',
            },
            'api': {
                'public': {
                    'get': [
                        '{currency}/ticker',    # ?crypto_currency=BTC
                        '{currency}/orderbook',  # ?crypto_currency=BTC
                        '{currency}/trades',    # ?crypto_currency=BTC&since=<TIMESTAMP>&limit=<NUMBER>
                    ],
                },
                'private': {
                    'post': [
                        'D',   # order
                        'F',   # cancel order
                        'U2',  # balance
                        'U4',  # my orders
                        'U6',  # withdraw
                        'U18',  # deposit
                        'U24',  # confirm withdrawal
                        'U26',  # list withdrawals
                        'U30',  # list deposits
                        'U34',  # ledger
                        'U70',  # cancel withdrawal
                    ],
                },
            },
            'markets': {
                'BTC/VEF': {'id': 'BTCVEF', 'symbol': 'BTC/VEF', 'base': 'BTC', 'quote': 'VEF', 'brokerId': 1, 'broker': 'SurBitcoin'},
                'BTC/VND': {'id': 'BTCVND', 'symbol': 'BTC/VND', 'base': 'BTC', 'quote': 'VND', 'brokerId': 3, 'broker': 'VBTC'},
                'BTC/BRL': {'id': 'BTCBRL', 'symbol': 'BTC/BRL', 'base': 'BTC', 'quote': 'BRL', 'brokerId': 4, 'broker': 'FoxBit'},
                'BTC/PKR': {'id': 'BTCPKR', 'symbol': 'BTC/PKR', 'base': 'BTC', 'quote': 'PKR', 'brokerId': 8, 'broker': 'UrduBit'},
                'BTC/CLP': {'id': 'BTCCLP', 'symbol': 'BTC/CLP', 'base': 'BTC', 'quote': 'CLP', 'brokerId': 9, 'broker': 'ChileBit'},
            },
        }
        params.update(config)
        super(blinktrade, self).__init__(params)

    def fetch_balance(self, params={}):
        # todo parse balance
        return self.privatePostU2({
            'BalanceReqID': self.nonce(),
        })

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderbook = self.publicGetCurrencyOrderbook(self.extend({
            'currency': market['quote'],
            'crypto_currency': market['base'],
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        market = self.market(symbol)
        ticker = self.publicGetCurrencyTicker(self.extend({
            'currency': market['quote'],
            'crypto_currency': market['base'],
        }, params))
        timestamp = self.milliseconds()
        lowercaseQuote = market['quote'].lower()
        quoteVolume = 'vol_' + lowercaseQuote
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['vol']),
            'quoteVolume': float(ticker[quoteVolume]),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'id': trade['tid'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['side'],
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetCurrencyTrades(self.extend({
            'currency': market['quote'],
            'crypto_currency': market['base'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        market = self.market(symbol)
        order = {
            'ClOrdID': self.nonce(),
            'Symbol': market['id'],
            'Side': self.capitalize(side),
            'OrdType': '2',
            'Price': price,
            'OrderQty': amount,
            'BrokerID': market['brokerId'],
        }
        response = self.privatePostD(self.extend(order, params))
        indexed = self.index_by(response['Responses'], 'MsgType')
        execution = indexed['8']
        return {
            'info': response,
            'id': execution['OrderID'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostF(self.extend({
            'ClOrdID': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = str(self.nonce())
            request = self.extend({'MsgType': path}, query)
            body = self.json(request)
            headers = {
                'APIKey': self.apiKey,
                'Nonce': nonce,
                'Signature': self.hmac(self.encode(nonce), self.encode(self.secret)),
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'Status' in response:
            if response['Status'] != 200:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class bl3p (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bl3p',
            'name': 'BL3P',
            'countries': ['NL', 'EU'],  # Netherlands, EU
            'rateLimit': 1000,
            'version': '1',
            'comment': 'An exchange market by BitonicNL',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28501752-60c21b82-6feb-11e7-818b-055ee6d0e754.jpg',
                'api': 'https://api.bl3p.eu',
                'www': [
                    'https://bl3p.eu',
                    'https://bitonic.nl',
                ],
                'doc': [
                    'https://github.com/BitonicNL/bl3p-api/tree/master/docs',
                    'https://bl3p.eu/api',
                    'https://bitonic.nl/en/api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        '{market}/ticker',
                        '{market}/orderbook',
                        '{market}/trades',
                    ],
                },
                'private': {
                    'post': [
                        '{market}/money/depth/full',
                        '{market}/money/order/add',
                        '{market}/money/order/cancel',
                        '{market}/money/order/result',
                        '{market}/money/orders',
                        '{market}/money/orders/history',
                        '{market}/money/trades/fetch',
                        'GENMKT/money/info',
                        'GENMKT/money/deposit_address',
                        'GENMKT/money/new_deposit_address',
                        'GENMKT/money/wallet/history',
                        'GENMKT/money/withdraw',
                    ],
                },
            },
            'markets': {
                'BTC/EUR': {'id': 'BTCEUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                # 'LTC/EUR': {'id': 'LTCEUR', 'symbol': 'LTC/EUR', 'base': 'LTC', 'quote': 'EUR'},
            },
        }
        params.update(config)
        super(bl3p, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privatePostGENMKTMoneyInfo()
        data = response['data']
        balance = data['wallets']
        result = {'info': data}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in balance:
                if 'available' in balance[currency]:
                    account['free'] = float(balance[currency]['available']['value'])
            if currency in balance:
                if 'balance' in balance[currency]:
                    account['total'] = float(balance[currency]['balance']['value'])
            if account['total']:
                if account['free']:
                    account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def parse_bidask(self, bidask, priceKey=0, amountKey=0):
        return [
            bidask['price_int'] / 100000.0,
            bidask['amount_int'] / 100000000.0,
        ]

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetMarketOrderbook(self.extend({
            'market': market['id'],
        }, params))
        orderbook = response['data']
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetMarketTicker(self.extend({
            'market': self.market_id(symbol),
        }, params))
        timestamp = ticker['timestamp'] * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']['24h']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        return {
            'id': trade['trade_id'],
            'info': trade,
            'timestamp': trade['date'],
            'datetime': self.iso8601(trade['date']),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': trade['price_int'] / 100000.0,
            'amount': trade['amount_int'] / 100000000.0,
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetMarketTrades(self.extend({
            'market': market['id'],
        }, params))
        result = self.parse_trades(response['data']['trades'], market)
        return result

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        market = self.market(symbol)
        order = {
            'market': market['id'],
            'amount_int': amount,
            'fee_currency': market['quote'],
            'type': 'bid' if (side == 'buy') else 'ask',
        }
        if type == 'limit':
            order['price_int'] = price
        response = self.privatePostMarketMoneyOrderAdd(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['order_id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostMarketMoneyOrderCancel({'order_id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = self.implode_params(path, params)
        url = self.urls['api'] + '/' + self.version + '/' + request
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            body = self.urlencode(self.extend({'nonce': nonce}, query))
            secret = base64.b64decode(self.secret)
            auth = request + "\0" + body
            signature = self.hmac(self.encode(auth), secret, hashlib.sha512, 'base64')
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Rest-Key': self.apiKey,
                'Rest-Sign': signature,
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class bleutrade (bittrex):

    def __init__(self, config={}):
        params = {
            'id': 'bleutrade',
            'name': 'Bleutrade',
            'countries': 'BR',  # Brazil
            'rateLimit': 1000,
            'version': 'v2',
            'hasCORS': True,
            'hasFetchTickers': True,
            'hasFetchOHLCV': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30303000-b602dbe6-976d-11e7-956d-36c5049c01e7.jpg',
                'api': {
                    'public': 'https://bleutrade.com/api',
                    'account': 'https://bleutrade.com/api',
                    'market': 'https://bleutrade.com/api',
                },
                'www': 'https://bleutrade.com',
                'doc': 'https://bleutrade.com/help/API',
            },
        }
        params.update(config)
        super(bleutrade, self).__init__(params)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetOrderbook(self.extend({
            'market': self.market_id(symbol),
            'type': 'ALL',
            'depth': 50,
        }, params))
        orderbook = response['result']
        return self.parse_order_book(orderbook, None, 'buy', 'sell', 'Rate', 'Quantity')

# -----------------------------------------------------------------------------


class asia (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'asia',
            'name': 'Asia',
            'comment': 'a common base API for several exchanges from China and Japan',
            'countries': ['JP', 'CN'],
            'rateLimit': 1000,
            'version': 'v1',
            'hasCORS': False,
            'hasFetchOHLCV': False,
            'api': {
                'public': {
                    'get': [
                        'depth',
                        'orders',
                        'ticker',
                        'allticker',
                    ],
                },
                'private': {
                    'post': [
                        'balance',
                        'trade_add',
                        'trade_cancel',
                        'trade_list',
                        'trade_view',
                        'wallet',
                    ],
                },
            },
        }
        params.update(config)
        super(asia, self).__init__(params)

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privatePostBalance()
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            if lowercase == 'dash':
                lowercase = 'drk'
            account = self.account()
            free = lowercase + '_balance'
            used = lowercase + '_lock'
            if free in balances:
                account['free'] = float(balances[free])
            if used in balances:
                account['used'] = float(balances[used])
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {}
        numSymbols = len(self.symbols)
        if numSymbols > 1:
            request['coin'] = market['id']
        orderbook = self.publicGetDepth(self.extend(request, params))
        result = self.parse_order_book(orderbook)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'buy'),
            'ask': self.safe_float(ticker, 'sell'),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': self.safe_float(ticker, 'last'),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'vol'),
            'quoteVolume': self.safe_float(ticker, 'volume'),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetAllticker(params)
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {}
        numSymbols = len(self.symbols)
        if numSymbols > 1:
            request['coin'] = market['id']
        ticker = self.publicGetTicker(self.extend(request, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = int(trade['date']) * 1000
        return {
            'info': trade,
            'id': trade['tid'],
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {}
        numSymbols = len(self.symbols)
        if numSymbols > 1:
            request['coin'] = market['id']
        response = self.publicGetOrders(self.extend(request, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'amount': amount,
            'price': price,
            'type': side,
        }
        numSymbols = len(self.symbols)
        if numSymbols > 1:
            request['coin'] = market['id']
        response = self.privatePostTradeAdd(self.extend(request, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostTradeCancel(self.extend({
            'id': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            nonce = str(self.nonce())
            query = self.extend({
                'key': self.apiKey,
                'nonce': nonce,
            }, params)
            request = self.urlencode(query)
            secret = self.hash(self.encode(self.secret))
            query['signature'] = self.hmac(self.encode(request), self.encode(secret))
            body = self.urlencode(query)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'result' in response:
            if not response['result']:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class btcbox (asia):

    def __init__(self, config={}):
        params = {
            'id': 'btcbox',
            'name': 'BtcBox',
            'countries': 'JP',
            'rateLimit': 1000,
            'version': 'v1',
            'hasCORS': False,
            'hasFetchOHLCV': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/31275803-4df755a8-aaa1-11e7-9abb-11ec2fad9f2d.jpg',
                'api': 'https://www.btcbox.co.jp/api',
                'www': 'https://www.btcbox.co.jp/',
                'doc': 'https://www.btcbox.co.jp/help/asm',
            },
            'markets': {
                'BTC/JPY': {'id': 'BTC/JPY', 'symbol': 'BTC/JPY', 'base': 'BTC', 'quote': 'JPY'},
            },
        }
        params.update(config)
        super(btcbox, self).__init__(params)

# -----------------------------------------------------------------------------


class btcchina (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'btcchina',
            'name': 'BTCChina',
            'countries': 'CN',
            'rateLimit': 1500,
            'version': 'v1',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766368-465b3286-5ed6-11e7-9a11-0f6467e1d82b.jpg',
                'api': {
                    'plus': 'https://plus-api.btcchina.com/market',
                    'public': 'https://data.btcchina.com/data',
                    'private': 'https://api.btcchina.com/api_trade_v1.php',
                },
                'www': 'https://www.btcchina.com',
                'doc': 'https://www.btcchina.com/apidocs'
            },
            'api': {
                'plus': {
                    'get': [
                        'orderbook',
                        'ticker',
                        'trade',
                    ],
                },
                'public': {
                    'get': [
                        'historydata',
                        'orderbook',
                        'ticker',
                        'trades',
                    ],
                },
                'private': {
                    'post': [
                        'BuyIcebergOrder',
                        'BuyOrder',
                        'BuyOrder2',
                        'BuyStopOrder',
                        'CancelIcebergOrder',
                        'CancelOrder',
                        'CancelStopOrder',
                        'GetAccountInfo',
                        'getArchivedOrder',
                        'getArchivedOrders',
                        'GetDeposits',
                        'GetIcebergOrder',
                        'GetIcebergOrders',
                        'GetMarketDepth',
                        'GetMarketDepth2',
                        'GetOrder',
                        'GetOrders',
                        'GetStopOrder',
                        'GetStopOrders',
                        'GetTransactions',
                        'GetWithdrawal',
                        'GetWithdrawals',
                        'RequestWithdrawal',
                        'SellIcebergOrder',
                        'SellOrder',
                        'SellOrder2',
                        'SellStopOrder',
                    ],
                },
            },
            'markets': {
                'BTC/CNY': {'id': 'btccny', 'symbol': 'BTC/CNY', 'base': 'BTC', 'quote': 'CNY', 'api': 'public', 'plus': False},
                'LTC/CNY': {'id': 'ltccny', 'symbol': 'LTC/CNY', 'base': 'LTC', 'quote': 'CNY', 'api': 'public', 'plus': False},
                'LTC/BTC': {'id': 'ltcbtc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC', 'api': 'public', 'plus': False},
                'BCH/CNY': {'id': 'bcccny', 'symbol': 'BCH/CNY', 'base': 'BCH', 'quote': 'CNY', 'api': 'plus', 'plus': True},
                'ETH/CNY': {'id': 'ethcny', 'symbol': 'ETH/CNY', 'base': 'ETH', 'quote': 'CNY', 'api': 'plus', 'plus': True},
            },
        }
        params.update(config)
        super(btcchina, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetTicker({
            'market': 'all',
        })
        result = []
        keys = list(markets.keys())
        for p in range(0, len(keys)):
            key = keys[p]
            market = markets[key]
            parts = key.split('_')
            id = parts[1]
            base = id[0:3]
            quote = id[3:6]
            base = base.upper()
            quote = quote.upper()
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetAccountInfo()
        balances = response['result']
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = self.account()
            if lowercase in balances['balance']:
                account['total'] = float(balances['balance'][lowercase]['amount'])
            if lowercase in balances['frozen']:
                account['used'] = float(balances['frozen'][lowercase]['amount'])
            account['free'] = account['total'] - account['used']
            result[currency] = account
        return self.parse_balance(result)

    def createMarketRequest(self, market):
        request = {}
        field = 'symbol' if (market['plus']) else 'market'
        request[field] = market['id']
        return request

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = market['api'] + 'GetOrderbook'
        request = self.createMarketRequest(market)
        orderbook = getattr(self, method)(self.extend(request, params))
        timestamp = orderbook['date'] * 1000
        result = self.parse_order_book(orderbook, timestamp)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def parse_ticker(self, ticker, market):
        timestamp = ticker['date'] * 1000
        return {
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': float(ticker['vwap']),
            'open': float(ticker['open']),
            'close': float(ticker['prev_close']),
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['vol']),
            'quoteVolume': None,
            'info': ticker,
        }

    def parse_tickerPlus(self, ticker, market):
        timestamp = ticker['Timestamp']
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['High']),
            'low': float(ticker['Low']),
            'bid': float(ticker['BidPrice']),
            'ask': float(ticker['AskPrice']),
            'vwap': None,
            'open': float(ticker['Open']),
            'close': float(ticker['PrevCls']),
            'first': None,
            'last': float(ticker['Last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['Volume24H']),
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = market['api'] + 'GetTicker'
        request = self.createMarketRequest(market)
        tickers = getattr(self, method)(self.extend(request, params))
        ticker = tickers['ticker']
        if market['plus']:
            return self.parseTickerPlus(ticker, market)
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = int(trade['date']) * 1000
        return {
            'id': trade['tid'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def parse_tradePlus(self, trade, market):
        timestamp = self.parse8601(trade['timestamp'])
        return {
            'id': None,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['side'].lower(),
            'price': trade['price'],
            'amount': trade['size'],
        }

    def parse_tradesPlus(self, trades, market=None):
        result = []
        for i in range(0, len(trades)):
            result.append(self.parseTradePlus(trades[i], market))
        return result

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = market['api'] + 'GetTrade'
        request = self.createMarketRequest(market)
        if market['plus']:
            now = self.milliseconds()
            request['start_time'] = now - 86400 * 1000
            request['end_time'] = now
        else:
            method += 's'  # trades vs trade
        response = getattr(self, method)(self.extend(request, params))
        if market['plus']:
            return self.parseTradesPlus(response['trades'], market)
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = 'privatePost' + self.capitalize(side) + 'Order2'
        order = {}
        id = market['id'].upper()
        if type == 'market':
            order['params'] = [None, amount, id]
        else:
            order['params'] = [price, amount, id]
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = params['market']  # TODO fixme
        return self.privatePostCancelOrder(self.extend({
            'params': [id, market],
        }, params))

    def nonce(self):
        return self.microseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + path
        if api == 'private':
            if not self.apiKey:
                raise AuthenticationError(self.id + ' requires `' + self.id + '.apiKey` property for authentication')
            if not self.secret:
                raise AuthenticationError(self.id + ' requires `' + self.id + '.secret` property for authentication')
            p = []
            if 'params' in params:
                p = params['params']
            nonce = self.nonce()
            request = {
                'method': path,
                'id': nonce,
                'params': p,
            }
            p = ','.join(p)
            body = self.json(request)
            query = (
                'tonce=' + nonce +
                '&accesskey=' + self.apiKey +
                '&requestmethod=' + method.lower() +
                '&id=' + nonce +
                '&method=' + path +
                '&params=' + p
            )
            signature = self.hmac(self.encode(query), self.encode(self.secret), hashlib.sha1)
            auth = self.apiKey + ':' + signature
            headers = {
                'Authorization': 'Basic ' + base64.b64encode(auth),
                'Json-Rpc-Tonce': nonce,
            }
        else:
            if params:
                url += '?' + self.urlencode(params)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class btce (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'btce',
            'name': 'BTC-e',
            'comment': 'Base API for many markets, including Liqui, WEX, Tidex, DSX, YoBit...',
            'version': '3',
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'hasFetchTickers': True,
            'hasFetchMyTrades': True,
            'api': {
                'public': {
                    'get': [
                        'info',
                        'ticker/{pair}',
                        'depth/{pair}',
                        'trades/{pair}',
                    ],
                },
                'private': {
                    'post': [
                        'getInfo',
                        'Trade',
                        'ActiveOrders',
                        'OrderInfo',
                        'CancelOrder',
                        'TradeHistory',
                        'TransHistory',
                        'CoinDepositAddress',
                        'WithdrawCoin',
                        'CreateCoupon',
                        'RedeemCoupon',
                    ],
                },
            },
        }
        params.update(config)
        super(btce, self).__init__(params)

    def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='taker', params={}):
        market = self.markets[symbol]
        key = 'quote'
        rate = market[takerOrMaker]
        cost = float(self.cost_to_precision(symbol, amount * rate))
        if side == 'sell':
            cost *= price
        else:
            key = 'base'
        return {
            'currency': market[key],
            'rate': rate,
            'cost': cost,
        }

    def common_currency_code(self, currency):
        if not self.substituteCommonCurrencyCodes:
            return currency
        if currency == 'XBT':
            return 'BTC'
        if currency == 'BCC':
            return 'BCH'
        if currency == 'DRK':
            return 'DASH'
        # they misspell DASH as dsh :/
        if currency == 'DSH':
            return 'DASH'
        return currency

    def getBaseQuoteFromMarketId(self, id):
        uppercase = id.upper()
        base, quote = uppercase.split('_')
        base = self.common_currency_code(base)
        quote = self.common_currency_code(quote)
        return [base, quote]

    def fetch_markets(self):
        response = self.publicGetInfo()
        markets = response['pairs']
        keys = list(markets.keys())
        result = []
        for p in range(0, len(keys)):
            id = keys[p]
            market = markets[id]
            base, quote = self.getBaseQuoteFromMarketId(id)
            symbol = base + '/' + quote
            precision = {
                'amount': self.safe_integer(market, 'decimal_places'),
                'price': self.safe_integer(market, 'decimal_places'),
            }
            amountLimits = {
                'min': self.safe_float(market, 'min_amount'),
                'max': self.safe_float(market, 'max_amount'),
            }
            priceLimits = {
                'min': self.safe_float(market, 'min_price'),
                'max': self.safe_float(market, 'max_price'),
            }
            costLimits = {
                'min': self.safe_float(market, 'min_total'),
            }
            limits = {
                'amount': amountLimits,
                'price': priceLimits,
                'cost': costLimits,
            }
            result.append(self.extend(self.fees['trading'], {
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'taker': market['fee'] / 100,
                'lot': amountLimits['min'],
                'precision': precision,
                'limits': limits,
                'info': market,
            }))
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetInfo()
        balances = response['return']
        result = {'info': balances}
        funds = balances['funds']
        currencies = list(funds.keys())
        for c in range(0, len(currencies)):
            currency = currencies[c]
            uppercase = currency.upper()
            uppercase = self.common_currency_code(uppercase)
            total = None
            used = None
            if balances['open_orders'] == 0:
                total = funds[currency]
                used = 0.0
            account = {
                'free': funds[currency],
                'used': used,
                'total': total,
            }
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetDepthPair(self.extend({
            'pair': market['id'],
        }, params))
        market_id_in_reponse = (market['id'] in list(response.keys()))
        if not market_id_in_reponse:
            raise ExchangeError(self.id + ' ' + market['symbol'] + ' order book is empty or not available')
        orderbook = response[market['id']]
        result = self.parse_order_book(orderbook)
        result['bids'] = self.sort_by(result['bids'], 0, True)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['updated'] * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'buy'),
            'ask': self.safe_float(ticker, 'sell'),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': self.safe_float(ticker, 'last'),
            'change': None,
            'percentage': None,
            'average': self.safe_float(ticker, 'avg'),
            'baseVolume': self.safe_float(ticker, 'vol_cur'),
            'quoteVolume': self.safe_float(ticker, 'vol'),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        ids = None
        if not symbols:
            numIds = len(self.ids)
            if numIds > 256:
                raise ExchangeError(self.id + ' fetchTickers() requires symbols argument')
            ids = self.ids
        else:
            ids = self.market_ids(symbols)
        tickers = self.publicGetTickerPair(self.extend({
            'pair': '-'.join(ids),
        }, params))
        result = {}
        keys = list(tickers.keys())
        for k in range(0, len(keys)):
            id = keys[k]
            ticker = tickers[id]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        tickers = self.fetch_tickers([symbol], params)
        return tickers[symbol]

    def parse_trade(self, trade, market):
        timestamp = trade['timestamp'] * 1000
        side = trade['type']
        if side == 'ask':
            side = 'sell'
        if side == 'bid':
            side = 'buy'
        price = self.safe_float(trade, 'price')
        if 'rate' in trade:
            price = self.safe_float(trade, 'rate')
        id = self.safe_string(trade, 'tid')
        if 'trade_id' in trade:
            id = self.safe_string(trade, 'trade_id')
        order = self.safe_string(trade, self.getOrderIdKey())
        fee = None
        return {
            'id': id,
            'order': order,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': 'limit',
            'side': side,
            'price': price,
            'amount': trade['amount'],
            'fee': fee,
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTradesPair(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response[market['id']], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
            'type': side,
            'amount': self.amount_to_precision(symbol, amount),
            'rate': self.price_to_precision(symbol, price),
        }
        response = self.privatePostTrade(self.extend(request, params))
        id = self.safe_string(response['return'], self.getOrderIdKey())
        if not id:
            id = self.safe_string(response['return'], 'init_order_id')
        timestamp = self.milliseconds()
        price = float(price)
        amount = float(amount)
        order = {
            'id': id,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': 'open',
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'cost': price * amount,
            'amount': amount,
            'remaining': amount,
            'filled': 0.0,
            'fee': None,
            # 'trades': self.parse_trades(order['trades'], market),
        }
        self.orders[id] = order
        return self.extend({'info': response}, order)

    def getOrderIdKey(self):
        return 'order_id'

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = None
        try:
            request = {}
            idKey = self.getOrderIdKey()
            request[idKey] = id
            response = self.privatePostCancelOrder(self.extend(request, params))
            if id in self.orders:
                self.orders[id]['status'] = 'canceled'
        except Exception as e:
            if self.last_json_response:
                message = self.safe_string(self.last_json_response, 'error')
                if message.find('not found') >= 0:
                    raise OrderNotFound(self.id + ' cancelOrder() error: ' + self.last_http_response)
            raise e
        return response

    def parse_order(self, order, market=None):
        id = str(order['id'])
        status = order['status']
        if status == 0:
            status = 'open'
        elif status == 1:
            status = 'closed'
        elif (status == 2) or (status == 3):
            status = 'canceled'
        timestamp = order['timestamp_created'] * 1000
        symbol = None
        if not market:
            market = self.markets_by_id[order['pair']]
        if market:
            symbol = market['symbol']
        remaining = self.safe_float(order, 'amount')
        amount = self.safe_float(order, 'start_amount', remaining)
        if amount is None:
            if id in self.orders:
                amount = self.safe_float(self.orders[id], 'amount')
        price = self.safe_float(order, 'rate')
        filled = None
        cost = None
        if amount is not None:
            filled = amount - remaining
            cost = price * filled
        fee = None
        result = {
            'info': order,
            'id': id,
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'type': 'limit',
            'side': order['type'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'remaining': remaining,
            'filled': filled,
            'status': status,
            'fee': fee,
        }
        return result

    def parse_orders(self, orders, market=None):
        ids = list(orders.keys())
        result = []
        for i in range(0, len(ids)):
            id = ids[i]
            order = orders[id]
            extended = self.extend(order, {'id': id})
            result.append(self.parse_order(extended, market))
        return result

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostOrderInfo(self.extend({
            'order_id': int(id),
        }, params))
        order = self.parse_order(self.extend({'id': id}, response['return'][id]))
        self.orders[id] = self.extend(self.orders[id], order)
        return order

    def fetch_orders(self, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOrders requires a symbol')
        self.load_markets()
        market = self.market(symbol)
        request = {'pair': market['id']}
        response = self.privatePostActiveOrders(self.extend(request, params))
        openOrders = []
        if 'return' in response:
            openOrders = self.parse_orders(response['return'], market)
        for j in range(0, len(openOrders)):
            self.orders[openOrders[j]['id']] = openOrders[j]
        openOrdersIndexedById = self.index_by(openOrders, 'id')
        cachedOrderIds = list(self.orders.keys())
        result = []
        for k in range(0, len(cachedOrderIds)):
            id = cachedOrderIds[k]
            if id in openOrdersIndexedById:
                self.orders[id] = self.extend(self.orders[id], openOrdersIndexedById[id])
            else:
                order = self.orders[id]
                if order['status'] == 'open':
                    self.orders[id] = self.extend(order, {
                        'status': 'closed',
                        'cost': order['amount'] * order['price'],
                        'filled': order['amount'],
                        'remaining': 0.0,
                    })
            order = self.orders[id]
            if order['symbol'] == symbol:
                result.append(order)
        return result

    def fetch_open_orders(self, symbol=None, params={}):
        orders = self.fetch_orders(symbol, params)
        result = []
        for i in range(0, len(orders)):
            if orders[i]['status'] == 'open':
                result.append(orders[i])
        return result

    def fetchClosedOrders(self, symbol=None, params={}):
        orders = self.fetch_orders(symbol, params)
        result = []
        for i in range(0, len(orders)):
            if orders[i]['status'] == 'closed':
                result.append(orders[i])
        return result

    def fetch_my_trades(self, symbol=None, params={}):
        self.load_markets()
        request = self.extend({
            # 'from': 123456789,  # trade ID, from which the display starts numerical 0
            'count': 1000,  # the number of trades for display numerical, default = 1000
            # 'from_id': trade ID, from which the display starts numerical 0
            # 'end_id': trade ID on which the display ends numerical ∞
            # 'order': 'ASC',  # sorting, default = DESC
            # 'since': 1234567890,  # UTC start time, default = 0
            # 'end': 1234567890,  # UTC end time, default = ∞
            # 'pair': 'eth_btc',  # default = all markets
        }, params)
        market = None
        if symbol:
            market = self.market(symbol)
            request['pair'] = market['id']
        response = self.privatePostTradeHistory(request)
        trades = []
        if 'return' in response:
            trades = response['return']
        return self.parse_trades(trades, market)

    def signBodyWithSecret(self, body):
        return self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512)

    def getVersionString(self):
        return '/' + self.version

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            nonce = self.nonce()
            body = self.urlencode(self.extend({
                'nonce': nonce,
                'method': path,
            }, query))
            signature = self.signBodyWithSecret(body)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': signature,
            }
        else:
            url += self.getVersionString() + '/' + self.implode_params(path, params)
            if query:
                url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'success' in response:
            if not response['success']:
                if response['error'].find('Not enougth') >= 0:  # not enougTh is a typo inside Liqui's own API...
                    raise InsufficientFunds(self.id + ' ' + self.json(response))
                elif response['error'] == 'Requests too often':
                    raise DDoSProtection(self.id + ' ' + self.json(response))
                elif (response['error'] == 'not available') or (response['error'] == 'external service unavailable'):
                    raise DDoSProtection(self.id + ' ' + self.json(response))
                else:
                    raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class btcmarkets (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'btcmarkets',
            'name': 'BTC Markets',
            'countries': 'AU',  # Australia
            'rateLimit': 1000,  # market data cached for 1 second (trades cached for 2 seconds)
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/29142911-0e1acfc2-7d5c-11e7-98c4-07d9532b29d7.jpg',
                'api': 'https://api.btcmarkets.net',
                'www': 'https://btcmarkets.net/',
                'doc': 'https://github.com/BTCMarkets/API',
            },
            'api': {
                'public': {
                    'get': [
                        'market/{id}/tick',
                        'market/{id}/orderbook',
                        'market/{id}/trades',
                    ],
                },
                'private': {
                    'get': [
                        'account/balance',
                        'account/{id}/tradingfee',
                    ],
                    'post': [
                        'fundtransfer/withdrawCrypto',
                        'fundtransfer/withdrawEFT',
                        'order/create',
                        'order/cancel',
                        'order/history',
                        'order/open',
                        'order/trade/history',
                        'order/createBatch',  # they promise it's coming soon...
                        'order/detail',
                    ],
                },
            },
            'markets': {
                'BTC/AUD': {'id': 'BTC/AUD', 'symbol': 'BTC/AUD', 'base': 'BTC', 'quote': 'AUD'},
                'LTC/AUD': {'id': 'LTC/AUD', 'symbol': 'LTC/AUD', 'base': 'LTC', 'quote': 'AUD'},
                'ETH/AUD': {'id': 'ETH/AUD', 'symbol': 'ETH/AUD', 'base': 'ETH', 'quote': 'AUD'},
                'ETC/AUD': {'id': 'ETC/AUD', 'symbol': 'ETC/AUD', 'base': 'ETC', 'quote': 'AUD'},
                'XRP/AUD': {'id': 'XRP/AUD', 'symbol': 'XRP/AUD', 'base': 'XRP', 'quote': 'AUD'},
                'BCH/AUD': {'id': 'BCH/AUD', 'symbol': 'BCH/AUD', 'base': 'BCH', 'quote': 'AUD'},
                'LTC/BTC': {'id': 'LTC/BTC', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'ETH/BTC': {'id': 'ETH/BTC', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
                'ETC/BTC': {'id': 'ETC/BTC', 'symbol': 'ETC/BTC', 'base': 'ETC', 'quote': 'BTC'},
                'XRP/BTC': {'id': 'XRP/BTC', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC'},
                'BCH/BTC': {'id': 'BCH/BTC', 'symbol': 'BCH/BTC', 'base': 'BCH', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(btcmarkets, self).__init__(params)

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privateGetAccountBalance()
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            multiplier = 100000000
            free = float(balance['balance'] / multiplier)
            used = float(balance['pendingFunds'] / multiplier)
            account = {
                'free': free,
                'used': used,
                'total': self.sum(free, used),
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        orderbook = self.publicGetMarketIdOrderbook(self.extend({
            'id': market['id'],
        }, params))
        timestamp = orderbook['timestamp'] * 1000
        return self.parse_order_book(orderbook, timestamp)

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['timestamp'] * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['bestBid']),
            'ask': float(ticker['bestAsk']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['lastPrice']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume24h']),
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetMarketIdTick(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'info': trade,
            'id': str(trade['tid']),
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketIdTrades(self.extend({
            # 'since': 59868345231,
            'id': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        multiplier = 100000000  # for price and volume
        # does BTC Markets support market orders at all?
        orderSide = 'Bid' if (side == 'buy') else 'Ask'
        order = self.ordered({
            'currency': market['quote'],
            'instrument': market['base'],
            'price': price * multiplier,
            'volume': amount * multiplier,
            'orderSide': orderSide,
            'ordertype': self.capitalize(type),
            'clientRequestId': str(self.nonce()),
        })
        response = self.privatePostOrderCreate(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['id']),
        }

    def cancel_orders(self, ids):
        self.load_markets()
        return self.privatePostOrderCancel({'order_ids': ids})

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.cancelOrders([id])

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        uri = '/' + self.implode_params(path, params)
        url = self.urls['api'] + uri
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            nonce = str(self.nonce())
            auth = uri + "\n" + nonce + "\n"
            headers = {
                'Content-Type': 'application/json',
                'apikey': self.apiKey,
                'timestamp': nonce,
            }
            if method == 'POST':
                body = self.urlencode(query)
                auth += body
            secret = base64.b64decode(self.secret)
            signature = self.hmac(self.encode(auth), secret, hashlib.sha512, 'base64')
            headers['signature'] = self.decode(signature)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if api == 'private':
            if 'success' in response:
                if not response['success']:
                    raise ExchangeError(self.id + ' ' + self.json(response))
            return response
        return response

# -----------------------------------------------------------------------------


class btctrader (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'btctrader',
            'name': 'BTCTrader',
            'countries': ['TR', 'GR', 'PH'],  # Turkey, Greece, Philippines
            'rateLimit': 1000,
            'hasFetchOHLCV': True,
            'timeframes': {
                '1d': '1d',
            },
            'comment': 'base API for BTCExchange, BTCTurk',
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27992404-cda1e386-649c-11e7-8dc1-40bbd2897768.jpg',
                'api': 'https://www.btctrader.com/api',
                'www': 'https://www.btctrader.com',
                'doc': 'https://github.com/BTCTrader/broker-api-docs',
            },
            'api': {
                'public': {
                    'get': [
                        'ohlcdata',  # ?last=COUNT
                        'orderbook',
                        'ticker',
                        'trades',   # ?last=COUNT (max 50)
                    ],
                },
                'private': {
                    'get': [
                        'balance',
                        'openOrders',
                        'userTransactions',  # ?offset=0&limit=25&sort=asc
                    ],
                    'post': [
                        'buy',
                        'cancelOrder',
                        'sell',
                    ],
                },
            },
        }
        params.update(config)
        super(btctrader, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privateGetBalance()
        result = {'info': response}
        base = {
            'free': response['bitcoin_available'],
            'used': response['bitcoin_reserved'],
            'total': response['bitcoin_balance'],
        }
        quote = {
            'free': response['money_available'],
            'used': response['money_reserved'],
            'total': response['money_balance'],
        }
        symbol = self.symbols[0]
        market = self.markets[symbol]
        result[market['base']] = base
        result[market['quote']] = quote
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderbook = self.publicGetOrderbook(self.extend({
            'pairSymbol': market['id'],
        }, params))
        timestamp = int(orderbook['timestamp'] * 1000)
        return self.parse_order_book(orderbook, timestamp)

    def parse_ticker(self, ticker, market=None):
        symbol = None
        if market:
            symbol = market['symbol']
        timestamp = int(ticker['timestamp']) * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': float(ticker['average']),
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTicker(params)
        result = {}
        for i in range(0, len(tickers)):
            ticker = tickers[i]
            symbol = ticker['pair']
            market = None
            if symbol in self.markets_by_id:
                market = self.markets_by_id[symbol]
                symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        tickers = self.fetch_tickers()
        result = None
        if symbol in tickers:
            result = tickers[symbol]
        return result

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'id': trade['tid'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        # maxCount = 50
        response = self.publicGetTrades(self.extend({
            'pairSymbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1d', since=None, limit=None):
        timestamp = self.parse8601(ohlcv['Time'])
        return [
            timestamp,
            ohlcv['Open'],
            ohlcv['High'],
            ohlcv['Low'],
            ohlcv['Close'],
            ohlcv['Volume'],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1d', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {}
        if limit:
            request['last'] = limit
        response = self.publicGetOhlcdata(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        method = 'privatePost' + self.capitalize(side)
        order = {
            'Type': 'BuyBtc' if (side == 'buy') else 'SelBtc',
            'IsMarketOrder': 1 if (type == 'market') else 0,
        }
        if type == 'market':
            if side == 'buy':
                order['Total'] = amount
            else:
                order['Amount'] = amount
        else:
            order['Price'] = price
            order['Amount'] = amount
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        if self.id == 'btctrader':
            raise ExchangeError(self.id + ' is an abstract base API for BTCExchange, BTCTurk')
        url = self.urls['api'] + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            nonce = self.nonce().toString
            body = self.urlencode(params)
            secret = self.base64ToString(self.secret)
            auth = self.apiKey + nonce
            headers = {
                'X-PCK': self.apiKey,
                'X-Stamp': str(nonce),
                'X-Signature': self.hmac(self.encode(auth), secret, hashlib.sha256, 'base64'),
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class btcexchange (btctrader):

    def __init__(self, config={}):
        params = {
            'id': 'btcexchange',
            'name': 'BTCExchange',
            'countries': 'PH',  # Philippines
            'rateLimit': 1500,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27993052-4c92911a-64aa-11e7-96d8-ec6ac3435757.jpg',
                'api': 'https://www.btcexchange.ph/api',
                'www': 'https://www.btcexchange.ph',
                'doc': 'https://github.com/BTCTrader/broker-api-docs',
            },
            'markets': {
                'BTC/PHP': {'id': 'BTC/PHP', 'symbol': 'BTC/PHP', 'base': 'BTC', 'quote': 'PHP'},
            },
        }
        params.update(config)
        super(btcexchange, self).__init__(params)

# -----------------------------------------------------------------------------


class btctradeua (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'btctradeua',
            'name': 'BTC Trade UA',
            'countries': 'UA',  # Ukraine,
            'rateLimit': 3000,
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27941483-79fc7350-62d9-11e7-9f61-ac47f28fcd96.jpg',
                'api': 'https://btc-trade.com.ua/api',
                'www': 'https://btc-trade.com.ua',
                'doc': 'https://docs.google.com/document/d/1ocYA0yMy_RXd561sfG3qEPZ80kyll36HUxvCRe5GbhE/edit',
            },
            'api': {
                'public': {
                    'get': [
                        'deals/{symbol}',
                        'trades/sell/{symbol}',
                        'trades/buy/{symbol}',
                        'japan_stat/high/{symbol}',
                    ],
                },
                'private': {
                    'post': [
                        'auth',
                        'ask/{symbol}',
                        'balance',
                        'bid/{symbol}',
                        'buy/{symbol}',
                        'my_orders/{symbol}',
                        'order/status/{id}',
                        'remove/order/{id}',
                        'sell/{symbol}',
                    ],
                },
            },
            'markets': {
                'BTC/UAH': {'id': 'btc_uah', 'symbol': 'BTC/UAH', 'base': 'BTC', 'quote': 'UAH'},
                'ETH/UAH': {'id': 'eth_uah', 'symbol': 'ETH/UAH', 'base': 'ETH', 'quote': 'UAH'},
                'LTC/UAH': {'id': 'ltc_uah', 'symbol': 'LTC/UAH', 'base': 'LTC', 'quote': 'UAH'},
                'DOGE/UAH': {'id': 'doge_uah', 'symbol': 'DOGE/UAH', 'base': 'DOGE', 'quote': 'UAH'},
                'DASH/UAH': {'id': 'dash_uah', 'symbol': 'DASH/UAH', 'base': 'DASH', 'quote': 'UAH'},
                'SIB/UAH': {'id': 'sib_uah', 'symbol': 'SIB/UAH', 'base': 'SIB', 'quote': 'UAH'},
                'KRB/UAH': {'id': 'krb_uah', 'symbol': 'KRB/UAH', 'base': 'KRB', 'quote': 'UAH'},
                'NVC/UAH': {'id': 'nvc_uah', 'symbol': 'NVC/UAH', 'base': 'NVC', 'quote': 'UAH'},
                'LTC/BTC': {'id': 'ltc_btc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'NVC/BTC': {'id': 'nvc_btc', 'symbol': 'NVC/BTC', 'base': 'NVC', 'quote': 'BTC'},
                'ITI/UAH': {'id': 'iti_uah', 'symbol': 'ITI/UAH', 'base': 'ITI', 'quote': 'UAH'},
                'DOGE/BTC': {'id': 'doge_btc', 'symbol': 'DOGE/BTC', 'base': 'DOGE', 'quote': 'BTC'},
                'DASH/BTC': {'id': 'dash_btc', 'symbol': 'DASH/BTC', 'base': 'DASH', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(btctradeua, self).__init__(params)

    def sign_in(self):
        return self.privatePostAuth()

    def fetch_balance(self, params={}):
        response = self.privatePostBalance()
        result = {'info': response}
        if 'accounts' in response:
            accounts = response['accounts']
            for b in range(0, len(accounts)):
                account = accounts[b]
                currency = account['currency']
                balance = float(account['balance'])
                result[currency] = {
                    'free': balance,
                    'used': 0.0,
                    'total': balance,
                }
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        bids = self.publicGetTradesBuySymbol(self.extend({
            'symbol': market['id'],
        }, params))
        asks = self.publicGetTradesSellSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        orderbook = {
            'bids': [],
            'asks': [],
        }
        if bids:
            if 'list' in bids:
                orderbook['bids'] = bids['list']
        if asks:
            if 'list' in asks:
                orderbook['asks'] = asks['list']
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'currency_trade')

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetJapanStatHighSymbol(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        orderbook = self.fetch_order_book(symbol)
        bid = None
        numBids = len(orderbook['bids'])
        if numBids > 0:
            bid = orderbook['bids'][0][0]
        ask = None
        numAsks = len(orderbook['asks'])
        if numAsks > 0:
            ask = orderbook['asks'][0][0]
        ticker = response['trades']
        timestamp = self.milliseconds()
        result = {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': bid,
            'ask': ask,
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': None,
            'info': ticker,
        }
        tickerLength = len(ticker)
        if tickerLength > 0:
            start = max(tickerLength - 48, 0)
            for t in range(start, len(ticker)):
                candle = ticker[t]
                if result['open'] is None:
                    result['open'] = candle[1]
                if (result['high'] is None) or (result['high'] < candle[2]):
                    result['high'] = candle[2]
                if (result['low'] is None) or (result['low'] > candle[3]):
                    result['low'] = candle[3]
                if result['quoteVolume'] is None:
                    result['quoteVolume'] = -candle[5]
                else:
                    result['quoteVolume'] -= candle[5]
            last = tickerLength - 1
            result['close'] = ticker[last][4]
            result['quoteVolume'] = -1 * result['quoteVolume']
        return result

    def parse_trade(self, trade, market):
        timestamp = self.milliseconds()  # until we have a better solution for python
        return {
            'id': str(trade['id']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['amnt_trade']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetDealsSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        market = self.market(symbol)
        method = 'privatePost' + self.capitalize(side) + 'Id'
        order = {
            'count': amount,
            'currency1': market['quote'],
            'currency': market['base'],
            'price': price,
        }
        return getattr(self, method)(self.extend(order, params))

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostRemoveOrderId({'id': id})

    def parse_order(self, trade, market):
        timestamp = self.milliseconds
        return {
            'id': trade['id'],
            'timestamp': timestamp,  # until they fix their timestamp
            'datetime': self.iso8601(timestamp),
            'status': 'open',
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': trade['price'],
            'amount': trade['amnt_trade'],
            'filled': 0,
            'remaining': trade['amnt_trade'],
            'trades': None,
            'info': trade,
        }

    def fetch_open_orders(self, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOpenOrders requires a symbol param')
        market = self.market(symbol)
        response = self.privatePostMyOrdersSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        orders = response['your_open_orders']
        return self.parse_orders(orders, market)

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += self.implode_params(path, query)
        else:
            nonce = self.nonce()
            body = self.urlencode(self.extend({
                'out_order_id': nonce,
                'nonce': nonce,
            }, query))
            auth = body + self.secret
            headers = {
                'public-key': self.apiKey,
                'api-sign': self.hash(self.encode(auth), 'sha256'),
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class btcturk (btctrader):

    def __init__(self, config={}):
        params = {
            'id': 'btcturk',
            'name': 'BTCTurk',
            'countries': 'TR',  # Turkey
            'rateLimit': 1000,
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27992709-18e15646-64a3-11e7-9fa2-b0950ec7712f.jpg',
                'api': 'https://www.btcturk.com/api',
                'www': 'https://www.btcturk.com',
                'doc': 'https://github.com/BTCTrader/broker-api-docs',
            },
            'markets': {
                'BTC/TRY': {'id': 'BTCTRY', 'symbol': 'BTC/TRY', 'base': 'BTC', 'quote': 'TRY'},
                'ETH/TRY': {'id': 'ETHTRY', 'symbol': 'ETH/TRY', 'base': 'ETH', 'quote': 'TRY'},
                'ETH/BTC': {'id': 'ETHBTC', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(btcturk, self).__init__(params)

# -----------------------------------------------------------------------------


class btcx (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'btcx',
            'name': 'BTCX',
            'countries': ['IS', 'US', 'EU'],
            'rateLimit': 1500,  # support in english is very poor, unable to tell rate limits
            'version': 'v1',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766385-9fdcc98c-5ed6-11e7-8f14-66d5e5cd47e6.jpg',
                'api': 'https://btc-x.is/api',
                'www': 'https://btc-x.is',
                'doc': 'https://btc-x.is/custom/api-document.html',
            },
            'api': {
                'public': {
                    'get': [
                        'depth/{id}/{limit}',
                        'ticker/{id}',
                        'trade/{id}/{limit}',
                    ],
                },
                'private': {
                    'post': [
                        'balance',
                        'cancel',
                        'history',
                        'order',
                        'redeem',
                        'trade',
                        'withdraw',
                    ],
                },
            },
            'markets': {
                'BTC/USD': {'id': 'btc/usd', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'BTC/EUR': {'id': 'btc/eur', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
            },
        }
        params.update(config)
        super(btcx, self).__init__(params)

    def fetch_balance(self, params={}):
        balances = self.privatePostBalance()
        result = {'info': balances}
        currencies = list(balances.keys())
        for c in range(0, len(currencies)):
            currency = currencies[c]
            uppercase = currency.upper()
            account = {
                'free': balances[currency],
                'used': 0.0,
                'total': balances[currency],
            }
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetDepthIdLimit(self.extend({
            'id': self.market_id(symbol),
            'limit': 1000,
        }, params))
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetTickerId(self.extend({
            'id': self.market_id(symbol),
        }, params))
        timestamp = ticker['time'] * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['sell']),
            'ask': float(ticker['buy']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = int(trade['date']) * 1000
        side = 'sell' if (trade['type'] == 'ask') else 'buy'
        return {
            'id': trade['id'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTradeIdLimit(self.extend({
            'id': market['id'],
            'limit': 1000,
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        response = self.privatePostTrade(self.extend({
            'type': side.upper(),
            'market': self.market_id(symbol),
            'amount': amount,
            'price': price,
        }, params))
        return {
            'info': response,
            'id': response['order']['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancel({'order': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/'
        if api == 'public':
            url += self.implode_params(path, params)
        else:
            nonce = self.nonce()
            url += api
            body = self.urlencode(self.extend({
                'Method': path.upper(),
                'Nonce': nonce,
            }, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Signature': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class bter (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bter',
            'name': 'Bter',
            'countries': ['VG', 'CN'],  # British Virgin Islands, China
            'version': '2',
            'hasCORS': False,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27980479-cfa3188c-6387-11e7-8191-93fc4184ba5c.jpg',
                'api': {
                    'public': 'https://data.bter.com/api',
                    'private': 'https://api.bter.com/api',
                },
                'www': 'https://bter.com',
                'doc': 'https://bter.com/api2',
            },
            'api': {
                'public': {
                    'get': [
                        'pairs',
                        'marketinfo',
                        'marketlist',
                        'tickers',
                        'ticker/{id}',
                        'orderBook/{id}',
                        'trade/{id}',
                        'tradeHistory/{id}',
                        'tradeHistory/{id}/{tid}',
                    ],
                },
                'private': {
                    'post': [
                        'balances',
                        'depositAddress',
                        'newAddress',
                        'depositsWithdrawals',
                        'buy',
                        'sell',
                        'cancelOrder',
                        'cancelAllOrders',
                        'getOrder',
                        'openOrders',
                        'tradeHistory',
                        'withdraw',
                    ],
                },
            },
        }
        params.update(config)
        super(bter, self).__init__(params)

    def fetch_markets(self):
        response = self.publicGetMarketinfo()
        markets = response['pairs']
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            keys = list(market.keys())
            id = keys[0]
            details = market[id]
            base, quote = id.split('_')
            base = base.upper()
            quote = quote.upper()
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            precision = {
                'amount': details['decimal_places'],
                'price': details['decimal_places'],
            }
            amountLimits = {
                'min': details['min_amount'],
                'max': None,
            }
            priceLimits = {
                'min': None,
                'max': None,
            }
            limits = {
                'amount': amountLimits,
                'price': priceLimits,
            }
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
                'maker': details['fee'] / 100,
                'taker': details['fee'] / 100,
                'precision': precision,
                'limits': limits,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balance = self.privatePostBalances()
        result = {'info': balance}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            code = self.common_currency_code(currency)
            account = self.account()
            if 'available' in balance:
                if currency in balance['available']:
                    account['free'] = float(balance['available'][currency])
            if 'locked' in balance:
                if currency in balance['locked']:
                    account['used'] = float(balance['locked'][currency])
            account['total'] = self.sum(account['free'], account['used'])
            result[code] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetOrderBookId(self.extend({
            'id': self.market_id(symbol),
        }, params))
        result = self.parse_order_book(orderbook)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high24hr']),
            'low': float(ticker['low24hr']),
            'bid': float(ticker['highestBid']),
            'ask': float(ticker['lowestAsk']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': float(ticker['percentChange']),
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['quoteVolume']),
            'quoteVolume': float(ticker['baseVolume']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTickers(params)
        result = {}
        ids = list(tickers.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            baseId, quoteId = id.split('_')
            base = baseId.upper()
            quote = quoteId.upper()
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            ticker = tickers[id]
            market = None
            if symbol in self.markets:
                market = self.markets[symbol]
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetTickerId(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = self.parse8601(trade['date'])
        return {
            'id': trade['tradeID'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': trade['rate'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        self.load_markets()
        response = self.publicGetTradeHistoryId(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_trades(response['data'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        self.load_markets()
        method = 'privatePost' + self.capitalize(side)
        order = {
            'currencyPair': self.market_id(symbol),
            'rate': price,
            'amount': amount,
        }
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['orderNumber'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostCancelOrder({'orderNumber': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        prefix = (api + '/') if (api == 'private') else ''
        url = self.urls['api'][api] + self.version + '/1/' + prefix + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            request = {'nonce': nonce}
            body = self.urlencode(self.extend(request, query))
            signature = self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512)
            headers = {
                'Key': self.apiKey,
                'Sign': signature,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'result' in response:
            if response['result'] != 'true':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class bxinth (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'bxinth',
            'name': 'BX.in.th',
            'countries': 'TH',  # Thailand
            'rateLimit': 1500,
            'hasCORS': False,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766412-567b1eb4-5ed7-11e7-94a8-ff6a3884f6c5.jpg',
                'api': 'https://bx.in.th/api',
                'www': 'https://bx.in.th',
                'doc': 'https://bx.in.th/info/api',
            },
            'api': {
                'public': {
                    'get': [
                        '',  # ticker
                        'options',
                        'optionbook',
                        'orderbook',
                        'pairing',
                        'trade',
                        'tradehistory',
                    ],
                },
                'private': {
                    'post': [
                        'balance',
                        'biller',
                        'billgroup',
                        'billpay',
                        'cancel',
                        'deposit',
                        'getorders',
                        'history',
                        'option-issue',
                        'option-bid',
                        'option-sell',
                        'option-myissue',
                        'option-mybid',
                        'option-myoptions',
                        'option-exercise',
                        'option-cancel',
                        'option-history',
                        'order',
                        'withdrawal',
                        'withdrawal-history',
                    ],
                },
            },
        }
        params.update(config)
        super(bxinth, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetPairing()
        keys = list(markets.keys())
        result = []
        for p in range(0, len(keys)):
            market = markets[keys[p]]
            id = str(market['pairing_id'])
            base = market['secondary_currency']
            quote = market['primary_currency']
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def common_currency_code(self, currency):
        # why would they use three letters instead of four for currency codes
        if currency == 'DAS':
            return 'DASH'
        if currency == 'DOG':
            return 'DOGE'
        return currency

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostBalance()
        balance = response['balance']
        result = {'info': balance}
        currencies = list(balance.keys())
        for c in range(0, len(currencies)):
            currency = currencies[c]
            code = self.common_currency_code(currency)
            account = {
                'free': float(balance[currency]['available']),
                'used': 0.0,
                'total': float(balance[currency]['total']),
            }
            account['used'] = account['total'] - account['free']
            result[code] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetOrderbook(self.extend({
            'pairing': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['orderbook']['bids']['highbid']),
            'ask': float(ticker['orderbook']['asks']['highbid']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last_price']),
            'change': float(ticker['change']),
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume_24hours']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGet(params)
        result = {}
        ids = list(tickers.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            ticker = tickers[id]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        tickers = self.publicGet(self.extend({
            'pairing': market['id'],
        }, params))
        id = str(market['id'])
        ticker = tickers[id]
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = self.parse8601(trade['trade_date'])
        return {
            'id': trade['trade_id'],
            'info': trade,
            'order': trade['order_id'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['trade_type'],
            'price': float(trade['rate']),
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrade(self.extend({
            'pairing': market['id'],
        }, params))
        return self.parse_trades(response['trades'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        response = self.privatePostOrder(self.extend({
            'pairing': self.market_id(symbol),
            'type': side,
            'amount': amount,
            'rate': price,
        }, params))
        return {
            'info': response,
            'id': str(response['order_id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        pairing = None  # TODO fixme
        return self.privatePostCancel({
            'order_id': id,
            'pairing': pairing,
        })

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/'
        if path:
            url += path + '/'
        if params:
            url += '?' + self.urlencode(params)
        if api == 'private':
            nonce = self.nonce()
            auth = self.apiKey + str(nonce) + self.secret
            signature = self.hash(self.encode(auth), 'sha256')
            body = self.urlencode(self.extend({
                'key': self.apiKey,
                'nonce': nonce,
                'signature': signature,
                # twofa: self.twofa,
            }, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if api == 'public':
            return response
        if 'success' in response:
            if response['success']:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class ccex (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'ccex',
            'name': 'C-CEX',
            'countries': ['DE', 'EU'],
            'rateLimit': 1500,
            'hasCORS': False,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766433-16881f90-5ed8-11e7-92f8-3d92cc747a6c.jpg',
                'api': {
                    'tickers': 'https://c-cex.com/t',
                    'public': 'https://c-cex.com/t/api_pub.html',
                    'private': 'https://c-cex.com/t/api.html',
                },
                'www': 'https://c-cex.com',
                'doc': 'https://c-cex.com/?id=api',
            },
            'api': {
                'tickers': {
                    'get': [
                        'coinnames',
                        '{market}',
                        'pairs',
                        'prices',
                        'volume_{coin}',
                    ],
                },
                'public': {
                    'get': [
                        'balancedistribution',
                        'markethistory',
                        'markets',
                        'marketsummaries',
                        'orderbook',
                    ],
                },
                'private': {
                    'get': [
                        'buylimit',
                        'cancel',
                        'getbalance',
                        'getbalances',
                        'getopenorders',
                        'getorder',
                        'getorderhistory',
                        'mytrades',
                        'selllimit',
                    ],
                },
            },
        }
        params.update(config)
        super(ccex, self).__init__(params)

    def common_currency_code(self, currency):
        if currency == 'IOT':
            return 'IoTcoin'
        if currency == 'BLC':
            return 'Cryptobullcoin'
        return currency

    def fetch_markets(self):
        markets = self.publicGetMarkets()
        result = []
        for p in range(0, len(markets['result'])):
            market = markets['result'][p]
            id = market['MarketName']
            base = market['MarketCurrency']
            quote = market['BaseCurrency']
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalances()
        balances = response['result']
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            code = balance['Currency']
            currency = self.common_currency_code(code)
            account = {
                'free': balance['Available'],
                'used': balance['Pending'],
                'total': balance['Balance'],
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetOrderbook(self.extend({
            'market': self.market_id(symbol),
            'type': 'both',
            'depth': 100,
        }, params))
        orderbook = response['result']
        return self.parse_order_book(orderbook, None, 'buy', 'sell', 'Rate', 'Quantity')

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['updated'] * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['lastprice']),
            'change': None,
            'percentage': None,
            'average': float(ticker['avg']),
            'baseVolume': None,
            'quoteVolume': self.safe_float(ticker, 'buysupport'),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.tickersGetPrices(params)
        result = {'info': tickers}
        ids = list(tickers.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            ticker = tickers[id]
            uppercase = id.upper()
            market = None
            symbol = None
            if uppercase in self.markets_by_id:
                market = self.markets_by_id[uppercase]
                symbol = market['symbol']
            else:
                base, quote = uppercase.split('-')
                base = self.common_currency_code(base)
                quote = self.common_currency_code(quote)
                symbol = base + '/' + quote
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.tickersGetMarket(self.extend({
            'market': market['id'].lower(),
        }, params))
        ticker = response['ticker']
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = self.parse8601(trade['TimeStamp'])
        return {
            'id': trade['Id'],
            'info': trade,
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['OrderType'].lower(),
            'price': trade['Price'],
            'amount': trade['Quantity'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarkethistory(self.extend({
            'market': market['id'],
            'type': 'both',
            'depth': 100,
        }, params))
        return self.parse_trades(response['result'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        method = 'privateGet' + self.capitalize(side) + type
        response = getattr(self, method)(self.extend({
            'market': self.market_id(symbol),
            'quantity': amount,
            'rate': price,
        }, params))
        return {
            'info': response,
            'id': response['result']['uuid'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privateGetCancel({'uuid': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        if api == 'private':
            nonce = str(self.nonce())
            query = self.keysort(self.extend({
                'a': path,
                'apikey': self.apiKey,
                'nonce': nonce,
            }, params))
            url += '?' + self.urlencode(query)
            headers = {'apisign': self.hmac(self.encode(url), self.encode(self.secret), hashlib.sha512)}
        elif api == 'public':
            url += '?' + self.urlencode(self.extend({
                'a': 'get' + path,
            }, params))
        else:
            url += '/' + self.implode_params(path, params) + '.json'
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if api == 'tickers':
            return response
        if 'success' in response:
            if response['success']:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class cex (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'cex',
            'name': 'CEX.IO',
            'countries': ['GB', 'EU', 'CY', 'RU'],
            'rateLimit': 1500,
            'hasCORS': True,
            'hasFetchOHLCV': True,
            'hasFetchTickers': False,
            'hasFetchOpenOrders': True,
            'timeframes': {
                '1m': '1m',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766442-8ddc33b0-5ed8-11e7-8b98-f786aef0f3c9.jpg',
                'api': 'https://cex.io/api',
                'www': 'https://cex.io',
                'doc': 'https://cex.io/cex-api',
            },
            'api': {
                'public': {
                    'get': [
                        'currency_limits/',
                        'last_price/{pair}/',
                        'last_prices/{currencies}/',
                        'ohlcv/hd/{yyyymmdd}/{pair}',
                        'order_book/{pair}/',
                        'ticker/{pair}/',
                        'tickers/{currencies}/',
                        'trade_history/{pair}/',
                    ],
                    'post': [
                        'convert/{pair}',
                        'price_stats/{pair}',
                    ],
                },
                'private': {
                    'post': [
                        'active_orders_status/',
                        'archived_orders/{pair}/',
                        'balance/',
                        'cancel_order/',
                        'cancel_orders/{pair}/',
                        'cancel_replace_order/{pair}/',
                        'close_position/{pair}/',
                        'get_address/',
                        'get_myfee/',
                        'get_order/',
                        'get_order_tx/',
                        'open_orders/{pair}/',
                        'open_orders/',
                        'open_position/{pair}/',
                        'open_positions/{pair}/',
                        'place_order/{pair}/',
                    ],
                }
            },
            'fees': {
                'trading': {
                    'maker': 0,
                    'taker': 0.2 / 100,
                },
            },
        }
        params.update(config)
        super(cex, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetCurrencyLimits()
        result = []
        for p in range(0, len(markets['data']['pairs'])):
            market = markets['data']['pairs'][p]
            id = market['symbol1'] + '/' + market['symbol2']
            symbol = id
            base, quote = symbol.split('/')
            precision = {
                'price': 4,
                'amount': -1 * math.log10(market['minLotSize']),
            }
            amountLimits = {
                'min': market['minLotSize'],
                'max': market['maxLotSize'],
            }
            priceLimits = {
                'min': market['minPrice'],
                'max': market['maxPrice'],
            }
            limits = {
                'amount': amountLimits,
                'price': priceLimits,
            }
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'precision': precision,
                'limits': limits,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privatePostBalance()
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            if currency in balances:
                account = {
                    'free': float(balances[currency]['available']),
                    'used': float(balances[currency]['orders']),
                    'total': 0.0,
                }
                account['total'] = self.sum(account['free'], account['used'])
                result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetOrderBookPair(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = orderbook['timestamp'] * 1000
        return self.parse_order_book(orderbook, timestamp)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv[0] * 1000,
            ohlcv[1],
            ohlcv[2],
            ohlcv[3],
            ohlcv[4],
            ohlcv[5],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        if not since:
            since = self.milliseconds() - 86400000  # yesterday
        ymd = self.Ymd(since)
        ymd = ymd.split('-')
        ymd = ''.join(ymd)
        request = {
            'pair': market['id'],
            'yyyymmdd': ymd,
        }
        response = self.publicGetOhlcvHdYyyymmddPair(self.extend(request, params))
        key = 'data' + self.timeframes[timeframe]
        ohlcvs = self.unjson(response[key])
        return self.parse_ohlcvs(ohlcvs, market, timeframe, since, limit)

    def parse_ticker(self, ticker, market=None):
        timestamp = None
        iso8601 = None
        if 'timestamp' in ticker:
            timestamp = int(ticker['timestamp']) * 1000
            iso8601 = self.iso8601(timestamp)
        volume = self.safe_float(ticker, 'volume')
        high = self.safe_float(ticker, 'high')
        low = self.safe_float(ticker, 'low')
        bid = self.safe_float(ticker, 'bid')
        ask = self.safe_float(ticker, 'ask')
        last = self.safe_float(ticker, 'last')
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': iso8601,
            'high': high,
            'low': low,
            'bid': bid,
            'ask': ask,
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': last,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': volume,
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        currencies = '/'.join(self.currencies)
        response = self.publicGetTickersCurrencies(self.extend({
            'currencies': currencies,
        }, params))
        tickers = response['data']
        result = {}
        for t in range(0, len(tickers)):
            ticker = tickers[t]
            symbol = ticker['pair'].replace(':', '/')
            market = self.markets[symbol]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetTickerPair(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market=None):
        timestamp = int(trade['date']) * 1000
        return {
            'info': trade,
            'id': trade['tid'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTradeHistoryPair(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'pair': self.market_id(symbol),
            'type': side,
            'amount': amount,
        }
        if type == 'limit':
            order['price'] = price
        else:
            order['order_type'] = type
        response = self.privatePostPlaceOrderPair(self.extend(order, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostCancelOrder({'id': id})

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostGetOrder(self.extend({
            'id': str(id),
        }, params))

    def parse_order(self, order, market=None):
        timestamp = int(order['time'])
        symbol = None
        if not market:
            symbol = order['symbol1'] + '/' + order['symbol2']
            if symbol in self.markets:
                market = self.market(symbol)
        status = order['status']
        if status == 'cd':
            status = 'canceled'
        elif status == 'c':
            status = 'canceled'
        elif status == 'd':
            status = 'closed'
        price = self.safe_float(order, 'price')
        amount = self.safe_float(order, 'amount')
        remaining = self.safe_float(order, 'pending')
        if not remaining:
            remaining = self.safe_float(order, 'remains')
        filled = amount - remaining
        fee = None
        cost = None
        if market:
            symbol = market['symbol']
            cost = self.safe_float(order, 'ta:' + market['quote'])
            baseFee = 'fa:' + market['base']
            quoteFee = 'fa:' + market['quote']
            feeRate = self.safe_float(order, 'tradingFeeMaker')
            if not feeRate:
                feeRate = self.safe_float(order, 'tradingFeeTaker', feeRate)
            if feeRate:
                feeRate /= 100.0  # convert to mathematically-correct percentage coefficients: 1.0 = 100%
            if baseFee in order:
                fee = {
                    'currency': market['base'],
                    'rate': feeRate,
                    'cost': self.safe_float(order, baseFee),
                }
            elif quoteFee in order:
                fee = {
                    'currency': market['quote'],
                    'rate': feeRate,
                    'cost': self.safe_float(order, quoteFee),
                }
        if not cost:
            cost = price * filled
        return {
            'id': order['id'],
            'datetime': self.iso8601(timestamp),
            'timestamp': timestamp,
            'status': status,
            'symbol': symbol,
            'type': None,
            'side': order['type'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': None,
            'fee': fee,
            'info': order,
        }

    def fetch_open_orders(self, symbol=None, params={}):
        self.loadMarkets()
        request = {}
        method = 'privatePostOpenOrders'
        market = None
        if symbol:
            market = self.market(symbol)
            request['pair'] = market['id']
            method += 'Pair'
        orders = getattr(self, method)(self.extend(request, params))
        for i in range(0, len(orders)):
            orders[i] = self.extend(orders[i], {'status': 'open'})
        return self.parse_orders(orders, market)

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            if not self.uid:
                raise AuthenticationError(self.id + ' requires `' + self.id + '.uid` property for authentication')
            nonce = str(self.nonce())
            auth = nonce + self.uid + self.apiKey
            signature = self.hmac(self.encode(auth), self.encode(self.secret))
            body = self.urlencode(self.extend({
                'key': self.apiKey,
                'signature': signature.upper(),
                'nonce': nonce,
            }, query))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if not response:
            raise ExchangeError(self.id + ' returned ' + self.json(response))
        elif response is True:
            return response
        elif 'e' in response:
            if 'ok' in response:
                if response['ok'] == 'ok':
                    return response
            raise ExchangeError(self.id + ' ' + self.json(response))
        elif 'error' in response:
            if response['error']:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class chbtc (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'chbtc',
            'name': 'CHBTC',
            'countries': 'CN',
            'rateLimit': 1000,
            'version': 'v1',
            'hasCORS': False,
            'hasFetchOrder': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28555659-f0040dc2-7109-11e7-9d99-688a438bf9f4.jpg',
                'api': {
                    'public': 'http://api.chbtc.com/data',  # no https for public API
                    'private': 'https://trade.chbtc.com/api',
                },
                'www': 'https://trade.chbtc.com/api',
                'doc': 'https://www.chbtc.com/i/developer',
            },
            'api': {
                'public': {
                    'get': [
                        'ticker',
                        'depth',
                        'trades',
                        'kline',
                    ],
                },
                'private': {
                    'post': [
                        'order',
                        'cancelOrder',
                        'getOrder',
                        'getOrders',
                        'getOrdersNew',
                        'getOrdersIgnoreTradeType',
                        'getUnfinishedOrdersIgnoreTradeType',
                        'getAccountInfo',
                        'getUserAddress',
                        'getWithdrawAddress',
                        'getWithdrawRecord',
                        'getChargeRecord',
                        'getCnyWithdrawRecord',
                        'getCnyChargeRecord',
                        'withdraw',
                    ],
                },
            },
            'markets': {
                'BTC/CNY': {'id': 'btc_cny', 'symbol': 'BTC/CNY', 'base': 'BTC', 'quote': 'CNY'},
                'LTC/CNY': {'id': 'ltc_cny', 'symbol': 'LTC/CNY', 'base': 'LTC', 'quote': 'CNY'},
                'ETH/CNY': {'id': 'eth_cny', 'symbol': 'ETH/CNY', 'base': 'ETH', 'quote': 'CNY'},
                'ETC/CNY': {'id': 'etc_cny', 'symbol': 'ETC/CNY', 'base': 'ETC', 'quote': 'CNY'},
                'BTS/CNY': {'id': 'bts_cny', 'symbol': 'BTS/CNY', 'base': 'BTS', 'quote': 'CNY'},
                # 'EOS/CNY': {'id': 'eos_cny', 'symbol': 'EOS/CNY', 'base': 'EOS', 'quote': 'CNY'},
                'BCH/CNY': {'id': 'bcc_cny', 'symbol': 'BCH/CNY', 'base': 'BCH', 'quote': 'CNY'},
                'HSR/CNY': {'id': 'hsr_cny', 'symbol': 'HSR/CNY', 'base': 'HSR', 'quote': 'CNY'},
                'QTUM/CNY': {'id': 'qtum_cny', 'symbol': 'QTUM/CNY', 'base': 'QTUM', 'quote': 'CNY'},
            },
        }
        params.update(config)
        super(chbtc, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privatePostGetAccountInfo()
        balances = response['result']
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in balances['balance']:
                account['free'] = float(balances['balance'][currency]['amount'])
            if currency in balances['frozen']:
                account['used'] = float(balances['frozen'][currency]['amount'])
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderbook = self.publicGetDepth(self.extend({
            'currency': market['id'],
        }, params))
        timestamp = self.milliseconds()
        bids = None
        asks = None
        if 'bids' in orderbook:
            bids = orderbook['bids']
        if 'asks' in orderbook:
            asks = orderbook['asks']
        result = {
            'bids': bids,
            'asks': asks,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
        }
        if result['bids']:
            result['bids'] = self.sort_by(result['bids'], 0, True)
        if result['asks']:
            result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetTicker(self.extend({
            'currency': self.market_id(symbol),
        }, params))
        ticker = response['ticker']
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['vol']),
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        timestamp = trade['date'] * 1000
        side = 'buy' if (trade['trade_type'] == 'bid') else 'sell'
        return {
            'info': trade,
            'id': str(trade['tid']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'currency': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        paramString = '&price=' + str(price)
        paramString += '&amount=' + str(amount)
        tradeType = '1' if (side == 'buy') else '0'
        paramString += '&tradeType=' + tradeType
        paramString += '&currency=' + self.market_id(symbol)
        response = self.privatePostOrder(paramString)
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        paramString = '&id=' + str(id)
        if 'currency' in params:
            paramString += '&currency=' + params['currency']
        return self.privatePostCancelOrder(paramString)

    def fetch_order(self, id, symbol=None, params={}):
        paramString = '&id=' + str(id)
        if 'currency' in params:
            paramString += '&currency=' + params['currency']
        return self.privatePostGetOrder(paramString)

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        if api == 'public':
            url += '/' + self.version + '/' + path
            if params:
                url += '?' + self.urlencode(params)
        else:
            paramsLength = len(params)  # params should be a string here
            nonce = self.nonce()
            auth = 'method=' + path
            auth += '&accesskey=' + self.apiKey
            auth += params if paramsLength else ''
            secret = self.hash(self.encode(self.secret), 'sha1')
            signature = self.hmac(self.encode(auth), self.encode(secret), hashlib.md5)
            suffix = 'sign=' + signature + '&reqTime=' + str(nonce)
            url += '/' + path + '?' + auth + '&' + suffix
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if api == 'private':
            if 'code' in response:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class chilebit (blinktrade):

    def __init__(self, config={}):
        params = {
            'id': 'chilebit',
            'name': 'ChileBit',
            'countries': 'CL',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27991414-1298f0d8-647f-11e7-9c40-d56409266336.jpg',
                'api': {
                    'public': 'https://api.blinktrade.com/api',
                    'private': 'https://api.blinktrade.com/tapi',
                },
                'www': 'https://chilebit.net',
                'doc': 'https://blinktrade.com/docs',
            },
            'comment': 'Blinktrade API',
            'markets': {
                'BTC/CLP': {'id': 'BTCCLP', 'symbol': 'BTC/CLP', 'base': 'BTC', 'quote': 'CLP', 'brokerId': 9, 'broker': 'ChileBit'},
            },
        }
        params.update(config)
        super(chilebit, self).__init__(params)

# -----------------------------------------------------------------------------


class coincheck (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'coincheck',
            'name': 'coincheck',
            'countries': ['JP', 'ID'],
            'rateLimit': 1500,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766464-3b5c3c74-5ed9-11e7-840e-31b32968e1da.jpg',
                'api': 'https://coincheck.com/api',
                'www': 'https://coincheck.com',
                'doc': 'https://coincheck.com/documents/exchange/api',
            },
            'api': {
                'public': {
                    'get': [
                        'exchange/orders/rate',
                        'order_books',
                        'rate/{pair}',
                        'ticker',
                        'trades',
                    ],
                },
                'private': {
                    'get': [
                        'accounts',
                        'accounts/balance',
                        'accounts/leverage_balance',
                        'bank_accounts',
                        'deposit_money',
                        'exchange/orders/opens',
                        'exchange/orders/transactions',
                        'exchange/orders/transactions_pagination',
                        'exchange/leverage/positions',
                        'lending/borrows/matches',
                        'send_money',
                        'withdraws',
                    ],
                    'post': [
                        'bank_accounts',
                        'deposit_money/{id}/fast',
                        'exchange/orders',
                        'exchange/transfers/to_leverage',
                        'exchange/transfers/from_leverage',
                        'lending/borrows',
                        'lending/borrows/{id}/repay',
                        'send_money',
                        'withdraws',
                    ],
                    'delete': [
                        'bank_accounts/{id}',
                        'exchange/orders/{id}',
                        'withdraws/{id}',
                    ],
                },
            },
            'markets': {
                'BTC/JPY': {'id': 'btc_jpy', 'symbol': 'BTC/JPY', 'base': 'BTC', 'quote': 'JPY'},  # the only real pair
                # 'ETH/JPY': {'id': 'eth_jpy', 'symbol': 'ETH/JPY', 'base': 'ETH', 'quote': 'JPY'},
                # 'ETC/JPY': {'id': 'etc_jpy', 'symbol': 'ETC/JPY', 'base': 'ETC', 'quote': 'JPY'},
                # 'DAO/JPY': {'id': 'dao_jpy', 'symbol': 'DAO/JPY', 'base': 'DAO', 'quote': 'JPY'},
                # 'LSK/JPY': {'id': 'lsk_jpy', 'symbol': 'LSK/JPY', 'base': 'LSK', 'quote': 'JPY'},
                # 'FCT/JPY': {'id': 'fct_jpy', 'symbol': 'FCT/JPY', 'base': 'FCT', 'quote': 'JPY'},
                # 'XMR/JPY': {'id': 'xmr_jpy', 'symbol': 'XMR/JPY', 'base': 'XMR', 'quote': 'JPY'},
                # 'REP/JPY': {'id': 'rep_jpy', 'symbol': 'REP/JPY', 'base': 'REP', 'quote': 'JPY'},
                # 'XRP/JPY': {'id': 'xrp_jpy', 'symbol': 'XRP/JPY', 'base': 'XRP', 'quote': 'JPY'},
                # 'ZEC/JPY': {'id': 'zec_jpy', 'symbol': 'ZEC/JPY', 'base': 'ZEC', 'quote': 'JPY'},
                # 'XEM/JPY': {'id': 'xem_jpy', 'symbol': 'XEM/JPY', 'base': 'XEM', 'quote': 'JPY'},
                # 'LTC/JPY': {'id': 'ltc_jpy', 'symbol': 'LTC/JPY', 'base': 'LTC', 'quote': 'JPY'},
                # 'DASH/JPY': {'id': 'dash_jpy', 'symbol': 'DASH/JPY', 'base': 'DASH', 'quote': 'JPY'},
                # 'ETH/BTC': {'id': 'eth_btc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
                # 'ETC/BTC': {'id': 'etc_btc', 'symbol': 'ETC/BTC', 'base': 'ETC', 'quote': 'BTC'},
                # 'LSK/BTC': {'id': 'lsk_btc', 'symbol': 'LSK/BTC', 'base': 'LSK', 'quote': 'BTC'},
                # 'FCT/BTC': {'id': 'fct_btc', 'symbol': 'FCT/BTC', 'base': 'FCT', 'quote': 'BTC'},
                # 'XMR/BTC': {'id': 'xmr_btc', 'symbol': 'XMR/BTC', 'base': 'XMR', 'quote': 'BTC'},
                # 'REP/BTC': {'id': 'rep_btc', 'symbol': 'REP/BTC', 'base': 'REP', 'quote': 'BTC'},
                # 'XRP/BTC': {'id': 'xrp_btc', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC'},
                # 'ZEC/BTC': {'id': 'zec_btc', 'symbol': 'ZEC/BTC', 'base': 'ZEC', 'quote': 'BTC'},
                # 'XEM/BTC': {'id': 'xem_btc', 'symbol': 'XEM/BTC', 'base': 'XEM', 'quote': 'BTC'},
                # 'LTC/BTC': {'id': 'ltc_btc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                # 'DASH/BTC': {'id': 'dash_btc', 'symbol': 'DASH/BTC', 'base': 'DASH', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(coincheck, self).__init__(params)

    def fetch_balance(self, params={}):
        balances = self.privateGetAccountsBalance()
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = self.account()
            if lowercase in balances:
                account['free'] = float(balances[lowercase])
            reserved = lowercase + '_reserved'
            if reserved in balances:
                account['used'] = float(balances[reserved])
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        if symbol != 'BTC/JPY':
            raise NotSupported(self.id + ' fetchOrderBook() supports BTC/JPY only')
        orderbook = self.publicGetOrderBooks(params)
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        if symbol != 'BTC/JPY':
            raise NotSupported(self.id + ' fetchTicker() supports BTC/JPY only')
        ticker = self.publicGetTicker(params)
        timestamp = ticker['timestamp'] * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = self.parse8601(trade['created_at'])
        return {
            'id': str(trade['id']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['order_type'],
            'price': float(trade['rate']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        if symbol != 'BTC/JPY':
            raise NotSupported(self.id + ' fetchTrades() supports BTC/JPY only')
        market = self.market(symbol)
        response = self.publicGetTrades(params)
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        prefix = ''
        order = {
            'pair': self.market_id(symbol),
        }
        if type == 'market':
            order_type = type + '_' + side
            order['order_type'] = order_type
            prefix = (order_type + '_') if (side == 'buy') else ''
            order[prefix + 'amount'] = amount
        else:
            order['order_type'] = side
            order['rate'] = price
            order['amount'] = amount
        response = self.privatePostExchangeOrders(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privateDeleteExchangeOrdersId({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = str(self.nonce())
            if query:
                body = self.urlencode(self.keysort(query))
            auth = nonce + url + (body or '')
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'ACCESS-KEY': self.apiKey,
                'ACCESS-NONCE': nonce,
                'ACCESS-SIGNATURE': self.hmac(self.encode(auth), self.encode(self.secret)),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if api == 'public':
            return response
        if 'success' in response:
            if response['success']:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class coinfloor (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'coinfloor',
            'name': 'coinfloor',
            'rateLimit': 1000,
            'countries': 'UK',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28246081-623fc164-6a1c-11e7-913f-bac0d5576c90.jpg',
                'api': 'https://webapi.coinfloor.co.uk:8090/bist',
                'www': 'https://www.coinfloor.co.uk',
                'doc': [
                    'https://github.com/coinfloor/api',
                    'https://www.coinfloor.co.uk/api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        '{id}/ticker/',
                        '{id}/order_book/',
                        '{id}/transactions/',
                    ],
                },
                'private': {
                    'post': [
                        '{id}/balance/',
                        '{id}/user_transactions/',
                        '{id}/open_orders/',
                        '{id}/cancel_order/',
                        '{id}/buy/',
                        '{id}/sell/',
                        '{id}/buy_market/',
                        '{id}/sell_market/',
                        '{id}/estimate_sell_market/',
                        '{id}/estimate_buy_market/',
                    ],
                },
            },
            'markets': {
                'BTC/GBP': {'id': 'XBT/GBP', 'symbol': 'BTC/GBP', 'base': 'BTC', 'quote': 'GBP'},
                'BTC/EUR': {'id': 'XBT/EUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                'BTC/USD': {'id': 'XBT/USD', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'BTC/PLN': {'id': 'XBT/PLN', 'symbol': 'BTC/PLN', 'base': 'BTC', 'quote': 'PLN'},
                'BCH/GBP': {'id': 'BCH/GBP', 'symbol': 'BCH/GBP', 'base': 'BCH', 'quote': 'GBP'},
            },
        }
        params.update(config)
        super(coinfloor, self).__init__(params)

    def fetch_balance(self, params={}):
        symbol = None
        if 'symbol' in params:
            symbol = params['symbol']
        if 'id' in params:
            symbol = params['id']
        if not symbol:
            raise ExchangeError(self.id + ' fetchBalance requires a symbol param')
        # todo parse balance
        return self.privatePostIdBalance({
            'id': self.market_id(symbol),
        })

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetIdOrderBook(self.extend({
            'id': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def parse_ticker(self, ticker, market=None):
        # rewrite to get the timestamp from HTTP headers
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': self.safe_float(ticker, 'vwap'),
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        market = self.market(symbol)
        ticker = self.publicGetIdTicker(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'info': trade,
            'id': str(trade['tid']),
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetIdTransactions(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        order = {'id': self.market_id(symbol)}
        method = 'privatePostId' + self.capitalize(side)
        if type == 'market':
            order['quantity'] = amount
            method += 'Market'
        else:
            order['price'] = price
            order['amount'] = amount
        return getattr(self, method)(self.extend(order, params))

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostIdCancelOrder({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        # curl -k -u '[User ID]/[API key]:[Passphrase]' https://webapi.coinfloor.co.uk:8090/bist/XBT/GBP/balance/
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            body = self.urlencode(self.extend({'nonce': nonce}, query))
            auth = self.uid + '/' + self.apiKey + ':' + self.password
            signature = base64.b64encode(auth)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + signature,
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class coingi (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'coingi',
            'name': 'Coingi',
            'rateLimit': 1000,
            'countries': ['PA', 'BG', 'CN', 'US'],  # Panama, Bulgaria, China, US
            'hasFetchTickers': True,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28619707-5c9232a8-7212-11e7-86d6-98fe5d15cc6e.jpg',
                'api': 'https://api.coingi.com',
                'www': 'https://coingi.com',
                'doc': 'http://docs.coingi.apiary.io/',
            },
            'api': {
                'current': {
                    'get': [
                        'order-book/{pair}/{askCount}/{bidCount}/{depth}',
                        'transactions/{pair}/{maxCount}',
                        '24hour-rolling-aggregation',
                    ],
                },
                'user': {
                    'post': [
                        'balance',
                        'add-order',
                        'cancel-order',
                        'orders',
                        'transactions',
                        'create-crypto-withdrawal',
                    ],
                },
            },
            'markets': {
                'LTC/BTC': {'id': 'ltc-btc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'PPC/BTC': {'id': 'ppc-btc', 'symbol': 'PPC/BTC', 'base': 'PPC', 'quote': 'BTC'},
                'DOGE/BTC': {'id': 'doge-btc', 'symbol': 'DOGE/BTC', 'base': 'DOGE', 'quote': 'BTC'},
                'VTC/BTC': {'id': 'vtc-btc', 'symbol': 'VTC/BTC', 'base': 'VTC', 'quote': 'BTC'},
                'FTC/BTC': {'id': 'ftc-btc', 'symbol': 'FTC/BTC', 'base': 'FTC', 'quote': 'BTC'},
                'NMC/BTC': {'id': 'nmc-btc', 'symbol': 'NMC/BTC', 'base': 'NMC', 'quote': 'BTC'},
                'DASH/BTC': {'id': 'dash-btc', 'symbol': 'DASH/BTC', 'base': 'DASH', 'quote': 'BTC'},
            },
        }
        params.update(config)
        super(coingi, self).__init__(params)

    def fetch_balance(self, params={}):
        currencies = []
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c].lower()
            currencies.append(currency)
        balances = self.userPostBalance({
            'currencies': ','.join(currencies)
        })
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']['name']
            currency = currency.upper()
            account = {
                'free': balance['available'],
                'used': balance['blocked'] + balance['inOrders'] + balance['withdrawing'],
                'total': 0.0,
            }
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderbook = self.currentGetOrderBookPairAskCountBidCountDepth(self.extend({
            'pair': market['id'],
            'askCount': 512,  # maximum returned number of asks 1-512
            'bidCount': 512,  # maximum returned number of bids 1-512
            'depth': 32,  # maximum number of depth range steps 1-32
        }, params))
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'baseAmount')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': ticker['high'],
            'low': ticker['low'],
            'bid': ticker['highestBid'],
            'ask': ticker['lowestAsk'],
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': ticker['baseVolume'],
            'quoteVolume': ticker['counterVolume'],
            'info': ticker,
        }
        return ticker

    def fetch_tickers(self, symbols=None, params={}):
        response = self.currentGet24hourRollingAggregation(params)
        result = {}
        for t in range(0, len(response)):
            ticker = response[t]
            base = ticker['currencyPair']['base'].upper()
            quote = ticker['currencyPair']['counter'].upper()
            symbol = base + '/' + quote
            market = self.markets[symbol]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        tickers = self.fetch_tickers(None, params)
        if symbol in tickers:
            return tickers[symbol]
        raise ExchangeError(self.id + ' return did not contain ' + symbol)

    def parse_trade(self, trade, market=None):
        if not market:
            market = self.markets_by_id[trade['currencyPair']]
        return {
            'id': trade['id'],
            'info': trade,
            'timestamp': trade['timestamp'],
            'datetime': self.iso8601(trade['timestamp']),
            'symbol': market['symbol'],
            'type': None,
            'side': None,  # type
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.currentGetTransactionsPairMaxCount(self.extend({
            'pair': market['id'],
            'maxCount': 128,
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        order = {
            'currencyPair': self.market_id(symbol),
            'volume': amount,
            'price': price,
            'orderType': 0 if (side == 'buy') else 1,
        }
        response = self.userPostAddOrder(self.extend(order, params))
        return {
            'info': response,
            'id': response['result'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.userPostCancelOrder({'orderId': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + api + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'current':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            request = self.extend({
                'token': self.apiKey,
                'nonce': nonce,
            }, query)
            auth = str(nonce) + '$' + self.apiKey
            request['signature'] = self.hmac(self.encode(auth), self.encode(self.secret))
            body = self.json(request)
            headers = {
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'errors' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class coinmarketcap (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'coinmarketcap',
            'name': 'CoinMarketCap',
            'rateLimit': 10000,
            'version': 'v1',
            'countries': 'US',
            'hasCORS': True,
            'hasPrivateAPI': False,
            'hasCreateOrder': False,
            'hasCancelOrder': False,
            'hasFetchBalance': False,
            'hasFetchOrderBook': False,
            'hasFetchTrades': False,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28244244-9be6312a-69ed-11e7-99c1-7c1797275265.jpg',
                'api': 'https://api.coinmarketcap.com',
                'www': 'https://coinmarketcap.com',
                'doc': 'https://coinmarketcap.com/api',
            },
            'api': {
                'public': {
                    'get': [
                        'ticker/',
                        'ticker/{id}/',
                        'global/',
                    ],
                },
            },
            'currencyCodes': [
                'AUD',
                'BRL',
                'CAD',
                'CHF',
                'CNY',
                'EUR',
                'GBP',
                'HKD',
                'IDR',
                'INR',
                'JPY',
                'KRW',
                'MXN',
                'RUB',
                'USD',
            ],
        }
        params.update(config)
        super(coinmarketcap, self).__init__(params)

    def fetch_order_book(self, symbol, params={}):
        raise ExchangeError('Fetching order books is not supported by the API of ' + self.id)

    def fetch_markets(self):
        markets = self.publicGetTicker({
            'limit' : 0,
        })
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            currencies = self.currencyCodes
            for c in range(0, len(currencies)):
                quote = currencies[c]
                quoteId = quote.lower()
                base = market['symbol']
                baseId = market['id']
                symbol = base + '/' + quote
                id = baseId + '/' + quote
                result.append({
                    'id': id,
                    'symbol': symbol,
                    'base': base,
                    'quote': quote,
                    'baseId': baseId,
                    'quoteId': quoteId,
                    'info': market,
                })
        return result

    def fetch_global(self, currency='USD'):
        self.load_markets()
        request = {}
        if currency:
            request['convert'] = currency
        return self.publicGetGlobal(request)

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        if 'last_updated' in ticker:
            if ticker['last_updated']:
                timestamp = int(ticker['last_updated']) * 1000
        change = None
        changeKey = 'percent_change_24h'
        if changeKey in ticker:
            change = float(ticker[changeKey])
        last = None
        symbol = None
        volume = None
        if market:
            price = 'price_' + market['quoteId']
            if price in ticker:
                if ticker[price]:
                    last = float(ticker[price])
            symbol = market['symbol']
            volumeKey = '24h_volume_' + market['quoteId']
            if volumeKey in ticker:
                volume = float(ticker[volumeKey])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': None,
            'ask': None,
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': last,
            'change': change,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': volume,
            'info': ticker,
        }

    def fetch_tickers(self, currency='USD', params={}):
        self.load_markets()
        request = {
            'limit' : 10000,
        }
        if currency:
            request['convert'] = currency
        response = self.publicGetTicker(self.extend(request, params))
        tickers = {}
        for t in range(0, len(response)):
            ticker = response[t]
            id = ticker['id'] + '/' + currency
            symbol = id
            market = None
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            tickers[symbol] = self.parse_ticker(ticker, market)
        return tickers

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = self.extend({
            'convert': market['quote'],
            'id': market['baseId'],
        }, params)
        response = self.publicGetTickerId(request)
        ticker = response[0]
        return self.parse_ticker(ticker, market)

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if query:
            url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        return response

# -----------------------------------------------------------------------------


class coinmate (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'coinmate',
            'name': 'CoinMate',
            'countries': ['GB', 'CZ'],  # UK, Czech Republic
            'rateLimit': 1000,
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27811229-c1efb510-606c-11e7-9a36-84ba2ce412d8.jpg',
                'api': 'https://coinmate.io/api',
                'www': 'https://coinmate.io',
                'doc': [
                    'http://docs.coinmate.apiary.io',
                    'https://coinmate.io/developers',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'orderBook',
                        'ticker',
                        'transactions',
                    ],
                },
                'private': {
                    'post': [
                        'balances',
                        'bitcoinWithdrawal',
                        'bitcoinDepositAddresses',
                        'buyInstant',
                        'buyLimit',
                        'cancelOrder',
                        'cancelOrderWithInfo',
                        'createVoucher',
                        'openOrders',
                        'redeemVoucher',
                        'sellInstant',
                        'sellLimit',
                        'transactionHistory',
                        'unconfirmedBitcoinDeposits',
                    ],
                },
            },
            'markets': {
                'BTC/EUR': {'id': 'BTC_EUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                'BTC/CZK': {'id': 'BTC_CZK', 'symbol': 'BTC/CZK', 'base': 'BTC', 'quote': 'CZK'},
            },
        }
        params.update(config)
        super(coinmate, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privatePostBalances()
        balances = response['data']
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in balances:
                account['free'] = balances[currency]['available']
                account['used'] = balances[currency]['reserved']
                account['total'] = balances[currency]['balance']
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        response = self.publicGetOrderBook(self.extend({
            'currencyPair': self.market_id(symbol),
            'groupByPriceLimit': 'False',
        }, params))
        orderbook = response['data']
        timestamp = orderbook['timestamp'] * 1000
        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetTicker(self.extend({
            'currencyPair': self.market_id(symbol),
        }, params))
        ticker = response['data']
        timestamp = ticker['timestamp'] * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['amount']),
            'quoteVolume': None,
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        if not market:
            market = self.markets_by_id[trade['currencyPair']]
        return {
            'id': trade['transactionId'],
            'info': trade,
            'timestamp': trade['timestamp'],
            'datetime': self.iso8601(trade['timestamp']),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTransactions(self.extend({
            'currencyPair': market['id'],
            'minutesIntoHistory': 10,
        }, params))
        return self.parse_trades(response['data'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        method = 'privatePost' + self.capitalize(side)
        order = {
            'currencyPair': self.market_id(symbol),
        }
        if type == 'market':
            if side == 'buy':
                order['total'] = amount  # amount in fiat
            else:
                order['amount'] = amount  # amount in fiat
            method += 'Instant'
        else:
            order['amount'] = amount  # amount in crypto
            order['price'] = price
            method += self.capitalize(type)
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['data']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder({'orderId': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            if not self.uid:
                raise AuthenticationError(self.id + ' requires `' + self.id + '.uid` property for authentication')
            nonce = str(self.nonce())
            auth = nonce + self.uid + self.apiKey
            signature = self.hmac(self.encode(auth), self.encode(self.secret))
            body = self.urlencode(self.extend({
                'clientId': self.uid,
                'nonce': nonce,
                'publicKey': self.apiKey,
                'signature': signature.upper(),
            }, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            if response['error']:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class coinsecure (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'coinsecure',
            'name': 'Coinsecure',
            'countries': 'IN',  # India
            'rateLimit': 1000,
            'version': 'v1',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766472-9cbd200a-5ed9-11e7-9551-2267ad7bac08.jpg',
                'api': 'https://api.coinsecure.in',
                'www': 'https://coinsecure.in',
                'doc': [
                    'https://api.coinsecure.in',
                    'https://github.com/coinsecure/plugins',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'bitcoin/search/confirmation/{txid}',
                        'exchange/ask/low',
                        'exchange/ask/orders',
                        'exchange/bid/high',
                        'exchange/bid/orders',
                        'exchange/lastTrade',
                        'exchange/max24Hr',
                        'exchange/min24Hr',
                        'exchange/ticker',
                        'exchange/trades',
                    ],
                },
                'private': {
                    'get': [
                        'mfa/authy/call',
                        'mfa/authy/sms',
                        'netki/search/{netkiName}',
                        'user/bank/otp/{number}',
                        'user/kyc/otp/{number}',
                        'user/profile/phone/otp/{number}',
                        'user/wallet/coin/address/{id}',
                        'user/wallet/coin/deposit/confirmed/all',
                        'user/wallet/coin/deposit/confirmed/{id}',
                        'user/wallet/coin/deposit/unconfirmed/all',
                        'user/wallet/coin/deposit/unconfirmed/{id}',
                        'user/wallet/coin/wallets',
                        'user/exchange/bank/fiat/accounts',
                        'user/exchange/bank/fiat/balance/available',
                        'user/exchange/bank/fiat/balance/pending',
                        'user/exchange/bank/fiat/balance/total',
                        'user/exchange/bank/fiat/deposit/cancelled',
                        'user/exchange/bank/fiat/deposit/unverified',
                        'user/exchange/bank/fiat/deposit/verified',
                        'user/exchange/bank/fiat/withdraw/cancelled',
                        'user/exchange/bank/fiat/withdraw/completed',
                        'user/exchange/bank/fiat/withdraw/unverified',
                        'user/exchange/bank/fiat/withdraw/verified',
                        'user/exchange/ask/cancelled',
                        'user/exchange/ask/completed',
                        'user/exchange/ask/pending',
                        'user/exchange/bid/cancelled',
                        'user/exchange/bid/completed',
                        'user/exchange/bid/pending',
                        'user/exchange/bank/coin/addresses',
                        'user/exchange/bank/coin/balance/available',
                        'user/exchange/bank/coin/balance/pending',
                        'user/exchange/bank/coin/balance/total',
                        'user/exchange/bank/coin/deposit/cancelled',
                        'user/exchange/bank/coin/deposit/unverified',
                        'user/exchange/bank/coin/deposit/verified',
                        'user/exchange/bank/coin/withdraw/cancelled',
                        'user/exchange/bank/coin/withdraw/completed',
                        'user/exchange/bank/coin/withdraw/unverified',
                        'user/exchange/bank/coin/withdraw/verified',
                        'user/exchange/bank/summary',
                        'user/exchange/coin/fee',
                        'user/exchange/fiat/fee',
                        'user/exchange/kycs',
                        'user/exchange/referral/coin/paid',
                        'user/exchange/referral/coin/successful',
                        'user/exchange/referral/fiat/paid',
                        'user/exchange/referrals',
                        'user/exchange/trade/summary',
                        'user/login/token/{token}',
                        'user/summary',
                        'user/wallet/summary',
                        'wallet/coin/withdraw/cancelled',
                        'wallet/coin/withdraw/completed',
                        'wallet/coin/withdraw/unverified',
                        'wallet/coin/withdraw/verified',
                    ],
                    'post': [
                        'login',
                        'login/initiate',
                        'login/password/forgot',
                        'mfa/authy/initiate',
                        'mfa/ga/initiate',
                        'signup',
                        'user/netki/update',
                        'user/profile/image/update',
                        'user/exchange/bank/coin/withdraw/initiate',
                        'user/exchange/bank/coin/withdraw/newVerifycode',
                        'user/exchange/bank/fiat/withdraw/initiate',
                        'user/exchange/bank/fiat/withdraw/newVerifycode',
                        'user/password/change',
                        'user/password/reset',
                        'user/wallet/coin/withdraw/initiate',
                        'wallet/coin/withdraw/newVerifycode',
                    ],
                    'put': [
                        'signup/verify/{token}',
                        'user/exchange/kyc',
                        'user/exchange/bank/fiat/deposit/new',
                        'user/exchange/ask/new',
                        'user/exchange/bid/new',
                        'user/exchange/instant/buy',
                        'user/exchange/instant/sell',
                        'user/exchange/bank/coin/withdraw/verify',
                        'user/exchange/bank/fiat/account/new',
                        'user/exchange/bank/fiat/withdraw/verify',
                        'user/mfa/authy/initiate/enable',
                        'user/mfa/ga/initiate/enable',
                        'user/netki/create',
                        'user/profile/phone/new',
                        'user/wallet/coin/address/new',
                        'user/wallet/coin/new',
                        'user/wallet/coin/withdraw/sendToExchange',
                        'user/wallet/coin/withdraw/verify',
                    ],
                    'delete': [
                        'user/gcm/{code}',
                        'user/logout',
                        'user/exchange/bank/coin/withdraw/unverified/cancel/{withdrawID}',
                        'user/exchange/bank/fiat/deposit/cancel/{depositID}',
                        'user/exchange/ask/cancel/{orderID}',
                        'user/exchange/bid/cancel/{orderID}',
                        'user/exchange/bank/fiat/withdraw/unverified/cancel/{withdrawID}',
                        'user/mfa/authy/disable/{code}',
                        'user/mfa/ga/disable/{code}',
                        'user/profile/phone/delete',
                        'user/profile/image/delete/{netkiName}',
                        'user/wallet/coin/withdraw/unverified/cancel/{withdrawID}',
                    ],
                },
            },
            'markets': {
                'BTC/INR': {'id': 'BTC/INR', 'symbol': 'BTC/INR', 'base': 'BTC', 'quote': 'INR'},
            },
        }
        params.update(config)
        super(coinsecure, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privateGetUserExchangeBankSummary()
        balance = response['message']
        coin = {
            'free': balance['availableCoinBalance'],
            'used': balance['pendingCoinBalance'],
            'total': balance['totalCoinBalance'],
        }
        fiat = {
            'free': balance['availableFiatBalance'],
            'used': balance['pendingFiatBalance'],
            'total': balance['totalFiatBalance'],
        }
        result = {
            'info': balance,
            'BTC': coin,
            'INR': fiat,
        }
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        bids = self.publicGetExchangeBidOrders(params)
        asks = self.publicGetExchangeAskOrders(params)
        orderbook = {
            'bids': bids['message'],
            'asks': asks['message'],
        }
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'rate', 'vol')

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetExchangeTicker(params)
        ticker = response['message']
        timestamp = ticker['timestamp']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['lastPrice']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['coinvolume']),
            'quoteVolume': float(ticker['fiatvolume']),
            'info': ticker,
        }

    def fetch_trades(self, market, params={}):
        return self.publicGetExchangeTrades(params)

    def create_order(self, market, type, side, amount, price=None, params={}):
        method = 'privatePutUserExchange'
        order = {}
        if type == 'market':
            method += 'Instant' + self.capitalize(side)
            if side == 'buy':
                order['maxFiat'] = amount
            else:
                order['maxVol'] = amount
        else:
            direction = 'Bid' if (side == 'buy') else 'Ask'
            method += direction + 'New'
            order['rate'] = price
            order['vol'] = amount
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['message']['orderID'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        raise ExchangeError(self.id + ' cancelOrder() is not fully implemented yet')
        method = 'privateDeleteUserExchangeAskCancelOrderId'  # TODO fixme, have to specify order side here
        return getattr(self, method)({'orderID': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            headers = {'Authorization': self.apiKey}
            if query:
                body = self.json(query)
                headers['Content-Type'] = 'application/json'
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'success' in response:
            if response['success']:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class coinspot (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'coinspot',
            'name': 'CoinSpot',
            'countries': 'AU',  # Australia
            'rateLimit': 1000,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28208429-3cacdf9a-6896-11e7-854e-4c79a772a30f.jpg',
                'api': {
                    'public': 'https://www.coinspot.com.au/pubapi',
                    'private': 'https://www.coinspot.com.au/api',
                },
                'www': 'https://www.coinspot.com.au',
                'doc': 'https://www.coinspot.com.au/api',
            },
            'api': {
                'public': {
                    'get': [
                        'latest',
                    ],
                },
                'private': {
                    'post': [
                        'orders',
                        'orders/history',
                        'my/coin/deposit',
                        'my/coin/send',
                        'quote/buy',
                        'quote/sell',
                        'my/balances',
                        'my/orders',
                        'my/buy',
                        'my/sell',
                        'my/buy/cancel',
                        'my/sell/cancel',
                    ],
                },
            },
            'markets': {
                'BTC/AUD': {'id': 'BTC', 'symbol': 'BTC/AUD', 'base': 'BTC', 'quote': 'AUD'},
                'LTC/AUD': {'id': 'LTC', 'symbol': 'LTC/AUD', 'base': 'LTC', 'quote': 'AUD'},
                'DOGE/AUD': {'id': 'DOGE', 'symbol': 'DOGE/AUD', 'base': 'DOGE', 'quote': 'AUD'},
            },
        }
        params.update(config)
        super(coinspot, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privatePostMyBalances()
        result = {'info': response}
        if 'balance' in response:
            balances = response['balance']
            currencies = list(balances.keys())
            for c in range(0, len(currencies)):
                currency = currencies[c]
                uppercase = currency.upper()
                account = {
                    'free': balances[currency],
                    'used': 0.0,
                    'total': balances[currency],
                }
                if uppercase == 'DRK':
                    uppercase = 'DASH'
                result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderbook = self.privatePostOrders(self.extend({
            'cointype': market['id'],
        }, params))
        result = self.parse_order_book(orderbook, None, 'buyorders', 'sellorders', 'rate', 'amount')
        result['bids'] = self.sort_by(result['bids'], 0, True)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetLatest(params)
        id = self.market_id(symbol)
        id = id.lower()
        ticker = response['prices'][id]
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_trades(self, market, params={}):
        return self.privatePostOrdersHistory(self.extend({
            'cointype': self.market_id(market),
        }, params))

    def create_order(self, market, type, side, amount, price=None, params={}):
        method = 'privatePostMy' + self.capitalize(side)
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        order = {
            'cointype': self.market_id(market),
            'amount': amount,
            'rate': price,
        }
        return getattr(self, method)(self.extend(order, params))

    def cancel_order(self, id, symbol=None, params={}):
        raise ExchangeError(self.id + ' cancelOrder() is not fully implemented yet')
        method = 'privatePostMyBuy'
        return getattr(self, method)({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        if not self.apiKey:
            raise AuthenticationError(self.id + ' requires apiKey for all requests')
        url = self.urls['api'][api] + '/' + path
        if api == 'private':
            nonce = self.nonce()
            body = self.json(self.extend({'nonce': nonce}, params))
            headers = {
                'Content-Type': 'application/json',
                'key': self.apiKey,
                'sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class cryptopia (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'cryptopia',
            'name': 'Cryptopia',
            'rateLimit': 1500,
            'countries': 'NZ',  # New Zealand
            'hasFetchTickers': True,
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'hasFetchMyTrades': True,
            'hasCORS': False,
            'hasDeposit': True,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/29484394-7b4ea6e2-84c6-11e7-83e5-1fccf4b2dc81.jpg',
                'api': 'https://www.cryptopia.co.nz/api',
                'www': 'https://www.cryptopia.co.nz',
                'doc': [
                    'https://www.cryptopia.co.nz/Forum/Thread/255',
                    'https://www.cryptopia.co.nz/Forum/Thread/256',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'GetCurrencies',
                        'GetTradePairs',
                        'GetMarkets',
                        'GetMarkets/{id}',
                        'GetMarkets/{hours}',
                        'GetMarkets/{id}/{hours}',
                        'GetMarket/{id}',
                        'GetMarket/{id}/{hours}',
                        'GetMarketHistory/{id}',
                        'GetMarketHistory/{id}/{hours}',
                        'GetMarketOrders/{id}',
                        'GetMarketOrders/{id}/{count}',
                        'GetMarketOrderGroups/{ids}/{count}',
                    ],
                },
                'private': {
                    'post': [
                        'CancelTrade',
                        'GetBalance',
                        'GetDepositAddress',
                        'GetOpenOrders',
                        'GetTradeHistory',
                        'GetTransactions',
                        'SubmitTip',
                        'SubmitTrade',
                        'SubmitTransfer',
                        'SubmitWithdraw',
                    ],
                },
            },
        }
        params.update(config)
        super(cryptopia, self).__init__(params)

    def common_currency_code(self, currency):
        if currency == 'CC':
            return 'CCX'
        if currency == 'FCN':
            return 'Facilecoin'
        if currency == 'NET':
            return 'NetCoin'
        if currency == 'BTG':
            return 'Bitgem'
        return currency

    def fetch_markets(self):
        response = self.publicGetTradePairs()
        result = []
        markets = response['Data']
        for i in range(0, len(markets)):
            market = markets[i]
            id = market['Id']
            symbol = market['Label']
            base, quote = symbol.split('/')
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            precision = {
                'amount': 8,
                'price': 8,
            }
            amountLimits = {
                'min': market['MinimumTrade'],
                'max': market['MaximumTrade']
            }
            priceLimits = {
                'min': market['MinimumPrice'],
                'max': market['MaximumPrice'],
            }
            limits = {
                'amount': amountLimits,
                'price': priceLimits,
            }
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
                'maker': market['TradeFee'] / 100,
                'taker': market['TradeFee'] / 100,
                'lot': amountLimits['min'],
                'precision': precision,
                'limits': limits,
            })
        return result

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetMarketOrdersId(self.extend({
            'id': self.market_id(symbol),
        }, params))
        orderbook = response['Data']
        return self.parse_order_book(orderbook, None, 'Buy', 'Sell', 'Price', 'Volume')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'info': ticker,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['High']),
            'low': float(ticker['Low']),
            'bid': float(ticker['BidPrice']),
            'ask': float(ticker['AskPrice']),
            'vwap': None,
            'open': float(ticker['Open']),
            'close': float(ticker['Close']),
            'first': None,
            'last': float(ticker['LastPrice']),
            'change': float(ticker['Change']),
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['Volume']),
            'quoteVolume': float(ticker['BaseVolume']),
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketId(self.extend({
            'id': market['id'],
        }, params))
        ticker = response['Data']
        return self.parse_ticker(ticker, market)

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetMarkets(params)
        result = {}
        tickers = response['Data']
        for i in range(0, len(tickers)):
            ticker = tickers[i]
            id = ticker['TradePairId']
            market = self.markets_by_id[id]
            symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def parse_trade(self, trade, market=None):
        timestamp = None
        if 'Timestamp' in trade:
            timestamp = trade['Timestamp'] * 1000
        elif 'TimeStamp' in trade:
            timestamp = self.parse8601(trade['TimeStamp'])
        price = self.safe_float(trade, 'Price')
        if not price:
            price = self.safe_float(trade, 'Rate')
        cost = self.safe_float(trade, 'Total')
        id = self.safe_string(trade, 'TradeId')
        if not market:
            if 'TradePairId' in trade:
                if trade['TradePairId'] in self.markets_by_id:
                    market = self.markets_by_id[trade['TradePairId']]
        symbol = None
        fee = None
        if market:
            symbol = market['symbol']
            if 'Fee' in trade:
                fee = {
                    'currency': market['quote'],
                    'cost': trade['Fee'],
                }
        return {
            'id': id,
            'info': trade,
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': 'limit',
            'side': trade['Type'].lower(),
            'price': price,
            'cost': cost,
            'amount': trade['Amount'],
            'fee': fee,
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketHistoryIdHours(self.extend({
            'id': market['id'],
            'hours': 24,  # default
        }, params))
        trades = response['Data']
        return self.parse_trades(trades, market)

    def fetch_my_trades(self, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchMyTrades requires a symbol')
        self.load_markets()
        market = self.market(symbol)
        response = self.privatePostGetTradeHistory(self.extend({
            # 'Market': market['id'],
            'TradePairId': market['id'],  # Cryptopia identifier(not required if 'Market' supplied)
            # 'Count': 10,  # max = 100
        }, params))
        return self.parse_trades(response['Data'], market)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetBalance()
        balances = response['Data']
        result = {'info': response}
        for i in range(0, len(balances)):
            balance = balances[i]
            code = balance['Symbol']
            currency = self.common_currency_code(code)
            account = {
                'free': balance['Available'],
                'used': 0.0,
                'total': balance['Total'],
            }
            account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        price = float(price)
        amount = float(amount)
        request = {
            'TradePairId': market['id'],
            'Type': self.capitalize(side),
            'Rate': self.price_to_precision(symbol, price),
            'Amount': self.amount_to_precision(symbol, amount),
        }
        response = self.privatePostSubmitTrade(self.extend(request, params))
        if not response:
            raise ExchangeError(self.id + ' createOrder returned unknown error: ' + self.json(response))
        if 'Data' in response:
            if 'OrderId' in response['Data']:
                if not response['Data']['OrderId']:
                    raise ExchangeError(self.id + ' createOrder returned bad OrderId: ' + self.json(response))
            else:
                raise ExchangeError(self.id + ' createOrder returned no OrderId in Data: ' + self.json(response))
        else:
            raise ExchangeError(self.id + ' createOrder returned no Data in response: ' + self.json(response))
        id = str(response['Data']['OrderId'])
        timestamp = self.milliseconds()
        order = {
            'id': id,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': 'open',
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'cost': price * amount,
            'amount': amount,
            'remaining': amount,
            'filled': 0.0,
            'fee': None,
            # 'trades': self.parse_trades(order['trades'], market),
        }
        self.orders[id] = order
        return self.extend({'info': response}, order)

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = None
        try:
            response = self.privatePostCancelTrade(self.extend({
                'Type': 'Trade',
                'OrderId': id,
            }, params))
            if id in self.orders:
                self.orders[id]['status'] = 'canceled'
        except Exception as e:
            if self.last_json_response:
                message = self.safe_string(self.last_json_response, 'Error')
                if message:
                    if message.find('does not exist') >= 0:
                        raise OrderNotFound(self.id + ' cancelOrder() error: ' + self.last_http_response)
            raise e
        return response

    def parse_order(self, order, market=None):
        symbol = None
        if market:
            symbol = market['symbol']
        elif 'Market' in order:
            id = order['Market']
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
        timestamp = self.parse8601(order['TimeStamp'])
        amount = self.safe_float(order, 'Amount')
        remaining = self.safe_float(order, 'Remaining')
        filled = amount - remaining
        return {
            'id': str(order['OrderId']),
            'info': self.omit(order, 'status'),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': order['status'],
            'symbol': symbol,
            'type': 'limit',
            'side': order['Type'].lower(),
            'price': self.safe_float(order, 'Rate'),
            'cost': self.safe_float(order, 'Total'),
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'fee': None,
            # 'trades': self.parse_trades(order['trades'], market),
        }

    def fetch_orders(self, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOrders requires a symbol param')
        self.load_markets()
        market = self.market(symbol)
        response = self.privatePostGetOpenOrders({
            # 'Market': market['id'],
            'TradePairId': market['id'],  # Cryptopia identifier(not required if 'Market' supplied)
            # 'Count': 100,  # default = 100
        }, params)
        orders = []
        for i in range(0, len(response['Data'])):
            orders.append(self.extend(response['Data'][i], {'status': 'open'}))
        openOrders = self.parse_orders(orders, market)
        for j in range(0, len(openOrders)):
            self.orders[openOrders[j]['id']] = openOrders[j]
        openOrdersIndexedById = self.index_by(openOrders, 'id')
        cachedOrderIds = list(self.orders.keys())
        result = []
        for k in range(0, len(cachedOrderIds)):
            id = cachedOrderIds[k]
            if id in openOrdersIndexedById:
                self.orders[id] = self.extend(self.orders[id], openOrdersIndexedById[id])
            else:
                order = self.orders[id]
                if order['status'] == 'open':
                    self.orders[id] = self.extend(order, {
                        'status': 'closed',
                        'cost': order['amount'] * order['price'],
                        'filled': order['amount'],
                        'remaining': 0.0,
                    })
            order = self.orders[id]
            if order['symbol'] == symbol:
                result.append(order)
        return result

    def fetch_order(self, id, symbol=None, params={}):
        id = str(id)
        orders = self.fetch_orders(symbol, params)
        for i in range(0, len(orders)):
            if orders[i]['id'] == id:
                return orders[i]
        raise OrderNotCached(self.id + ' order ' + id + ' not found in cached .orders, fetchOrder requires .orders(de)serialization implemented for self method to work properly')

    def fetch_open_orders(self, symbol=None, params={}):
        orders = self.fetch_orders(symbol, params)
        result = []
        for i in range(0, len(orders)):
            if orders[i]['status'] == 'open':
                result.append(orders[i])
        return result

    def fetchClosedOrders(self, symbol=None, params={}):
        orders = self.fetch_orders(symbol, params)
        result = []
        for i in range(0, len(orders)):
            if orders[i]['status'] == 'closed':
                result.append(orders[i])
        return result

    def deposit(self, currency, params={}):
        self.load_markets()
        response = self.privatePostGetDepositAddress(self.extend({
            'Currency': currency
        }, params))
        address = self.safe_string(response['Data'], 'BaseAddress')
        if not address:
            address = self.safe_string(response['Data'], 'Address')
        return {
            'info': response,
            'address': address,
        }

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        response = self.privatePostSubmitWithdraw(self.extend({
            'Currency': currency,
            'Amount': amount,
            'Address': address,  # Address must exist in you AddressBook in security settings
        }, params))
        return {
            'info': response,
            'id': response['Data'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = str(self.nonce())
            body = self.json(query)
            hash = self.hash(self.encode(body), 'md5', 'base64')
            secret = base64.b64decode(self.secret)
            uri = self.encode_uri_component(url)
            lowercase = uri.lower()
            payload = self.apiKey + method + lowercase + nonce + self.binary_to_string(hash)
            signature = self.hmac(self.encode(payload), secret, hashlib.sha256, 'base64')
            auth = 'amx ' + self.apiKey + ':' + self.binary_to_string(signature) + ':' + nonce
            headers = {
                'Content-Type': 'application/json',
                'Authorization': auth,
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if response:
            if 'Success' in response:
                if response['Success']:
                    return response
                elif 'Error' in response:
                    if response['Error'] == 'Insufficient Funds.':
                        raise InsufficientFunds(self.id + ' ' + self.json(response))
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class dsx (btce):

    def __init__(self, config={}):
        params = {
            'id': 'dsx',
            'name': 'DSX',
            'countries': 'UK',
            'rateLimit': 1500,
            'hasCORS': False,
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'hasFetchTickers': True,
            'hasFetchMyTrades': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27990275-1413158a-645a-11e7-931c-94717f7510e3.jpg',
                'api': {
                    'public': 'https://dsx.uk/mapi',  # market data
                    'private': 'https://dsx.uk/tapi',  # trading
                    'dwapi': 'https://dsx.uk/dwapi',  # deposit/withdraw
                },
                'www': 'https://dsx.uk',
                'doc': [
                    'https://api.dsx.uk',
                    'https://dsx.uk/api_docs/public',
                    'https://dsx.uk/api_docs/private',
                    '',
                ],
            },
            'api': {
                # market data (public)
                'public': {
                    'get': [
                        'barsFromMoment/{id}/{period}/{start}',  # empty reply :\
                        'depth/{pair}',
                        'info',
                        'lastBars/{id}/{period}/{amount}',  # period is (m, h or d)
                        'periodBars/{id}/{period}/{start}/{end}',
                        'ticker/{pair}',
                        'trades/{pair}',
                    ],
                },
                # trading (private)
                'private': {
                    'post': [
                        'getInfo',
                        'TransHistory',
                        'TradeHistory',
                        'OrderHistory',
                        'ActiveOrders',
                        'Trade',
                        'CancelOrder',
                    ],
                },
                # deposit / withdraw (private)
                'dwapi': {
                    'post': [
                        'getCryptoDepositAddress',
                        'cryptoWithdraw',
                        'fiatWithdraw',
                        'getTransactionStatus',
                        'getTransactions',
                    ],
                },
            },
        }
        params.update(config)
        super(dsx, self).__init__(params)

    def getBaseQuoteFromMarketId(self, id):
        uppercase = id.upper()
        base = uppercase[0:3]
        quote = uppercase[3:6]
        base = self.common_currency_code(base)
        quote = self.common_currency_code(quote)
        return [base, quote]

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetInfo()
        balances = response['return']
        result = {'info': balances}
        funds = balances['funds']
        currencies = list(funds.keys())
        for c in range(0, len(currencies)):
            currency = currencies[c]
            uppercase = currency.upper()
            uppercase = self.common_currency_code(uppercase)
            account = {
                'free': funds[currency],
                'used': 0.0,
                'total': balances['total'][currency],
            }
            account['used'] = account['total'] - account['free']
            result[uppercase] = account
        return self.parse_balance(result)

    def getOrderIdKey(self):
        return 'orderId'

    def signBodyWithSecret(self, body):
        return self.decode(self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512, 'base64'))

    def getVersionString(self):
        return ''  # they don't prepend version number to public URLs as other BTC-e clones do

# -----------------------------------------------------------------------------


class exmo (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'exmo',
            'name': 'EXMO',
            'countries': ['ES', 'RU'],  # Spain, Russia
            'rateLimit': 1000,  # once every 350 ms ≈ 180 requests per minute ≈ 3 requests per second
            'version': 'v1',
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766491-1b0ea956-5eda-11e7-9225-40d67b481b8d.jpg',
                'api': 'https://api.exmo.com',
                'www': 'https://exmo.me',
                'doc': [
                    'https://exmo.me/ru/api_doc',
                    'https://github.com/exmo-dev/exmo_api_lib/tree/master/nodejs',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'currency',
                        'order_book',
                        'pair_settings',
                        'ticker',
                        'trades',
                    ],
                },
                'private': {
                    'post': [
                        'user_info',
                        'order_create',
                        'order_cancel',
                        'user_open_orders',
                        'user_trades',
                        'user_cancelled_orders',
                        'order_trades',
                        'required_amount',
                        'deposit_address',
                        'withdraw_crypt',
                        'withdraw_get_txid',
                        'excode_create',
                        'excode_load',
                        'wallet_history',
                    ],
                },
            },
        }
        params.update(config)
        super(exmo, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetPairSettings()
        keys = list(markets.keys())
        result = []
        for p in range(0, len(keys)):
            id = keys[p]
            market = markets[id]
            symbol = id.replace('_', '/')
            base, quote = symbol.split('/')
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostUserInfo()
        result = {'info': response}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in response['balances']:
                account['free'] = float(response['balances'][currency])
            if currency in response['reserved']:
                account['used'] = float(response['reserved'][currency])
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetOrderBook(self.extend({
            'pair': market['id'],
        }, params))
        orderbook = response[market['id']]
        return self.parse_order_book(orderbook, None, 'bid', 'ask')

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['updated'] * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy_price']),
            'ask': float(ticker['sell_price']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last_trade']),
            'change': None,
            'percentage': None,
            'average': float(ticker['avg']),
            'baseVolume': float(ticker['vol']),
            'quoteVolume': float(ticker['vol_curr']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetTicker(params)
        result = {}
        ids = list(response.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = response[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetTicker(params)
        market = self.market(symbol)
        return self.parse_ticker(response[market['id']], market)

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'id': str(trade['trade_id']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': None,
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response[market['id']], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        prefix = ''
        if type == 'market':
            prefix = 'market_'
        order = {
            'pair': self.market_id(symbol),
            'quantity': amount,
            'price': price or 0,
            'type': prefix + side,
        }
        response = self.privatePostOrderCreate(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['order_id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostOrderCancel({'order_id': id})

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        result = self.privatePostWithdrawCrypt(self.extend({
            'amount': amount,
            'currency': currency,
            'address': address,
        }, params))
        return {
            'info': result,
            'id': result['task_id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            nonce = self.nonce()
            body = self.urlencode(self.extend({'nonce': nonce}, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'result' in response:
            if response['result']:
                return response
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class flowbtc (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'flowbtc',
            'name': 'flowBTC',
            'countries': 'BR',  # Brazil
            'version': 'v1',
            'rateLimit': 1000,
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28162465-cd815d4c-67cf-11e7-8e57-438bea0523a2.jpg',
                'api': 'https://api.flowbtc.com:8400/ajax',
                'www': 'https://trader.flowbtc.com',
                'doc': 'http://www.flowbtc.com.br/api/',
            },
            'api': {
                'public': {
                    'post': [
                        'GetTicker',
                        'GetTrades',
                        'GetTradesByDate',
                        'GetOrderBook',
                        'GetProductPairs',
                        'GetProducts',
                    ],
                },
                'private': {
                    'post': [
                        'CreateAccount',
                        'GetUserInfo',
                        'SetUserInfo',
                        'GetAccountInfo',
                        'GetAccountTrades',
                        'GetDepositAddresses',
                        'Withdraw',
                        'CreateOrder',
                        'ModifyOrder',
                        'CancelOrder',
                        'CancelAllOrders',
                        'GetAccountOpenOrders',
                        'GetOrderFee',
                    ],
                },
            },
        }
        params.update(config)
        super(flowbtc, self).__init__(params)

    def fetch_markets(self):
        response = self.publicPostGetProductPairs()
        markets = response['productPairs']
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['name']
            base = market['product1Label']
            quote = market['product2Label']
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetAccountInfo()
        balances = response['currencies']
        result = {'info': response}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['name']
            account = {
                'free': balance['balance'],
                'used': balance['hold'],
                'total': 0.0,
            }
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        orderbook = self.publicPostGetOrderBook(self.extend({
            'productPair': market['id'],
        }, params))
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'px', 'qty')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicPostGetTicker(self.extend({
            'productPair': market['id'],
        }, params))
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['volume24hr']),
            'quoteVolume': float(ticker['volume24hrProduct2']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['unixtime'] * 1000
        side = 'buy' if (trade['incomingOrderSide'] == 0) else 'sell'
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': str(trade['tid']),
            'order': None,
            'type': None,
            'side': side,
            'price': trade['px'],
            'amount': trade['qty'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicPostGetTrades(self.extend({
            'ins': market['id'],
            'startIndex': -1,
        }, params))
        return self.parse_trades(response['trades'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        orderType = 1 if (type == 'market') else 0
        order = {
            'ins': self.market_id(symbol),
            'side': side,
            'orderType': orderType,
            'qty': amount,
            'px': price,
        }
        response = self.privatePostCreateOrder(self.extend(order, params))
        return {
            'info': response,
            'id': response['serverOrderId'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        if 'ins' in params:
            return self.privatePostCancelOrder(self.extend({
                'serverOrderId': id,
            }, params))
        raise ExchangeError(self.id + ' requires `ins` symbol parameter for cancelling an order')

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if params:
                body = self.json(params)
        else:
            if not self.uid:
                raise AuthenticationError(self.id + ' requires `' + self.id + '.uid` property for authentication')
            nonce = self.nonce()
            auth = str(nonce) + self.uid + self.apiKey
            signature = self.hmac(self.encode(auth), self.encode(self.secret))
            body = self.json(self.extend({
                'apiKey': self.apiKey,
                'apiNonce': nonce,
                'apiSig': signature.upper(),
            }, params))
            headers = {
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'isAccepted' in response:
            if response['isAccepted']:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class foxbit (blinktrade):

    def __init__(self, config={}):
        params = {
            'id': 'foxbit',
            'name': 'FoxBit',
            'countries': 'BR',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27991413-11b40d42-647f-11e7-91ee-78ced874dd09.jpg',
                'api': {
                    'public': 'https://api.blinktrade.com/api',
                    'private': 'https://api.blinktrade.com/tapi',
                },
                'www': 'https://foxbit.exchange',
                'doc': 'https://blinktrade.com/docs',
            },
            'comment': 'Blinktrade API',
            'markets': {
                'BTC/BRL': {'id': 'BTCBRL', 'symbol': 'BTC/BRL', 'base': 'BTC', 'quote': 'BRL', 'brokerId': 4, 'broker': 'FoxBit'},
            },
        }
        params.update(config)
        super(foxbit, self).__init__(params)

# -----------------------------------------------------------------------------


class fyb (Exchange):

    def __init__(self, config={}):
        params = {
            'rateLimit': 1500,
            'api': {
                'public': {
                    'get': [
                        'ticker',
                        'tickerdetailed',
                        'orderbook',
                        'trades',
                    ],
                },
                'private': {
                    'post': [
                        'test',
                        'getaccinfo',
                        'getpendingorders',
                        'getorderhistory',
                        'cancelpendingorder',
                        'placeorder',
                        'withdraw',
                    ],
                },
            },
        }
        params.update(config)
        super(fyb, self).__init__(params)

    def fetch_balance(self, params={}):
        balance = self.privatePostGetaccinfo()
        btc = float(balance['btcBal'])
        symbol = self.symbols[0]
        quote = self.markets[symbol]['quote']
        lowercase = quote.lower() + 'Bal'
        fiat = float(balance[lowercase])
        crypto = {
            'free': btc,
            'used': 0.0,
            'total': btc,
        }
        result = {'BTC': crypto}
        result[quote] = {
            'free': fiat,
            'used': 0.0,
            'total': fiat,
        }
        result['info'] = balance
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetOrderbook(params)
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetTickerdetailed(params)
        timestamp = self.milliseconds()
        last = None
        volume = None
        if 'last' in ticker:
            last = float(ticker['last'])
        if 'vol' in ticker:
            volume = float(ticker['vol'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': last,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': volume,
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = int(trade['date']) * 1000
        return {
            'info': trade,
            'id': str(trade['tid']),
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTrades(params)
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        response = self.privatePostPlaceorder(self.extend({
            'qty': amount,
            'price': price,
            'type': side[0].upper()
        }, params))
        return {
            'info': response,
            'id': response['pending_oid'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelpendingorder({'orderNo': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + path
        if api == 'public':
            url += '.json'
        else:
            nonce = self.nonce()
            body = self.urlencode(self.extend({'timestamp': nonce}, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'key': self.apiKey,
                'sig': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha1)
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if api == 'private':
            if 'error' in response:
                if response['error']:
                    raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class fybse (fyb):

    def __init__(self, config={}):
        params = {
            'id': 'fybse',
            'name': 'FYB-SE',
            'countries': 'SE',  # Sweden
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766512-31019772-5edb-11e7-8241-2e675e6797f1.jpg',
                'api': 'https://www.fybse.se/api/SEK',
                'www': 'https://www.fybse.se',
                'doc': 'http://docs.fyb.apiary.io',
            },
            'markets': {
                'BTC/SEK': {'id': 'SEK', 'symbol': 'BTC/SEK', 'base': 'BTC', 'quote': 'SEK'},
            },
        }
        params.update(config)
        super(fybse, self).__init__(params)

# -----------------------------------------------------------------------------


class fybsg (fyb):

    def __init__(self, config={}):
        params = {
            'id': 'fybsg',
            'name': 'FYB-SG',
            'countries': 'SG',  # Singapore
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766513-3364d56a-5edb-11e7-9e6b-d5898bb89c81.jpg',
                'api': 'https://www.fybsg.com/api/SGD',
                'www': 'https://www.fybsg.com',
                'doc': 'http://docs.fyb.apiary.io',
            },
            'markets': {
                'BTC/SGD': {'id': 'SGD', 'symbol': 'BTC/SGD', 'base': 'BTC', 'quote': 'SGD'},
            },
        }
        params.update(config)
        super(fybsg, self).__init__(params)

# -----------------------------------------------------------------------------


class gatecoin (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'gatecoin',
            'name': 'Gatecoin',
            'rateLimit': 2000,
            'countries': 'HK',  # Hong Kong
            'comment': 'a regulated/licensed exchange',
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasFetchOHLCV': True,
            'timeframes': {
                '1m': '1m',
                '15m': '15m',
                '1h': '1h',
                '6h': '6h',
                '1d': '24h',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28646817-508457f2-726c-11e7-9eeb-3528d2413a58.jpg',
                'api': 'https://api.gatecoin.com',
                'www': 'https://gatecoin.com',
                'doc': [
                    'https://gatecoin.com/api',
                    'https://github.com/Gatecoin/RESTful-API-Implementation',
                    'https://api.gatecoin.com/swagger-ui/index.html',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'Public/ExchangeRate',  # Get the exchange rates
                        'Public/LiveTicker',  # Get live ticker for all currency
                        'Public/LiveTicker/{CurrencyPair}',  # Get live ticker by currency
                        'Public/LiveTickers',  # Get live ticker for all currency
                        'Public/MarketDepth/{CurrencyPair}',  # Gets prices and market depth for the currency pair.
                        'Public/NetworkStatistics/{DigiCurrency}',  # Get the network status of a specific digital currency
                        'Public/StatisticHistory/{DigiCurrency}/{Typeofdata}',  # Get the historical data of a specific digital currency
                        'Public/TickerHistory/{CurrencyPair}/{Timeframe}',  # Get ticker history
                        'Public/Transactions/{CurrencyPair}',  # Gets recent transactions
                        'Public/TransactionsHistory/{CurrencyPair}',  # Gets all transactions
                        'Reference/BusinessNatureList',  # Get the business nature list.
                        'Reference/Countries',  # Get the country list.
                        'Reference/Currencies',  # Get the currency list.
                        'Reference/CurrencyPairs',  # Get the currency pair list.
                        'Reference/CurrentStatusList',  # Get the current status list.
                        'Reference/IdentydocumentTypes',  # Get the different types of identity documents possible.
                        'Reference/IncomeRangeList',  # Get the income range list.
                        'Reference/IncomeSourceList',  # Get the income source list.
                        'Reference/VerificationLevelList',  # Get the verif level list.
                        'Stream/PublicChannel',  # Get the public pubnub channel list
                    ],
                    'post': [
                        'Export/Transactions',  # Request a export of all trades from based on currencypair, start date and end date
                        'Ping',  # Post a string, then get it back.
                        'Public/Unsubscribe/{EmailCode}',  # Lets the user unsubscribe from emails
                        'RegisterUser',  # Initial trader registration.
                    ],
                },
                'private': {
                    'get': [
                        'Account/CorporateData',  # Get corporate account data
                        'Account/DocumentAddress',  # Check if residence proof uploaded
                        'Account/DocumentCorporation',  # Check if registered document uploaded
                        'Account/DocumentID',  # Check if ID document copy uploaded
                        'Account/DocumentInformation',  # Get Step3 Data
                        'Account/Email',  # Get user email
                        'Account/FeeRate',  # Get fee rate of logged in user
                        'Account/Level',  # Get verif level of logged in user
                        'Account/PersonalInformation',  # Get Step1 Data
                        'Account/Phone',  # Get user phone number
                        'Account/Profile',  # Get trader profile
                        'Account/Questionnaire',  # Fill the questionnaire
                        'Account/Referral',  # Get referral information
                        'Account/ReferralCode',  # Get the referral code of the logged in user
                        'Account/ReferralNames',  # Get names of referred traders
                        'Account/ReferralReward',  # Get referral reward information
                        'Account/ReferredCode',  # Get referral code
                        'Account/ResidentInformation',  # Get Step2 Data
                        'Account/SecuritySettings',  # Get verif details of logged in user
                        'Account/User',  # Get all user info
                        'APIKey/APIKey',  # Get API Key for logged in user
                        'Auth/ConnectionHistory',  # Gets connection history of logged in user
                        'Balance/Balances',  # Gets the available balance for each currency for the logged in account.
                        'Balance/Balances/{Currency}',  # Gets the available balance for s currency for the logged in account.
                        'Balance/Deposits',  # Get all account deposits, including wire and digital currency, of the logged in user
                        'Balance/Withdrawals',  # Get all account withdrawals, including wire and digital currency, of the logged in user
                        'Bank/Accounts/{Currency}/{Location}',  # Get internal bank account for deposit
                        'Bank/Transactions',  # Get all account transactions of the logged in user
                        'Bank/UserAccounts',  # Gets all the bank accounts related to the logged in user.
                        'Bank/UserAccounts/{Currency}',  # Gets all the bank accounts related to the logged in user.
                        'ElectronicWallet/DepositWallets',  # Gets all crypto currency addresses related deposits to the logged in user.
                        'ElectronicWallet/DepositWallets/{DigiCurrency}',  # Gets all crypto currency addresses related deposits to the logged in user by currency.
                        'ElectronicWallet/Transactions',  # Get all digital currency transactions of the logged in user
                        'ElectronicWallet/Transactions/{DigiCurrency}',  # Get all digital currency transactions of the logged in user
                        'ElectronicWallet/UserWallets',  # Gets all external digital currency addresses related to the logged in user.
                        'ElectronicWallet/UserWallets/{DigiCurrency}',  # Gets all external digital currency addresses related to the logged in user by currency.
                        'Info/ReferenceCurrency',  # Get user's reference currency
                        'Info/ReferenceLanguage',  # Get user's reference language
                        'Notification/Messages',  # Get from oldest unread + 3 read message to newest messages
                        'Trade/Orders',  # Gets open orders for the logged in trader.
                        'Trade/Orders/{OrderID}',  # Gets an order for the logged in trader.
                        'Trade/StopOrders',  # Gets all stop orders for the logged in trader. Max 1000 record.
                        'Trade/StopOrdersHistory',  # Gets all stop orders for the logged in trader. Max 1000 record.
                        'Trade/Trades',  # Gets all transactions of logged in user
                        'Trade/UserTrades',  # Gets all transactions of logged in user
                    ],
                    'post': [
                        'Account/DocumentAddress',  # Upload address proof document
                        'Account/DocumentCorporation',  # Upload registered document document
                        'Account/DocumentID',  # Upload ID document copy
                        'Account/Email/RequestVerify',  # Request for verification email
                        'Account/Email/Verify',  # Verification email
                        'Account/GoogleAuth',  # Enable google auth
                        'Account/Level',  # Request verif level of logged in user
                        'Account/Questionnaire',  # Fill the questionnaire
                        'Account/Referral',  # Post a referral email
                        'APIKey/APIKey',  # Create a new API key for logged in user
                        'Auth/ChangePassword',  # Change password.
                        'Auth/ForgotPassword',  # Request reset password
                        'Auth/ForgotUserID',  # Request user id
                        'Auth/Login',  # Trader session log in.
                        'Auth/Logout',  # Logout from the current session.
                        'Auth/LogoutOtherSessions',  # Logout other sessions.
                        'Auth/ResetPassword',  # Reset password
                        'Bank/Transactions',  # Request a transfer from the traders account of the logged in user. This is only available for bank account
                        'Bank/UserAccounts',  # Add an account the logged in user
                        'ElectronicWallet/DepositWallets/{DigiCurrency}',  # Add an digital currency addresses to the logged in user.
                        'ElectronicWallet/Transactions/Deposits/{DigiCurrency}',  # Get all internal digital currency transactions of the logged in user
                        'ElectronicWallet/Transactions/Withdrawals/{DigiCurrency}',  # Get all external digital currency transactions of the logged in user
                        'ElectronicWallet/UserWallets/{DigiCurrency}',  # Add an external digital currency addresses to the logged in user.
                        'ElectronicWallet/Withdrawals/{DigiCurrency}',  # Request a transfer from the traders account to an external address. This is only available for crypto currencies.
                        'Notification/Messages',  # Mark all as read
                        'Notification/Messages/{ID}',  # Mark as read
                        'Trade/Orders',  # Place an order at the exchange.
                        'Trade/StopOrders',  # Place a stop order at the exchange.
                    ],
                    'put': [
                        'Account/CorporateData',  # Update user company data for corporate account
                        'Account/DocumentID',  # Update ID document meta data
                        'Account/DocumentInformation',  # Update Step3 Data
                        'Account/Email',  # Update user email
                        'Account/PersonalInformation',  # Update Step1 Data
                        'Account/Phone',  # Update user phone number
                        'Account/Questionnaire',  # update the questionnaire
                        'Account/ReferredCode',  # Update referral code
                        'Account/ResidentInformation',  # Update Step2 Data
                        'Account/SecuritySettings',  # Update verif details of logged in user
                        'Account/User',  # Update all user info
                        'Bank/UserAccounts',  # Update the label of existing user bank accounnt
                        'ElectronicWallet/DepositWallets/{DigiCurrency}/{AddressName}',  # Update the name of an address
                        'ElectronicWallet/UserWallets/{DigiCurrency}',  # Update the name of an external address
                        'Info/ReferenceCurrency',  # User's reference currency
                        'Info/ReferenceLanguage',  # Update user's reference language
                    ],
                    'delete': [
                        'APIKey/APIKey/{PublicKey}',  # Remove an API key
                        'Bank/Transactions/{RequestID}',  # Delete pending account withdraw of the logged in user
                        'Bank/UserAccounts/{Currency}/{Label}',  # Delete an account of the logged in user
                        'ElectronicWallet/DepositWallets/{DigiCurrency}/{AddressName}',  # Delete an digital currency addresses related to the logged in user.
                        'ElectronicWallet/UserWallets/{DigiCurrency}/{AddressName}',  # Delete an external digital currency addresses related to the logged in user.
                        'Trade/Orders',  # Cancels all existing order
                        'Trade/Orders/{OrderID}',  # Cancels an existing order
                        'Trade/StopOrders',  # Cancels all existing stop orders
                        'Trade/StopOrders/{ID}',  # Cancels an existing stop order
                    ],
                },
            },
        }
        params.update(config)
        super(gatecoin, self).__init__(params)

    def fetch_markets(self):
        response = self.publicGetPublicLiveTickers()
        markets = response['tickers']
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['currencyPair']
            base = id[0:3]
            quote = id[3:6]
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalanceBalances()
        balances = response['balances']
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            account = {
                'free': balance['availableBalance'],
                'used': self.sum(
                    balance['pendingIncoming'],
                    balance['pendingOutgoing'],
                    balance['openOrder']),
                'total': balance['balance'],
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        orderbook = self.publicGetPublicMarketDepthCurrencyPair(self.extend({
            'CurrencyPair': market['id'],
        }, params))
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'volume')

    def parse_ticker(self, ticker, market=None):
        timestamp = int(ticker['createDateTime']) * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': float(ticker['vwap']),
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetPublicLiveTickers(params)
        tickers = response['tickers']
        result = {}
        for t in range(0, len(tickers)):
            ticker = tickers[t]
            id = ticker['currencyPair']
            market = self.markets_by_id[id]
            symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetPublicLiveTickerCurrencyPair(self.extend({
            'CurrencyPair': market['id'],
        }, params))
        ticker = response['ticker']
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market=None):
        side = None
        order = None
        if 'way' in trade:
            side = 'buy' if (trade['way'] == 'bid') else 'sell'
            orderId = trade['way'] + 'OrderId'
            order = trade[orderId]
        timestamp = int(trade['transactionTime']) * 1000
        if not market:
            market = self.markets_by_id[trade['currencyPair']]
        return {
            'info': trade,
            'id': str(trade['transactionId']),
            'order': order,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['quantity'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetPublicTransactionsCurrencyPair(self.extend({
            'CurrencyPair': market['id'],
        }, params))
        return self.parse_trades(response['transactions'], market)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            int(ohlcv['createDateTime']) * 1000,
            ohlcv['open'],
            ohlcv['high'],
            ohlcv['low'],
            None,
            ohlcv['volume'],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'CurrencyPair': market['id'],
            'Timeframe': self.timeframes[timeframe],
        }
        if limit:
            request['Count'] = limit
        request = self.extend(request, params)
        response = self.publicGetPublicTickerHistoryCurrencyPairTimeframe(request)
        return self.parse_ohlcvs(response['tickers'], market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'Code': self.market_id(symbol),
            'Way': 'Bid' if (side == 'buy') else 'Ask',
            'Amount': amount,
        }
        if type == 'limit':
            order['Price'] = price
        if self.twofa:
            if 'ValidationCode' in params:
                order['ValidationCode'] = params['ValidationCode']
            else:
                raise AuthenticationError(self.id + ' two-factor authentication requires a missing ValidationCode parameter')
        response = self.privatePostTradeOrders(self.extend(order, params))
        return {
            'info': response,
            'id': response['clOrderId'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privateDeleteTradeOrdersOrderID({'OrderID': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            contentType = '' if (method == 'GET') else 'application/json'
            auth = method + url + contentType + str(nonce)
            auth = auth.lower()
            signature = self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha256, 'base64')
            headers = {
                'API_PUBLIC_KEY': self.apiKey,
                'API_REQUEST_SIGNATURE': signature,
                'API_REQUEST_DATE': nonce,
            }
            if method != 'GET':
                headers['Content-Type'] = contentType
                body = self.json(self.extend({'nonce': nonce}, params))
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'responseStatus' in response:
            if 'message' in response['responseStatus']:
                if response['responseStatus']['message'] == 'OK':
                    return response
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class gateio (bter):

    def __init__(self, config={}):
        params = {
            'id': 'gateio',
            'name': 'Gate.io',
            'countries': 'CN',
            'rateLimit': 1000,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/31784029-0313c702-b509-11e7-9ccc-bc0da6a0e435.jpg',
                'api': {
                    'public': 'https://data.gate.io/api',
                    'private': 'https://data.gate.io/api',
                },
                'www': 'https://gate.io/',
                'doc': 'https://gate.io/api2',
            },
        }
        params.update(config)
        super(gateio, self).__init__(params)

# -----------------------------------------------------------------------------


class gdax (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'gdax',
            'name': 'GDAX',
            'countries': 'US',
            'rateLimit': 1000,
            'hasCORS': True,
            'hasFetchOHLCV': True,
            'hasWithdraw': True,
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'timeframes': {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '30m': 1800,
                '1h': 3600,
                '2h': 7200,
                '4h': 14400,
                '12h': 43200,
                '1d': 86400,
                '1w': 604800,
                '1M': 2592000,
                '1y': 31536000,
            },
            'urls': {
                'test': 'https://api-public.sandbox.gdax.com',
                'logo': 'https://user-images.githubusercontent.com/1294454/27766527-b1be41c6-5edb-11e7-95f6-5b496c469e2c.jpg',
                'api': 'https://api.gdax.com',
                'www': 'https://www.gdax.com',
                'doc': 'https://docs.gdax.com',
            },
            'api': {
                'public': {
                    'get': [
                        'currencies',
                        'products',
                        'products/{id}/book',
                        'products/{id}/candles',
                        'products/{id}/stats',
                        'products/{id}/ticker',
                        'products/{id}/trades',
                        'time',
                    ],
                },
                'private': {
                    'get': [
                        'accounts',
                        'accounts/{id}',
                        'accounts/{id}/holds',
                        'accounts/{id}/ledger',
                        'coinbase-accounts',
                        'fills',
                        'funding',
                        'orders',
                        'orders/{id}',
                        'payment-methods',
                        'position',
                        'reports/{id}',
                        'users/self/trailing-volume',
                    ],
                    'post': [
                        'deposits/coinbase-account',
                        'deposits/payment-method',
                        'funding/repay',
                        'orders',
                        'position/close',
                        'profiles/margin-transfer',
                        'reports',
                        'withdrawals/coinbase',
                        'withdrawals/crypto',
                        'withdrawals/payment-method',
                    ],
                    'delete': [
                        'orders',
                        'orders/{id}',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.0,
                    'taker': 0.25 / 100,
                },
            },
        }
        params.update(config)
        super(gdax, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetProducts()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['id']
            base = market['base_currency']
            quote = market['quote_currency']
            symbol = base + '/' + quote
            amountLimits = {
                'min': market['base_min_size'],
                'max': market['base_max_size'],
            }
            priceLimits = {
                'min': market['quote_increment'],
                'max': None,
            }
            costLimits = {
                'min': priceLimits['min'],
                'max': None,
            }
            limits = {
                'amount': amountLimits,
                'price': priceLimits,
                'cost': costLimits,
            }
            precision = {
                'amount': -math.log10(amountLimits['min']),
                'price': -math.log10(priceLimits['min']),
            }
            taker = self.fees['trading']['taker']
            if (base == 'ETH') or (base == 'LTC'):
                taker = 0.3
            result.append(self.extend(self.fees['trading'], {
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
                'precision': precision,
                'limits': limits,
                'taker': taker,
            }))
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privateGetAccounts()
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            account = {
                'free': float(balance['available']),
                'used': float(balance['hold']),
                'total': float(balance['balance']),
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetProductsIdBook(self.extend({
            'id': self.market_id(symbol),
            'level': 2,  # 1 best bidask, 2 aggregated, 3 full
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = self.extend({
            'id': market['id'],
        }, params)
        ticker = self.publicGetProductsIdTicker(request)
        quote = self.publicGetProductsIdStats(request)
        timestamp = self.parse8601(ticker['time'])
        bid = None
        ask = None
        if 'bid' in ticker:
            bid = float(ticker['bid'])
        if 'ask' in ticker:
            ask = float(ticker['ask'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(quote['high']),
            'low': float(quote['low']),
            'bid': bid,
            'ask': ask,
            'vwap': None,
            'open': float(quote['open']),
            'close': None,
            'first': None,
            'last': float(quote['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = self.parse8601(['time'])
        # type = None
        return {
            'id': str(trade['trade_id']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['side'],
            'price': float(trade['price']),
            'amount': float(trade['size']),
        }

    def fetch_trades(self, market, params={}):
        self.load_markets()
        return self.publicGetProductsIdTrades(self.extend({
            'id': self.market_id(market),  # fixes issue  #2
        }, params))

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv[0] * 1000,
            ohlcv[3],
            ohlcv[2],
            ohlcv[1],
            ohlcv[4],
            ohlcv[5],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        granularity = self.timeframes[timeframe]
        request = {
            'id': market['id'],
            'granularity': granularity,
        }
        if since:
            request['start'] = self.iso8601(since)
            if not limit:
                limit = 200  # max = 200
            request['end'] = self.iso8601(limit * granularity * 1000 + since)
        response = self.publicGetProductsIdCandles(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def fetchTime(self):
        response = self.publicGetTime()
        return self.parse8601(response['iso'])

    def getOrderStatus(self, status):
        statuses = {
            'pending': 'open',
            'active': 'open',
            'open': 'open',
            'done': 'closed',
            'canceled': 'canceled',
        }
        return self.safe_string(statuses, status, status)

    def parse_order(self, order, market=None):
        timestamp = self.parse8601(order['created_at'])
        symbol = None
        if not market:
            if order['product_id'] in self.markets_by_id:
                market = self.markets_by_id[order['product_id']]
        status = self.getOrderStatus(order['status'])
        price = self.safe_float(order, 'price')
        amount = self.safe_float(order, 'size')
        filled = self.safe_float(order, 'filled_size')
        remaining = amount - filled
        cost = self.safe_float(order, 'executed_value')
        if market:
            symbol = market['symbol']
        return {
            'id': order['id'],
            'info': order,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': status,
            'symbol': symbol,
            'type': order['type'],
            'side': order['side'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'fee': None,
        }

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = self.privateGetOrdersId(self.extend({
            'id': id,
        }, params))
        return self.parse_order(response)

    def fetch_orders(self, symbol=None, params={}):
        self.load_markets()
        request = {
            'status': 'all',
        }
        market = None
        if symbol:
            market = self.market(symbol)
            request['product_id'] = market['id']
        response = self.privateGetOrders(self.extend(request, params))
        return self.parse_orders(response, market)

    def fetch_open_orders(self, symbol=None, params={}):
        self.load_markets()
        request = {}
        market = None
        if symbol:
            market = self.market(symbol)
            request['product_id'] = market['id']
        response = self.privateGetOrders(self.extend(request, params))
        return self.parse_orders(response, market)

    def fetchClosedOrders(self, symbol=None, params={}):
        self.load_markets()
        request = {
            'status': 'done',
        }
        market = None
        if symbol:
            market = self.market(symbol)
            request['product_id'] = market['id']
        response = self.privateGetOrders(self.extend(request, params))
        return self.parse_orders(response, market)

    def create_order(self, market, type, side, amount, price=None, params={}):
        self.load_markets()
        # oid = str(self.nonce())
        order = {
            'product_id': self.market_id(market),
            'side': side,
            'size': amount,
            'type': type,
        }
        if type == 'limit':
            order['price'] = price
        response = self.privatePostOrders(self.extend(order, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privateDeleteOrdersId({'id': id})

    def getPaymentMethods(self):
        response = self.privateGetPaymentMethods()
        return response

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        response = None
        if 'payment_method_id' in params:
            response = self.privatePostWithdrawalsPaymentMethod(self.extend({
                'currency': currency,
                'amount': amount,
            }, params))
        else:
            response = self.privatePostWithdrawalsCrypto(self.extend({
                'currency': currency,
                'amount': amount,
                'crypto_address': address,
            }, params))
        if not response:
            raise ExchangeError(self.id + ' withdraw() error: ' + self.json(response))
        return {
            'info': response,
            'id': response['id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if method == 'GET':
            if query:
                request += '?' + self.urlencode(query)
        url = self.urls['api'] + request
        if api == 'private':
            if not self.apiKey:
                raise AuthenticationError(self.id + ' requires apiKey property for authentication and trading')
            if not self.secret:
                raise AuthenticationError(self.id + ' requires secret property for authentication and trading')
            if not self.password:
                raise AuthenticationError(self.id + ' requires password property for authentication and trading')
            nonce = str(self.nonce())
            payload = ''
            if method == 'POST':
                if query:
                    body = self.json(query)
                    payload = body
            # payload = body if (body) else ''
            what = nonce + method + request + payload
            secret = base64.b64decode(self.secret)
            signature = self.hmac(self.encode(what), secret, hashlib.sha256, 'base64')
            headers = {
                'CB-ACCESS-KEY': self.apiKey,
                'CB-ACCESS-SIGN': self.decode(signature),
                'CB-ACCESS-TIMESTAMP': nonce,
                'CB-ACCESS-PASSPHRASE': self.password,
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'message' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class gemini (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'gemini',
            'name': 'Gemini',
            'countries': 'US',
            'rateLimit': 1500,  # 200 for private API
            'version': 'v1',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27816857-ce7be644-6096-11e7-82d6-3c257263229c.jpg',
                'api': 'https://api.gemini.com',
                'www': 'https://gemini.com',
                'doc': 'https://docs.gemini.com/rest-api',
            },
            'api': {
                'public': {
                    'get': [
                        'symbols',
                        'pubticker/{symbol}',
                        'book/{symbol}',
                        'trades/{symbol}',
                        'auction/{symbol}',
                        'auction/{symbol}/history',
                    ],
                },
                'private': {
                    'post': [
                        'order/new',
                        'order/cancel',
                        'order/cancel/session',
                        'order/cancel/all',
                        'order/status',
                        'orders',
                        'mytrades',
                        'tradevolume',
                        'balances',
                        'deposit/{currency}/newAddress',
                        'withdraw/{currency}',
                        'heartbeat',
                    ],
                },
            },
        }
        params.update(config)
        super(gemini, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetSymbols()
        result = []
        for p in range(0, len(markets)):
            id = markets[p]
            market = id
            uppercase = market.upper()
            base = uppercase[0:3]
            quote = uppercase[3:6]
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetBookSymbol(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetPubtickerSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        timestamp = ticker['volume']['timestamp']
        baseVolume = market['base']
        quoteVolume = market['quote']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['volume'][baseVolume]),
            'quoteVolume': float(ticker['volume'][quoteVolume]),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['timestampms']
        return {
            'id': str(trade['tid']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTradesSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privatePostBalances()
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            account = {
                'free': float(balance['available']),
                'used': 0.0,
                'total': float(balance['amount']),
            }
            account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        order = {
            'client_order_id': self.nonce(),
            'symbol': self.market_id(symbol),
            'amount': str(amount),
            'price': str(price),
            'side': side,
            'type': 'exchange limit',  # gemini allows limit orders only
        }
        response = self.privatePostOrderNew(self.extend(order, params))
        return {
            'info': response,
            'id': response['order_id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostCancelOrder({'order_id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            request = self.extend({
                'request': url,
                'nonce': nonce,
            }, query)
            payload = self.json(request)
            payload = base64.b64encode(self.encode(payload))
            signature = self.hmac(payload, self.encode(self.secret), hashlib.sha384)
            headers = {
                'Content-Type': 'text/plain',
                'X-GEMINI-APIKEY': self.apiKey,
                'X-GEMINI-PAYLOAD': payload,
                'X-GEMINI-SIGNATURE': signature,
            }
        url = self.urls['api'] + url
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'result' in response:
            if response['result'] == 'error':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class hitbtc (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'hitbtc',
            'name': 'HitBTC',
            'countries': 'HK',  # Hong Kong
            'rateLimit': 1500,
            'version': '1',
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasFetchOrder': True,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766555-8eaec20e-5edc-11e7-9c5b-6dc69fc42f5e.jpg',
                'api': 'http://api.hitbtc.com',
                'www': 'https://hitbtc.com',
                'doc': [
                    'https://hitbtc.com/api',
                    'http://hitbtc-com.github.io/hitbtc-api',
                    'http://jsfiddle.net/bmknight/RqbYB',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        '{symbol}/orderbook',
                        '{symbol}/ticker',
                        '{symbol}/trades',
                        '{symbol}/trades/recent',
                        'symbols',
                        'ticker',
                        'time,'
                    ],
                },
                'trading': {
                    'get': [
                        'balance',
                        'orders/active',
                        'orders/recent',
                        'order',
                        'trades/by/order',
                        'trades',
                    ],
                    'post': [
                        'new_order',
                        'cancel_order',
                        'cancel_orders',
                    ],
                },
                'payment': {
                    'get': [
                        'balance',
                        'address/{currency}',
                        'transactions',
                        'transactions/{transaction}',
                    ],
                    'post': [
                        'transfer_to_trading',
                        'transfer_to_main',
                        'address/{currency}',
                        'payout',
                    ],
                }
            },
        }
        params.update(config)
        super(hitbtc, self).__init__(params)

    def common_currency_code(self, currency):
        if currency == 'XBT':
            return 'BTC'
        if currency == 'BCC':
            return 'BCH'
        if currency == 'DRK':
            return 'DASH'
        if currency == 'CAT':
            return 'BitClave'
        return currency

    def fetch_markets(self):
        markets = self.publicGetSymbols()
        result = []
        for p in range(0, len(markets['symbols'])):
            market = markets['symbols'][p]
            id = market['symbol']
            base = market['commodity']
            quote = market['currency']
            lot = float(market['lot'])
            step = float(market['step'])
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'lot': lot,
                'step': step,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        method = self.safe_string(params, 'type', 'trading')
        method += 'GetBalance'
        query = self.omit(params, 'type')
        response = getattr(self, method)(query)
        balances = response['balance']
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            code = balance['currency_code']
            currency = self.common_currency_code(code)
            free = self.safe_float(balance, 'cash', 0.0)
            free = self.safe_float(balance, 'balance', free)
            used = self.safe_float(balance, 'reserved', 0.0)
            account = {
                'free': free,
                'used': used,
                'total': self.sum(free, used),
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetSymbolOrderbook(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['timestamp']
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'bid'),
            'ask': self.safe_float(ticker, 'ask'),
            'vwap': None,
            'open': self.safe_float(ticker, 'open'),
            'close': None,
            'first': None,
            'last': self.safe_float(ticker, 'last'),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'volume'),
            'quoteVolume': self.safe_float(ticker, 'volume_quote'),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTicker(params)
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetSymbolTicker(self.extend({
            'symbol': market['id'],
        }, params))
        if 'message' in ticker:
            raise ExchangeError(self.id + ' ' + ticker['message'])
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market=None):
        return {
            'info': trade,
            'id': trade[0],
            'timestamp': trade[3],
            'datetime': self.iso8601(trade[3]),
            'symbol': market['symbol'],
            'type': None,
            'side': trade[4],
            'price': float(trade[1]),
            'amount': float(trade[2]),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetSymbolTrades(self.extend({
            'symbol': market['id'],
            # 'from': 0,
            # 'till': 100,
            # 'by': 'ts',  # or by trade_id
            # 'sort': 'desc',  # or asc
            # 'start_index': 0,
            # 'max_results': 1000,
            # 'format_item': 'object',
            # 'format_price': 'number',
            # 'format_amount': 'number',
            # 'format_tid': 'string',
            # 'format_timestamp': 'millisecond',
            # 'format_wrap': False,
            'side': 'true',
        }, params))
        return self.parse_trades(response['trades'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        # check if amount can be evenly divided into lots
        # they want integer quantity in lot units
        quantity = float(amount) / market['lot']
        wholeLots = int(round(quantity))
        difference = quantity - wholeLots
        if abs(difference) > market['step']:
            raise ExchangeError(self.id + ' order amount should be evenly divisible by lot unit size of ' + str(market['lot']))
        clientOrderId = self.milliseconds()
        order = {
            'clientOrderId': str(clientOrderId),
            'symbol': market['id'],
            'side': side,
            'quantity': str(wholeLots),  # quantity in integer lot units
            'type': type,
        }
        if type == 'limit':
            order['price'] = '{:.10f}'.format(price)
        else:
            order['timeInForce'] = 'FOK'
        response = self.tradingPostNewOrder(self.extend(order, params))
        return {
            'info': response,
            'id': response['ExecutionReport']['clientOrderId'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.tradingPostCancelOrder(self.extend({
            'clientOrderId': id,
        }, params))

    def getOrderStatus(self, status):
        statuses = {
            'new': 'open',
            'partiallyFilled': 'partial',
            'filled': 'closed',
            'canceled': 'canceled',
            'rejected': 'rejected',
            'expired': 'expired',
        }
        return self.safe_string(statuses, status)

    def parse_order(self, order, market=None):
        timestamp = int(order['lastTimestamp'])
        symbol = None
        if not market:
            market = self.markets_by_id[order['symbol']]
        status = self.safe_string(order, 'orderStatus')
        if status:
            status = self.getOrderStatus(status)
        averagePrice = self.safe_float(order, 'avgPrice', 0.0)
        price = self.safe_float(order, 'orderPrice')
        amount = self.safe_float(order, 'orderQuantity')
        remaining = self.safe_float(order, 'quantityLeaves')
        filled = None
        cost = None
        if market:
            symbol = market['symbol']
            amount *= market['lot']
            remaining *= market['lot']
        if amount and remaining:
            filled = amount - remaining
            cost = averagePrice * filled
        return {
            'id': str(order['clientOrderId']),
            'info': order,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': status,
            'symbol': symbol,
            'type': order['type'],
            'side': order['side'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'fee': None,
        }

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = self.tradingGetOrder(self.extend({
            'client_order_id': id,
        }, params))
        return self.parse_order(response['orders'][0])

    def fetch_open_orders(self, symbol=None, params={}):
        self.load_markets()
        statuses = ['new', 'partiallyFiiled']
        market = self.market(symbol)
        request = {
            'sort': 'desc',
            'statuses': ','.join(statuses),
        }
        if market:
            request['symbols'] = market['id']
        response = self.tradingGetOrdersActive(self.extend(request, params))
        return self.parse_orders(response['orders'], market)

    def fetchClosedOrders(self, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        statuses = ['filled', 'canceled', 'rejected', 'expired']
        request = {
            'sort': 'desc',
            'statuses': ','.join(statuses),
            'max_results': 1000,
        }
        if market:
            request['symbols'] = market['id']
        response = self.tradingGetOrdersRecent(self.extend(request, params))
        return self.parse_orders(response['orders'], market)

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        response = self.paymentPostPayout(self.extend({
            'currency_code': currency,
            'amount': amount,
            'address': address,
        }, params))
        return {
            'info': response,
            'id': response['transaction'],
        }

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = '/' + 'api' + '/' + self.version + '/' + api + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            payload = {'nonce': nonce, 'apikey': self.apiKey}
            query = self.extend(payload, query)
            if method == 'GET':
                url += '?' + self.urlencode(query)
            else:
                url += '?' + self.urlencode(payload)
            auth = url
            if method == 'POST':
                if query:
                    body = self.urlencode(query)
                    auth += body
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Signature': self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha512).lower(),
            }
        url = self.urls['api'] + url
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'code' in response:
            if 'ExecutionReport' in response:
                if response['ExecutionReport']['orderRejectReason'] == 'orderExceedsLimit':
                    raise InsufficientFunds(self.id + ' ' + self.json(response))
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class hitbtc2 (hitbtc):

    def __init__(self, config={}):
        params = {
            'id': 'hitbtc2',
            'name': 'HitBTC v2',
            'countries': 'HK',  # Hong Kong
            'rateLimit': 1500,
            'version': '2',
            'hasCORS': True,
            'hasFetchTickers': True,
            'hasFetchOrders': False,
            'hasFetchOpenOrders': False,
            'hasFetchClosedOrders': False,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766555-8eaec20e-5edc-11e7-9c5b-6dc69fc42f5e.jpg',
                'api': 'https://api.hitbtc.com',
                'www': 'https://hitbtc.com',
                'doc': [
                    'https://api.hitbtc.com/api/2/explore',
                    'https://github.com/hitbtc-com/hitbtc-api/blob/master/APIv2.md',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'symbol',  # Available Currency Symbols
                        'symbol/{symbol}',  # Get symbol info
                        'currency',  # Available Currencies
                        'currency/{currency}',  # Get currency info
                        'ticker',  # Ticker list for all symbols
                        'ticker/{symbol}',  # Ticker for symbol
                        'trades/{symbol}',  # Trades
                        'orderbook/{symbol}',  # Orderbook
                    ],
                },
                'private': {
                    'get': [
                        'order',  # List your current open orders
                        'order/{clientOrderId}',  # Get a single order by clientOrderId
                        'trading/balance',  # Get trading balance
                        'trading/fee/{symbol}',  # Get trading fee rate
                        'history/trades',  # Get historical trades
                        'history/order',  # Get historical orders
                        'history/order/{id}/trades',  # Get historical trades by specified order
                        'account/balance',  # Get main acccount balance
                        'account/transactions',  # Get account transactions
                        'account/transactions/{id}',  # Get account transaction by id
                        'account/crypto/address/{currency}',  # Get deposit crypro address
                    ],
                    'post': [
                        'order',  # Create new order
                        'account/crypto/withdraw',  # Withdraw crypro
                        'account/crypto/address/{currency}',  # Create new deposit crypro address
                        'account/transfer',  # Transfer amount to trading
                    ],
                    'put': [
                        'order/{clientOrderId}',  # Create new order
                        'account/crypto/withdraw/{id}',  # Commit withdraw crypro
                    ],
                    'delete': [
                        'order',  # Cancel all open orders
                        'order/{clientOrderId}',  # Cancel order
                        'account/crypto/withdraw/{id}',  # Rollback withdraw crypro
                    ],
                    'patch': [
                        'order/{clientOrderId}',  # Cancel Replace order
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.0 / 100,
                    'taker': 0.1 / 100,
                },
            },
        }
        params.update(config)
        super(hitbtc2, self).__init__(params)

    def common_currency_code(self, currency):
        if currency == 'XBT':
            return 'BTC'
        if currency == 'BCC':
            return 'BCH'
        if currency == 'DRK':
            return 'DASH'
        if currency == 'CAT':
            return 'BitClave'
        return currency

    def fetch_markets(self):
        markets = self.publicGetSymbol()
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            id = market['id']
            base = market['baseCurrency']
            quote = market['quoteCurrency']
            lot = market['quantityIncrement']
            step = float(market['tickSize'])
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            precision = {
                'price': 2,
                'amount': -1 * math.log10(step),
            }
            amountLimits = {'min': lot}
            limits = {'amount': amountLimits}
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'lot': lot,
                'step': step,
                'info': market,
                'precision': precision,
                'limits': limits,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privateGetTradingBalance()
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            code = balance['currency']
            currency = self.common_currency_code(code)
            account = {
                'free': float(balance['available']),
                'used': float(balance['reserved']),
                'total': 0.0,
            }
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetOrderbookSymbol(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'bid', 'ask', 'price', 'size')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.parse8601(ticker['timestamp'])
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'bid'),
            'ask': self.safe_float(ticker, 'ask'),
            'vwap': None,
            'open': self.safe_float(ticker, 'open'),
            'close': self.safe_float(ticker, 'close'),
            'first': None,
            'last': self.safe_float(ticker, 'last'),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'volume'),
            'quoteVolume': self.safe_float(ticker, 'volumeQuote'),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTicker(params)
        result = {}
        for i in range(0, len(tickers)):
            ticker = tickers[i]
            id = ticker['symbol']
            market = self.markets_by_id[id]
            symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetTickerSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        if 'message' in ticker:
            raise ExchangeError(self.id + ' ' + ticker['message'])
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(trade['timestamp'])
        return {
            'info': trade,
            'id': str(trade['id']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['side'],
            'price': float(trade['price']),
            'amount': float(trade['quantity']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTradesSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        clientOrderId = self.milliseconds()
        amount = float(amount)
        order = {
            'clientOrderId': str(clientOrderId),
            'symbol': market['id'],
            'side': side,
            'quantity': str(amount),
            'type': type,
        }
        if type == 'limit':
            price = float(price)
            order['price'] = '{:.10f}'.format(price)
        else:
            order['timeInForce'] = 'FOK'
        response = self.privatePostOrder(self.extend(order, params))
        return {
            'info': response,
            'id': response['clientOrderId'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privateDeleteOrderClientOrderId(self.extend({
            'clientOrderId': id,
        }, params))

    def parse_order(self, order, market=None):
        lastTime = self.parse8601(order['updatedAt'])
        timestamp = lastTime.getTime()
        if not market:
            market = self.markets_by_id[order['symbol']]
        symbol = market['symbol']
        amount = order['quantity']
        filled = order['cumQuantity']
        remaining = amount - filled
        return {
            'id': str(order['clientOrderId']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': order['status'],
            'symbol': symbol,
            'type': order['type'],
            'side': order['side'],
            'price': order['price'],
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'fee': None,
            'info': order,
        }

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = self.privateGetOrder(self.extend({
            'client_order_id': id,
        }, params))
        return self.parse_order(response['orders'][0])

    def fetch_open_orders(self, symbol=None, params={}):
        self.load_markets()
        market = None
        if symbol:
            market = self.market(symbol)
            params = self.extend({'symbol': market['id']})
        response = self.privateGetOrder(params)
        return self.parse_orders(response, market)

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        amount = float(amount)
        response = self.privatePostAccountCryptoWithdraw(self.extend({
            'currency': currency,
            'amount': str(amount),
            'address': address,
        }, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = '/api' + '/' + self.version + '/'
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            url += api + '/' + self.implode_params(path, params)
            if query:
                url += '?' + self.urlencode(query)
        else:
            url += self.implode_params(path, params) + '?' + self.urlencode(query)
            if method != 'GET':
                if query:
                    body = self.json(query)
            payload = self.encode(self.apiKey + ':' + self.secret)
            auth = base64.b64encode(payload)
            headers = {
                'Authorization': "Basic " + self.decode(auth),
                'Content-Type': 'application/json',
            }
        url = self.urls['api'] + url
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class huobi1 (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'huobi1',
            'name': 'Huobi v1',
            'countries': 'CN',
            'rateLimit': 2000,
            'version': 'v1',
            'hasFetchOHLCV': True,
            'accounts': None,
            'accountsById': None,
            'timeframes': {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '1h': '60min',
                '1d': '1day',
                '1w': '1week',
                '1M': '1mon',
                '1y': '1year',
            },
            'api': {
                'market': {
                    'get': [
                        'history/kline',  # 获取K线数据
                        'detail/merged',  # 获取聚合行情(Ticker)
                        'depth',  # 获取 Market Depth 数据
                        'trade',  # 获取 Trade Detail 数据
                        'history/trade',  # 批量获取最近的交易记录
                        'detail',  # 获取 Market Detail 24小时成交量数据
                    ],
                },
                'public': {
                    'get': [
                        'common/symbols',  # 查询系统支持的所有交易对
                        'common/currencys',  # 查询系统支持的所有币种
                        'common/timestamp',  # 查询系统当前时间
                    ],
                },
                'private': {
                    'get': [
                        'account/accounts',  # 查询当前用户的所有账户(即account-id)
                        'account/accounts/{id}/balance',  # 查询指定账户的余额
                        'order/orders/{id}',  # 查询某个订单详情
                        'order/orders/{id}/matchresults',  # 查询某个订单的成交明细
                        'order/orders',  # 查询当前委托、历史委托
                        'order/matchresults',  # 查询当前成交、历史成交
                        'dw/withdraw-virtual/addresses',  # 查询虚拟币提现地址
                    ],
                    'post': [
                        'order/orders/place',  # 创建并执行一个新订单 (一步下单， 推荐使用)
                        'order/orders',  # 创建一个新的订单请求 （仅创建订单，不执行下单）
                        'order/orders/{id}/place',  # 执行一个订单 （仅执行已创建的订单）
                        'order/orders/{id}/submitcancel',  # 申请撤销一个订单请求
                        'order/orders/batchcancel',  # 批量撤销订单
                        'dw/balance/transfer',  # 资产划转
                        'dw/withdraw-virtual/create',  # 申请提现虚拟币
                        'dw/withdraw-virtual/{id}/place',  # 确认申请虚拟币提现
                        'dw/withdraw-virtual/{id}/cancel',  # 申请取消提现虚拟币
                    ],
                },
            },
        }
        params.update(config)
        super(huobi1, self).__init__(params)

    def fetch_markets(self):
        response = self.publicGetCommonSymbols()
        markets = response['data']
        numMarkets = len(markets)
        if numMarkets < 1:
            raise ExchangeError(self.id + ' publicGetCommonSymbols returned empty response: ' + self.json(response))
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            baseId = market['base-currency']
            quoteId = market['quote-currency']
            base = baseId.upper()
            quote = quoteId.upper()
            id = baseId + quoteId
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def parse_ticker(self, ticker, market=None):
        symbol = None
        if market:
            symbol = market['symbol']
        last = None
        if 'last' in ticker:
            last = ticker['last']
        timestamp = self.milliseconds()
        if 'ts' in ticker:
            timestamp = ticker['ts']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': ticker['high'],
            'low': ticker['low'],
            'bid': ticker['bid'][0],
            'ask': ticker['ask'][0],
            'vwap': None,
            'open': ticker['open'],
            'close': ticker['close'],
            'first': None,
            'last': last,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['amount']),
            'quoteVolume': ticker['vol'],
            'info': ticker,
        }

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.marketGetDepth(self.extend({
            'symbol': market['id'],
            'type': 'step0',
        }, params))
        return self.parse_order_book(response['tick'], response['tick']['ts'])

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.marketGetDetailMerged(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_ticker(response['tick'], market)

    def parse_trade(self, trade, market):
        timestamp = trade['ts']
        return {
            'info': trade,
            'id': str(trade['id']),
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['direction'],
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def parse_trades_data(self, data, market):
        result = []
        for i in range(0, len(data)):
            trades = self.parse_trades(data[i]['data'], market)
            for k in range(0, len(trades)):
                result.append(trades[k])
        return result

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.marketGetHistoryTrade(self.extend({
            'symbol': market['id'],
            'size': 2000,
        }, params))
        return self.parse_trades_data(response['data'], market)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv['id'] * 1000,
            ohlcv['open'],
            ohlcv['high'],
            ohlcv['low'],
            ohlcv['close'],
            ohlcv['vol'],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.marketGetHistoryKline(self.extend({
            'symbol': market['id'],
            'period': self.timeframes[timeframe],
            'size': 2000,  # max = 2000
        }, params))
        return self.parse_ohlcvs(response['data'], market, timeframe, since, limit)

    def loadAccounts(self, reload=False):
        if reload:
            self.accounts = self.fetchAccounts()
        else:
            if self.accounts:
                return self.accounts
            else:
                self.accounts = self.fetchAccounts()
                self.accountsById = self.index_by(self.accounts, 'id')
        return self.accounts

    def fetchAccounts(self):
        self.load_markets()
        response = self.privateGetAccountAccounts()
        return response['data']

    def fetch_balance(self, params={}):
        self.load_markets()
        self.loadAccounts()
        response = self.privateGetAccountAccountsIdBalance(self.extend({
            'id': self.accounts[0]['id'],
        }, params))
        balances = response['data']['list']
        result = {'info': response}
        for i in range(0, len(balances)):
            balance = balances[i]
            uppercase = balance['currency'].upper()
            currency = self.common_currency_code(uppercase)
            account = self.account()
            account['free'] = float(balance['balance'])
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        self.loadAccounts()
        market = self.market(symbol)
        order = {
            'account-id': self.accounts[0]['id'],
            'amount': '{:.10f}'.format(amount),
            'symbol': market['id'],
            'type': side + '-' + type,
        }
        if type == 'limit':
            order['price'] = '{:.10f}'.format(price)
        response = self.privatePostOrderOrdersPlace(self.extend(order, params))
        return {
            'info': response,
            'id': response['data'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostOrderOrdersIdSubmitcancel({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = '/'
        if api == 'market':
            url += api
        else:
            url += self.version
        url += '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            timestamp = self.YmdHMS(self.milliseconds(), 'T')
            request = self.keysort(self.extend({
                'SignatureMethod': 'HmacSHA256',
                'SignatureVersion': '2',
                'AccessKeyId': self.apiKey,
                'Timestamp': timestamp,
            }, query))
            auth = self.urlencode(request)
            payload = "\n".join([method, self.hostname, url, auth])
            signature = self.hmac(self.encode(payload), self.encode(self.secret), hashlib.sha256, 'base64')
            auth += '&' + self.urlencode({'Signature': signature})
            if method == 'GET':
                url += '?' + auth
            else:
                body = self.json(query)
                headers = {
                    'Content-Type': 'application/json',
                }
        else:
            if params:
                url += '?' + self.urlencode(params)
        url = self.urls['api'] + url
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] == 'error':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class huobicny (huobi1):

    def __init__(self, config={}):
        params = {
            'id': 'huobicny',
            'name': 'Huobi CNY',
            'hostname': 'be.huobi.com',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766569-15aa7b9a-5edd-11e7-9e7f-44791f4ee49c.jpg',
                'api': 'https://be.huobi.com',
                'www': 'https://www.huobi.com',
                'doc': 'https://github.com/huobiapi/API_Docs/wiki/REST_api_reference',
            },
        }
        params.update(config)
        super(huobicny, self).__init__(params)

# -----------------------------------------------------------------------------


class huobipro (huobi1):

    def __init__(self, config={}):
        params = {
            'id': 'huobipro',
            'name': 'Huobi Pro',
            'hostname': 'api.huobi.pro',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766569-15aa7b9a-5edd-11e7-9e7f-44791f4ee49c.jpg',
                'api': 'https://api.huobi.pro',
                'www': 'https://www.huobi.pro',
                'doc': 'https://github.com/huobiapi/API_Docs/wiki/REST_api_reference',
            },
        }
        params.update(config)
        super(huobipro, self).__init__(params)

# -----------------------------------------------------------------------------


class huobi (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'huobi',
            'name': 'Huobi',
            'countries': 'CN',
            'rateLimit': 2000,
            'version': 'v3',
            'hasCORS': False,
            'hasFetchOHLCV': True,
            'timeframes': {
                '1m': '001',
                '5m': '005',
                '15m': '015',
                '30m': '030',
                '1h': '060',
                '1d': '100',
                '1w': '200',
                '1M': '300',
                '1y': '400',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766569-15aa7b9a-5edd-11e7-9e7f-44791f4ee49c.jpg',
                'api': 'http://api.huobi.com',
                'www': 'https://www.huobi.com',
                'doc': 'https://github.com/huobiapi/API_Docs_en/wiki',
            },
            'api': {
                'staticmarket': {
                    'get': [
                        '{id}_kline_{period}',
                        'ticker_{id}',
                        'depth_{id}',
                        'depth_{id}_{length}',
                        'detail_{id}',
                    ],
                },
                'usdmarket': {
                    'get': [
                        '{id}_kline_{period}',
                        'ticker_{id}',
                        'depth_{id}',
                        'depth_{id}_{length}',
                        'detail_{id}',
                    ],
                },
                'trade': {
                    'post': [
                        'get_account_info',
                        'get_orders',
                        'order_info',
                        'buy',
                        'sell',
                        'buy_market',
                        'sell_market',
                        'cancel_order',
                        'get_new_deal_orders',
                        'get_order_id_by_trade_id',
                        'withdraw_coin',
                        'cancel_withdraw_coin',
                        'get_withdraw_coin_result',
                        'transfer',
                        'loan',
                        'repayment',
                        'get_loan_available',
                        'get_loans',
                    ],
                },
            },
            'markets': {
                'BTC/CNY': {'id': 'btc', 'symbol': 'BTC/CNY', 'base': 'BTC', 'quote': 'CNY', 'type': 'staticmarket', 'coinType': 1},
                'LTC/CNY': {'id': 'ltc', 'symbol': 'LTC/CNY', 'base': 'LTC', 'quote': 'CNY', 'type': 'staticmarket', 'coinType': 2},
                # 'BTC/USD': {'id': 'btc', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD', 'type': 'usdmarket',    'coinType': 1},
            },
        }
        params.update(config)
        super(huobi, self).__init__(params)

    def fetch_balance(self, params={}):
        balances = self.tradePostGetAccountInfo()
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = self.account()
            available = 'available_' + lowercase + '_display'
            frozen = 'frozen_' + lowercase + '_display'
            loan = 'loan_' + lowercase + '_display'
            if available in balances:
                account['free'] = float(balances[available])
            if frozen in balances:
                account['used'] = float(balances[frozen])
            if loan in balances:
                account['used'] = self.sum(account['used'], float(balances[loan]))
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        method = market['type'] + 'GetDepthId'
        orderbook = getattr(self, method)(self.extend({'id': market['id']}, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        market = self.market(symbol)
        method = market['type'] + 'GetTickerId'
        response = getattr(self, method)(self.extend({
            'id': market['id'],
        }, params))
        ticker = response['ticker']
        timestamp = int(response['time']) * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': None,
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['vol']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['ts']
        return {
            'info': trade,
            'id': str(trade['id']),
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['direction'],
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        method = market['type'] + 'GetDetailId'
        response = getattr(self, method)(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_trades(response['trades'], market)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        # not implemented yet
        return [
            ohlcv[0],
            ohlcv[1],
            ohlcv[2],
            ohlcv[3],
            ohlcv[4],
            ohlcv[6],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        market = self.market(symbol)
        method = market['type'] + 'GetIdKlinePeriod'
        ohlcvs = getattr(self, method)(self.extend({
            'id': market['id'],
            'period': self.timeframes[timeframe],
        }, params))
        return ohlcvs
        # return self.parse_ohlcvs(ohlcvs, market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        market = self.market(symbol)
        method = 'tradePost' + self.capitalize(side)
        order = {
            'coin_type': market['coinType'],
            'amount': amount,
            'market': market['quote'].lower(),
        }
        if type == 'limit':
            order['price'] = price
        else:
            method += self.capitalize(type)
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.tradePostCancelOrder({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api']
        if api == 'trade':
            url += '/api' + self.version
            query = self.keysort(self.extend({
                'method': path,
                'access_key': self.apiKey,
                'created': self.nonce(),
            }, params))
            queryString = self.urlencode(self.omit(query, 'market'))
            # secret key must be appended to the query before signing
            queryString += '&secret_key=' + self.secret
            query['sign'] = self.hash(self.encode(queryString))
            body = self.urlencode(query)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        else:
            url += '/' + api + '/' + self.implode_params(path, params) + '_json.js'
            query = self.omit(params, self.extract_params(path))
            if query:
                url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='trade', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] == 'error':
                raise ExchangeError(self.id + ' ' + self.json(response))
        if 'code' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class independentreserve (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'independentreserve',
            'name': 'Independent Reserve',
            'countries': ['AU', 'NZ'],  # Australia, New Zealand
            'rateLimit': 1000,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30521662-cf3f477c-9bcb-11e7-89bc-d1ac85012eda.jpg',
                'api': {
                    'public': 'https://api.independentreserve.com/Public',
                    'private': 'https://api.independentreserve.com/Private',
                },
                'www': 'https://www.independentreserve.com',
                'doc': 'https://www.independentreserve.com/API',
            },
            'api': {
                'public': {
                    'get': [
                        'GetValidPrimaryCurrencyCodes',
                        'GetValidSecondaryCurrencyCodes',
                        'GetValidLimitOrderTypes',
                        'GetValidMarketOrderTypes',
                        'GetValidOrderTypes',
                        'GetValidTransactionTypes',
                        'GetMarketSummary',
                        'GetOrderBook',
                        'GetTradeHistorySummary',
                        'GetRecentTrades',
                        'GetFxRates',
                    ],
                },
                'private': {
                    'post': [
                        'PlaceLimitOrder',
                        'PlaceMarketOrder',
                        'CancelOrder',
                        'GetOpenOrders',
                        'GetClosedOrders',
                        'GetClosedFilledOrders',
                        'GetOrderDetails',
                        'GetAccounts',
                        'GetTransactions',
                        'GetDigitalCurrencyDepositAddress',
                        'GetDigitalCurrencyDepositAddresses',
                        'SynchDigitalCurrencyDepositAddressWithBlockchain',
                        'WithdrawDigitalCurrency',
                        'RequestFiatWithdrawal',
                        'GetTrades',
                    ],
                },
            },
        }
        params.update(config)
        super(independentreserve, self).__init__(params)

    def fetch_markets(self):
        baseCurrencies = self.publicGetValidPrimaryCurrencyCodes()
        quoteCurrencies = self.publicGetValidSecondaryCurrencyCodes()
        result = []
        for i in range(0, len(baseCurrencies)):
            baseId = baseCurrencies[i]
            baseIdUppercase = baseId.upper()
            base = self.common_currency_code(baseIdUppercase)
            for j in range(0, len(quoteCurrencies)):
                quoteId = quoteCurrencies[j]
                quoteIdUppercase = quoteId.upper()
                quote = self.common_currency_code(quoteIdUppercase)
                id = baseId + '/' + quoteId
                symbol = base + '/' + quote
                result.append({
                    'id': id,
                    'symbol': symbol,
                    'base': base,
                    'quote': quote,
                    'baseId': baseId,
                    'quoteId': quoteId,
                    'info': id,
                })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privatePostGetAccounts()
        result = {'info': balances}
        for i in range(0, len(balances)):
            balance = balances[i]
            currencyCode = balance['CurrencyCode']
            uppercase = currencyCode.upper()
            currency = self.common_currency_code(uppercase)
            account = self.account()
            account['free'] = balance['AvailableBalance']
            account['total'] = balance['TotalBalance']
            account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetOrderBook(self.extend({
            'primaryCurrencyCode': market['baseId'],
            'secondaryCurrencyCode': market['quoteId'],
        }, params))
        timestamp = self.parse8601(response['CreatedTimestampUtc'])
        return self.parse_order_book(response, timestamp, 'BuyOrders', 'SellOrders', 'Price', 'Volume')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.parse8601(ticker['CreatedTimestampUtc'])
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': ticker['DayHighestPrice'],
            'low': ticker['DayLowestPrice'],
            'bid': ticker['CurrentHighestBidPrice'],
            'ask': ticker['CurrentLowestOfferPrice'],
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': ticker['LastPrice'],
            'change': None,
            'percentage': None,
            'average': ticker['DayAvgPrice'],
            'baseVolume': ticker['DayVolumeXbtInSecondaryCurrrency'],
            'quoteVolume': ticker['DayVolumeXbt'],
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketSummary(self.extend({
            'primaryCurrencyCode': market['baseId'],
            'secondaryCurrencyCode': market['quoteId'],
        }, params))
        return self.parse_ticker(response, market)

    def parse_trade(self, trade, market):
        timestamp = self.parse8601(trade['TradeTimestampUtc'])
        return {
            'id': None,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': None,
            'type': None,
            'side': None,
            'price': trade['SecondaryCurrencyTradePrice'],
            'amount': trade['PrimaryCurrencyAmount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetRecentTrades(self.extend({
            'primaryCurrencyCode': market['baseId'],
            'secondaryCurrencyCode': market['quoteId'],
            'numberOfRecentTradesToRetrieve': 50,  # max = 50
        }, params))
        return self.parse_trades(response['Trades'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        capitalizedOrderType = self.capitalize(type)
        method = 'Place' + capitalizedOrderType + 'Order'
        orderType = capitalizedOrderType
        orderType += 'Offer' if (side == 'sell') else 'Bid'
        order = self.ordered({
            'primaryCurrencyCode': market['baseId'],
            'secondaryCurrencyCode': market['quoteId'],
            'orderType': orderType,
        })
        if type == 'limit':
            order['price'] = price
        order['volume'] = amount
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['OrderGuid'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostCancelOrder({'orderGuid': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            nonce = self.nonce()
            auth = [
                url,
                'apiKey=' + self.apiKey,
                'nonce=' + str(nonce),
            ]
            keysorted = self.keysort(params)
            keys = list(keysorted.keys())
            for i in range(0, len(keys)):
                key = keys[i]
                auth.append(key + '=' + params[key])
            message = ','.join(auth)
            signature = self.hmac(self.encode(message), self.encode(self.secret))
            query = self.keysort(self.extend({
                'apiKey': self.apiKey,
                'nonce': nonce,
                'signature': signature,
            }, params))
            body = self.json(query)
            headers = {'Content-Type': 'application/json'}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        # todo error handling
        return response

# -----------------------------------------------------------------------------


class itbit (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'itbit',
            'name': 'itBit',
            'countries': 'US',
            'rateLimit': 2000,
            'version': 'v1',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27822159-66153620-60ad-11e7-89e7-005f6d7f3de0.jpg',
                'api': 'https://api.itbit.com',
                'www': 'https://www.itbit.com',
                'doc': [
                    'https://api.itbit.com/docs',
                    'https://www.itbit.com/api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'markets/{symbol}/ticker',
                        'markets/{symbol}/order_book',
                        'markets/{symbol}/trades',
                    ],
                },
                'private': {
                    'get': [
                        'wallets',
                        'wallets/{walletId}',
                        'wallets/{walletId}/balances/{currencyCode}',
                        'wallets/{walletId}/funding_history',
                        'wallets/{walletId}/trades',
                        'wallets/{walletId}/orders/{id}',
                    ],
                    'post': [
                        'wallet_transfers',
                        'wallets',
                        'wallets/{walletId}/cryptocurrency_deposits',
                        'wallets/{walletId}/cryptocurrency_withdrawals',
                        'wallets/{walletId}/orders',
                        'wire_withdrawal',
                    ],
                    'delete': [
                        'wallets/{walletId}/orders/{id}',
                    ],
                },
            },
            'markets': {
                'BTC/USD': {'id': 'XBTUSD', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'BTC/SGD': {'id': 'XBTSGD', 'symbol': 'BTC/SGD', 'base': 'BTC', 'quote': 'SGD'},
                'BTC/EUR': {'id': 'XBTEUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
            },
        }
        params.update(config)
        super(itbit, self).__init__(params)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetMarketsSymbolOrderBook(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetMarketsSymbolTicker(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        serverTimeUTC = ('serverTimeUTC' in list(ticker.keys()))
        if not serverTimeUTC:
            raise ExchangeError(self.id + ' fetchTicker returned a bad response: ' + self.json(ticker))
        timestamp = self.parse8601(ticker['serverTimeUTC'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high24h']),
            'low': float(ticker['low24h']),
            'bid': self.safe_float(ticker, 'bid'),
            'ask': self.safe_float(ticker, 'ask'),
            'vwap': float(ticker['vwap24h']),
            'open': float(ticker['openToday']),
            'close': None,
            'first': None,
            'last': float(ticker['lastPrice']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume24h']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = self.parse8601(trade['timestamp'])
        id = str(trade['matchNumber'])
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': id,
            'order': id,
            'type': None,
            'side': None,
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetMarketsSymbolTrades(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response['recentTrades'], market)

    def fetch_balance(self, params={}):
        response = self.privateGetBalances()
        balances = response['balances']
        result = {'info': response}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            account = {
                'free': float(balance['availableBalance']),
                'used': 0.0,
                'total': float(balance['totalBalance']),
            }
            account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def fetchWallets(self):
        return self.privateGetWallets()

    def nonce(self):
        return self.milliseconds()

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        walletIdInParams = ('walletId' in list(params.keys()))
        if not walletIdInParams:
            raise ExchangeError(self.id + ' createOrder requires a walletId parameter')
        amount = str(amount)
        price = str(price)
        market = self.market(symbol)
        order = {
            'side': side,
            'type': type,
            'currency': market['base'],
            'amount': amount,
            'display': amount,
            'price': price,
            'instrument': market['id'],
        }
        response = self.privatePostTradeAdd(self.extend(order, params))
        return {
            'info': response,
            'id': response['id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        walletIdInParams = ('walletId' in list(params.keys()))
        if not walletIdInParams:
            raise ExchangeError(self.id + ' cancelOrder requires a walletId parameter')
        return self.privateDeleteWalletsWalletIdOrdersId(self.extend({
            'id': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            if query:
                body = self.json(query)
            else:
                body = ''
            nonce = str(self.nonce())
            timestamp = nonce
            auth = [method, url, body, nonce, timestamp]
            message = nonce + self.json(auth)
            hash = self.hash(self.encode(message), 'sha256', 'binary')
            binhash = self.binary_concat(url, hash)
            signature = self.hmac(binhash, self.encode(self.secret), hashlib.sha512, 'base64')
            headers = {
                'Authorization': self.apiKey + ':' + signature,
                'Content-Type': 'application/json',
                'X-Auth-Timestamp': timestamp,
                'X-Auth-Nonce': nonce,
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'code' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class jubi (asia):

    def __init__(self, config={}):
        params = {
            'id': 'jubi',
            'name': 'jubi.com',
            'countries': 'CN',
            'rateLimit': 1500,
            'version': 'v1',
            'hasCORS': False,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766581-9d397d9a-5edd-11e7-8fb9-5d8236c0e692.jpg',
                'api': 'https://www.jubi.com/api',
                'www': 'https://www.jubi.com',
                'doc': 'https://www.jubi.com/help/api.html',
            },
        }
        params.update(config)
        super(jubi, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetAllticker()
        keys = list(markets.keys())
        result = []
        for p in range(0, len(keys)):
            id = keys[p]
            base = id.upper()
            quote = 'CNY'  # todo
            symbol = base + '/' + quote
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': id,
            })
        return result

# -----------------------------------------------------------------------------


class kraken (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'kraken',
            'name': 'Kraken',
            'countries': 'US',
            'version': '0',
            'rateLimit': 3000,
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasFetchOHLCV': True,
            'hasFetchOrder': True,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'hasFetchMyTrades': True,
            'hasWithdraw': True,
            'marketsByAltname': {},
            'timeframes': {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '4h': '240',
                '1d': '1440',
                '1w': '10080',
                '2w': '21600',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766599-22709304-5ede-11e7-9de1-9f33732e1509.jpg',
                'api': 'https://api.kraken.com',
                'www': 'https://www.kraken.com',
                'doc': [
                    'https://www.kraken.com/en-us/help/api',
                    'https://github.com/nothingisdead/npm-kraken-api',
                ],
                'fees': 'https://www.kraken.com/en-us/help/fees',
            },
            'api': {
                'public': {
                    'get': [
                        'Assets',
                        'AssetPairs',
                        'Depth',
                        'OHLC',
                        'Spread',
                        'Ticker',
                        'Time',
                        'Trades',
                    ],
                },
                'private': {
                    'post': [
                        'AddOrder',
                        'Balance',
                        'CancelOrder',
                        'ClosedOrders',
                        'DepositAddresses',
                        'DepositMethods',
                        'DepositStatus',
                        'Ledgers',
                        'OpenOrders',
                        'OpenPositions',
                        'QueryLedgers',
                        'QueryOrders',
                        'QueryTrades',
                        'TradeBalance',
                        'TradesHistory',
                        'TradeVolume',
                        'Withdraw',
                        'WithdrawCancel',
                        'WithdrawInfo',
                        'WithdrawStatus',
                    ],
                },
            },
        }
        params.update(config)
        super(kraken, self).__init__(params)

    def cost_to_precision(self, symbol, cost):
        return self.truncate(float(cost), self.markets[symbol]['precision']['price'])

    def fee_to_precision(self, symbol, fee):
        return self.truncate(float(fee), self.markets[symbol]['precision']['amount'])

    def fetch_markets(self):
        markets = self.publicGetAssetPairs()
        keys = list(markets['result'].keys())
        result = []
        for p in range(0, len(keys)):
            id = keys[p]
            market = markets['result'][id]
            base = market['base']
            quote = market['quote']
            if (base[0] == 'X') or (base[0] == 'Z'):
                base = base[1:]
            if (quote[0] == 'X') or (quote[0] == 'Z'):
                quote = quote[1:]
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            darkpool = id.find('.d') >= 0
            symbol = market['altname'] if darkpool else(base + '/' + quote)
            maker = None
            if 'fees_maker' in market:
                maker = float(market['fees_maker'][0][1]) / 100
            precision = {
                'amount': market['lot_decimals'],
                'price': market['pair_decimals'],
            }
            amountLimits = {
                'min': math.pow(10, -precision['amount']),
                'max': math.pow(10, precision['amount']),
            }
            priceLimits = {
                'min': math.pow(10, -precision['price']),
                'max': None,
            }
            costLimits = {
                'min': 0,
                'max': None,
            }
            limits = {
                'amount': amountLimits,
                'price': priceLimits,
                'cost': costLimits,
            }
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'darkpool': darkpool,
                'info': market,
                'altname': market['altname'],
                'maker': maker,
                'taker': float(market['fees'][0][1]) / 100,
                'lot': amountLimits['min'],
                'active': True,
                'precision': precision,
                'limits': limits,
            })
        result = self.appendInactiveMarkets(result)
        self.marketsByAltname = self.index_by(result, 'altname')
        return result

    def appendInactiveMarkets(self, result=[]):
        precision = {'amount': 8, 'price': 8}
        costLimits = {'min': 0, 'max': None}
        priceLimits = {'min': math.pow(10, -precision['price']), 'max': None}
        amountLimits = {'min': math.pow(10, -precision['amount']), 'max': math.pow(10, precision['amount'])}
        limits = {'amount': amountLimits, 'price': priceLimits, 'cost': costLimits}
        defaults = {
            'darkpool': False,
            'info': None,
            'maker': None,
            'taker': None,
            'lot': amountLimits['min'],
            'active': False,
            'precision': precision,
            'limits': limits,
        }
        markets = [
            {'id': 'XXLMZEUR', 'symbol': 'XLM/EUR', 'base': 'XLM', 'quote': 'EUR', 'altname': 'XLMEUR'},
        ]
        for i in range(0, len(markets)):
            result.append(self.extend(defaults, markets[i]))
        return result

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        darkpool = symbol.find('.d') >= 0
        if darkpool:
            raise ExchangeError(self.id + ' does not provide an order book for darkpool symbol ' + symbol)
        market = self.market(symbol)
        response = self.publicGetDepth(self.extend({
            'pair': market['id'],
        }, params))
        orderbook = response['result'][market['id']]
        return self.parse_order_book(orderbook)

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['h'][1]),
            'low': float(ticker['l'][1]),
            'bid': float(ticker['b'][0]),
            'ask': float(ticker['a'][0]),
            'vwap': float(ticker['p'][1]),
            'open': float(ticker['o']),
            'close': None,
            'first': None,
            'last': float(ticker['c'][0]),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['v'][1]),
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        pairs = []
        for s in range(0, len(self.symbols)):
            symbol = self.symbols[s]
            market = self.markets[symbol]
            if market['active']:
                if not market['darkpool']:
                    pairs.append(market['id'])
        filter = ','.join(pairs)
        response = self.publicGetTicker(self.extend({
            'pair': filter,
        }, params))
        tickers = response['result']
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        darkpool = symbol.find('.d') >= 0
        if darkpool:
            raise ExchangeError(self.id + ' does not provide a ticker for darkpool symbol ' + symbol)
        market = self.market(symbol)
        response = self.publicGetTicker(self.extend({
            'pair': market['id'],
        }, params))
        ticker = response['result'][market['id']]
        return self.parse_ticker(ticker, market)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv[0] * 1000,
            float(ohlcv[1]),
            float(ohlcv[2]),
            float(ohlcv[3]),
            float(ohlcv[4]),
            float(ohlcv[6]),
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
            'interval': self.timeframes[timeframe],
        }
        if since:
            request['since'] = int(since / 1000)
        response = self.publicGetOHLC(self.extend(request, params))
        ohlcvs = response['result'][market['id']]
        return self.parse_ohlcvs(ohlcvs, market, timeframe, since, limit)

    def parse_trade(self, trade, market=None):
        timestamp = None
        side = None
        type = None
        price = None
        amount = None
        id = None
        order = None
        if not market:
            market = self.findMarketByAltnameOrId(trade['pair'])
        if 'ordertxid' in trade:
            order = trade['ordertxid']
            id = trade['id']
            timestamp = int(trade['time'] * 1000)
            side = trade['type']
            type = trade['ordertype']
            price = float(trade['price'])
            amount = float(trade['vol'])
        else:
            timestamp = int(trade[2] * 1000)
            side = 'sell' if (trade[3] == 's') else 'buy'
            type = 'limit' if (trade[4] == 'l') else 'market'
            price = float(trade[0])
            amount = float(trade[1])
        symbol = market['symbol'] if (market) else None
        return {
            'id': id,
            'order': order,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'amount': amount,
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        id = market['id']
        response = self.publicGetTrades(self.extend({
            'pair': id,
        }, params))
        trades = response['result'][id]
        return self.parse_trades(trades, market)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostBalance()
        balances = response['result']
        result = {'info': balances}
        currencies = list(balances.keys())
        for c in range(0, len(currencies)):
            currency = currencies[c]
            code = currency
            # X-ISO4217-A3 standard currency codes
            if code[0] == 'X':
                code = code[1:]
            elif code[0] == 'Z':
                code = code[1:]
            code = self.common_currency_code(code)
            balance = float(balances[currency])
            account = {
                'free': balance,
                'used': 0.0,
                'total': balance,
            }
            result[code] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        order = {
            'pair': market['id'],
            'type': side,
            'ordertype': type,
            'volume': self.amount_to_precision(symbol, amount),
        }
        if type == 'limit':
            order['price'] = self.price_to_precision(symbol, price)
        response = self.privatePostAddOrder(self.extend(order, params))
        length = len(response['result']['txid'])
        id = response['result']['txid'] if (length > 1) else response['result']['txid'][0]
        return {
            'info': response,
            'id': id,
        }

    def findMarketByAltnameOrId(self, id):
        result = None
        if id in self.marketsByAltname:
            result = self.marketsByAltname[id]
        elif id in self.markets_by_id:
            result = self.markets_by_id[id]
        return result

    def parse_order(self, order, market=None):
        description = order['descr']
        side = description['type']
        type = description['ordertype']
        symbol = None
        if not market:
            market = self.findMarketByAltnameOrId(description['pair'])
        timestamp = int(order['opentm'] * 1000)
        amount = float(order['vol'])
        filled = float(order['vol_exec'])
        remaining = amount - filled
        fee = None
        cost = self.safe_float(order, 'cost')
        price = self.safe_float(description, 'price')
        if not price:
            price = self.safe_float(order, 'price')
        if market:
            symbol = market['symbol']
            if 'fee' in order:
                flags = order['oflags']
                feeCost = self.safe_float(order, 'fee')
                fee = {
                    'cost': feeCost,
                    'rate': None,
                }
                if flags.find('fciq') >= 0:
                    fee['currency'] = market['quote']
                elif flags.find('fcib') >= 0:
                    fee['currency'] = market['base']
        return {
            'id': order['id'],
            'info': order,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': order['status'],
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'fee': fee,
            # 'trades': self.parse_trades(order['trades'], market),
        }

    def parse_orders(self, orders, market=None):
        result = []
        ids = list(orders.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            order = self.extend({'id': id}, orders[id])
            result.append(self.parse_order(order, market))
        return result

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostQueryOrders(self.extend({
            'trades': True,  # whether or not to include trades in output(optional, default False)
            'txid': id,  # comma delimited list of transaction ids to query info about(20 maximum)
            # 'userref': 'optional',  # restrict results to given user reference id(optional)
        }, params))
        orders = response['result']
        order = self.parse_order(self.extend({'id': id}, orders[id]))
        return self.extend({'info': response}, order)

    def fetch_my_trades(self, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostTradesHistory(self.extend({
            # 'type': 'all',  # any position, closed position, closing position, no position
            # 'trades': False,  # whether or not to include trades related to position in output
            # 'start': 1234567890,  # starting unix timestamp or trade tx id of results(exclusive)
            # 'end': 1234567890,  # ending unix timestamp or trade tx id of results(inclusive)
            # 'ofs' = result offset
        }, params))
        trades = response['result']['trades']
        ids = list(trades.keys())
        for i in range(0, len(ids)):
            trades[ids[i]]['id'] = ids[i]
        return self.parse_trades(trades)

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = None
        try:
            response = self.privatePostCancelOrder(self.extend({
                'txid': id,
            }, params))
        except Exception as e:
            if self.last_json_response:
                message = self.safe_string(self.last_json_response, 'error')
                if message.find('EOrder:Unknown order') >= 0:
                    raise OrderNotFound(self.id + ' cancelOrder() error: ' + self.last_http_response)
            raise e
        return response

    def withdraw(self, currency, amount, address, params={}):
        if 'key' in params:
            self.load_markets()
            response = self.privatePostWithdraw(self.extend({
                'asset': currency,
                'amount': amount,
                # 'address': address,  # they don't allow withdrawals to direct addresses
            }, params))
            return {
                'info': response,
                'id': response['result'],
            }
        raise ExchangeError(self.id + " withdraw requires a 'key' parameter(withdrawal key name, as set up on your account)")

    def fetch_open_orders(self, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostOpenOrders(params)
        orders = self.parse_orders(response['result']['open'])
        return self.filter_orders_by_symbol(orders, symbol)

    def fetchClosedOrders(self, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostClosedOrders(params)
        orders = self.parse_orders(response['result']['closed'])
        return self.filter_orders_by_symbol(orders, symbol)

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = '/' + self.version + '/' + api + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            nonce = str(self.nonce())
            body = self.urlencode(self.extend({'nonce': nonce}, params))
            auth = self.encode(nonce + body)
            hash = self.hash(auth, 'sha256', 'binary')
            binary = self.encode(url)
            binhash = self.binary_concat(binary, hash)
            secret = base64.b64decode(self.secret)
            signature = self.hmac(binhash, secret, hashlib.sha512, 'base64')
            headers = {
                'API-Key': self.apiKey,
                'API-Sign': self.decode(signature),
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        url = self.urls['api'] + url
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            numErrors = len(response['error'])
            if numErrors:
                for i in range(0, len(response['error'])):
                    if response['error'][i] == 'EService:Unavailable':
                        raise ExchangeNotAvailable(self.id + ' ' + self.json(response))
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class kuna (acx):

    def __init__(self, config={}):
        params = {
            'id': 'kuna',
            'name': 'Kuna',
            'countries': 'UA',
            'rateLimit': 1000,
            'version': 'v2',
            'hasCORS': False,
            'hasFetchTickers': False,
            'hasFetchOHLCV': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/31697638-912824fa-b3c1-11e7-8c36-cf9606eb94ac.jpg',
                'api': 'https://kuna.io',
                'www': 'https://kuna.io',
                'doc': 'https://kuna.io/documents/api',
            },
            'api': {
                'public': {
                    'get': [
                        'tickers/{market}',
                        'order_book',
                        'order_book/{market}',
                        'trades',
                        'trades/{market}',
                        'timestamp',
                    ],
                },
                'private': {
                    'get': [
                        'members/me',
                        'orders',
                        'trades/my',
                    ],
                    'post': [
                        'orders',
                        'order/delete',
                    ],
                },
            },
            'markets': {
                'BTC/UAH': {'id': 'btcuah', 'symbol': 'BTC/UAH', 'base': 'BTC', 'quote': 'UAH', 'precision': {'amount': 6, 'price': 0}, 'lot': 0.000001, 'limits': {'amount': {'min': 0.000001, 'max': None}, 'price': {'min': 1, 'max': None}}},
                'ETH/UAH': {'id': 'ethuah', 'symbol': 'ETH/UAH', 'base': 'ETH', 'quote': 'UAH', 'precision': {'amount': 6, 'price': 0}, 'lot': 0.000001, 'limits': {'amount': {'min': 0.000001, 'max': None}, 'price': {'min': 1, 'max': None}}},
                'GBG/UAH': {'id': 'gbguah', 'symbol': 'GBG/UAH', 'base': 'GBG', 'quote': 'UAH', 'precision': {'amount': 3, 'price': 2}, 'lot': 0.001, 'limits': {'amount': {'min': 0.000001, 'max': None}, 'price': {'min': 0.01, 'max': None}}},  # Golos Gold (GBG != GOLOS)
                'KUN/BTC': {'id': 'kunbtc', 'symbol': 'KUN/BTC', 'base': 'KUN', 'quote': 'BTC', 'precision': {'amount': 6, 'price': 6}, 'lot': 0.000001, 'limits': {'amount': {'min': 0.000001, 'max': None}, 'price': {'min': 0.000001, 'max': None}}},
                'BCH/BTC': {'id': 'bchbtc', 'symbol': 'BCH/BTC', 'base': 'BCH', 'quote': 'BTC', 'precision': {'amount': 6, 'price': 6}, 'lot': 0.000001, 'limits': {'amount': {'min': 0.000001, 'max': None}, 'price': {'min': 0.000001, 'max': None}}},
                'WAVES/UAH': {'id': 'wavesuah', 'symbol': 'WAVES/UAH', 'base': 'WAVES', 'quote': 'UAH', 'precision': {'amount': 6, 'price': 0}, 'lot': 0.000001, 'limits': {'amount': {'min': 0.000001, 'max': None}, 'price': {'min': 1, 'max': None}}},
            },
            'fees': {
                'trading': {
                    'taker': 0.2 / 100,
                    'maker': 0.2 / 100,
                },
            },
        }
        params.update(config)
        super(kuna, self).__init__(params)

    def handle_errors(self, code, reason, url, method, headers, body):
        if code == 400:
            data = json.loads(body)
            error = data['error']
            errorMessage = error['message']
            if errorMessage.includes('cannot lock funds'):
                raise InsufficientFunds(' '.join([self.id, method, url, code, reason, body]))

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderBook = self.publicGetOrderBook(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_order_book(orderBook, None, 'bids', 'asks', 'price', 'volume')

    def parse_order(self, order, market):
        symbol = market['symbol']
        timestamp = self.parse8601(order['created_at'])
        return {
            'id': order['id'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': 'open',
            'symbol': symbol,
            'type': order['ord_type'],
            'side': order['side'],
            'price': float(order['price']),
            'amount': float(order['volume']),
            'filled': float(order['executed_volume']),
            'remaining': float(order['remaining_volume']),
            'trades': None,
            'fee': None,
            'info': order,
        }

    def fetch_open_orders(self, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOpenOrders requires a symbol argument')
        market = self.market(symbol)
        orders = self.privateGetOrders(self.extend({
            'market': market['id'],
        }, params))
        # todo emulation of fetchClosedOrders, fetchOrders, fetchOrder
        # with order cache + fetchOpenOrders
        # as in BTC-e, Liqui, Yobit, DSX, Tidex, WEX
        return self.parse_orders(orders, market)

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(trade['created_at'])
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'id': trade['id'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': None,
            'side': None,
            'price': float(trade['price']),
            'amount': float(trade['volume']),
            'info': trade,
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_trades(response, market)

# -----------------------------------------------------------------------------


class lakebtc (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'lakebtc',
            'name': 'LakeBTC',
            'countries': 'US',
            'version': 'api_v2',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28074120-72b7c38a-6660-11e7-92d9-d9027502281d.jpg',
                'api': 'https://api.lakebtc.com',
                'www': 'https://www.lakebtc.com',
                'doc': [
                    'https://www.lakebtc.com/s/api_v2',
                    'https://www.lakebtc.com/s/api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'bcorderbook',
                        'bctrades',
                        'ticker',
                    ],
                },
                'private': {
                    'post': [
                        'buyOrder',
                        'cancelOrders',
                        'getAccountInfo',
                        'getExternalAccounts',
                        'getOrders',
                        'getTrades',
                        'openOrders',
                        'sellOrder',
                    ],
                },
            },
        }
        params.update(config)
        super(lakebtc, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetTicker()
        result = []
        keys = list(markets.keys())
        for k in range(0, len(keys)):
            id = keys[k]
            market = markets[id]
            base = id[0:3]
            quote = id[3:6]
            base = base.upper()
            quote = quote.upper()
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetAccountInfo()
        balances = response['balance']
        result = {'info': response}
        currencies = list(balances.keys())
        for c in range(0, len(currencies)):
            currency = currencies[c]
            balance = float(balances[currency])
            account = {
                'free': balance,
                'used': 0.0,
                'total': balance,
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetBcorderbook(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        tickers = self.publicGetTicker(self.extend({
            'symbol': market['id'],
        }, params))
        ticker = tickers[market['id']]
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'bid'),
            'ask': self.safe_float(ticker, 'ask'),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': self.safe_float(ticker, 'last'),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': self.safe_float(ticker, 'volume'),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': str(trade['tid']),
            'order': None,
            'type': None,
            'side': None,
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetBctrades(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, market, type, side, amount, price=None, params={}):
        self.load_markets()
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        method = 'privatePost' + self.capitalize(side) + 'Order'
        marketId = self.market_id(market)
        order = {
            'params': [price, amount, marketId],
        }
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostCancelOrder({'params': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version
        if api == 'public':
            url += '/' + path
            if params:
                url += '?' + self.urlencode(params)
        else:
            nonce = self.nonce()
            if params:
                params = ','.join(params)
            else:
                params = ''
            query = self.urlencode({
                'tonce': nonce,
                'accesskey': self.apiKey,
                'requestmethod': method.lower(),
                'id': nonce,
                'method': path,
                'params': params,
            })
            body = self.json({
                'method': path,
                'params': params,
                'id': nonce,
            })
            signature = self.hmac(self.encode(query), self.secret, hashlib.sha1, 'base64')
            headers = {
                'Json-Rpc-Tonce': nonce,
                'Authorization': "Basic " + self.apiKey + ':' + signature,
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class livecoin (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'livecoin',
            'name': 'LiveCoin',
            'countries': ['US', 'UK', 'RU'],
            'rateLimit': 1000,
            'hasCORS': False,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27980768-f22fc424-638a-11e7-89c9-6010a54ff9be.jpg',
                'api': 'https://api.livecoin.net',
                'www': 'https://www.livecoin.net',
                'doc': 'https://www.livecoin.net/api?lang=en',
            },
            'api': {
                'public': {
                    'get': [
                        'exchange/all/order_book',
                        'exchange/last_trades',
                        'exchange/maxbid_minask',
                        'exchange/order_book',
                        'exchange/restrictions',
                        'exchange/ticker',  # omit params to get all tickers at once
                        'info/coinInfo',
                    ],
                },
                'private': {
                    'get': [
                        'exchange/client_orders',
                        'exchange/order',
                        'exchange/trades',
                        'exchange/commission',
                        'exchange/commissionCommonInfo',
                        'payment/balances',
                        'payment/balance',
                        'payment/get/address',
                        'payment/history/size',
                        'payment/history/transactions',
                    ],
                    'post': [
                        'exchange/buylimit',
                        'exchange/buymarket',
                        'exchange/cancellimit',
                        'exchange/selllimit',
                        'exchange/sellmarket',
                        'payment/out/capitalist',
                        'payment/out/card',
                        'payment/out/coin',
                        'payment/out/okpay',
                        'payment/out/payeer',
                        'payment/out/perfectmoney',
                        'payment/voucher/amount',
                        'payment/voucher/make',
                        'payment/voucher/redeem',
                    ],
                },
            },
        }
        params.update(config)
        super(livecoin, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetExchangeTicker()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['symbol']
            symbol = id
            base, quote = symbol.split('/')
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privateGetPaymentBalances()
        result = {'info': balances}
        for b in range(0, len(self.currencies)):
            balance = balances[b]
            currency = balance['currency']
            account = None
            if currency in result:
                account = result[currency]
            else:
                account = self.account()
            if balance['type'] == 'total':
                account['total'] = float(balance['value'])
            if balance['type'] == 'available':
                account['free'] = float(balance['value'])
            if balance['type'] == 'trade':
                account['used'] = float(balance['value'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetExchangeOrderBook(self.extend({
            'currencyPair': self.market_id(symbol),
            'groupByPrice': 'false',
            'depth': 100,
        }, params))
        timestamp = orderbook['timestamp']
        return self.parse_order_book(orderbook, timestamp)

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['best_bid']),
            'ask': float(ticker['best_ask']),
            'vwap': float(ticker['vwap']),
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetExchangeTicker(params)
        tickers = self.index_by(response, 'symbol')
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetExchangeTicker(self.extend({
            'currencyPair': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = trade['time'] * 1000
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': str(trade['id']),
            'order': None,
            'type': None,
            'side': trade['type'].lower(),
            'price': trade['price'],
            'amount': trade['quantity'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetExchangeLastTrades(self.extend({
            'currencyPair': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        method = 'privatePostExchange' + self.capitalize(side) + type
        order = {
            'currencyPair': self.market_id(symbol),
            'quantity': amount,
        }
        if type == 'limit':
            order['price'] = price
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostExchangeCancellimit(self.extend({
            'orderId': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            query = self.urlencode(self.keysort(params))
            if method == 'GET':
                if query:
                    url += '?' + query
            else:
                if query:
                    body = query
            signature = self.hmac(self.encode(query), self.encode(self.secret), hashlib.sha256)
            headers = {
                'Api-Key': self.apiKey,
                'Sign': signature.upper(),
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'success' in response:
            if not response['success']:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class liqui (btce):

    def __init__(self, config={}):
        params = {
            'id': 'liqui',
            'name': 'Liqui',
            'countries': 'UA',
            'rateLimit': 2500,
            'version': '3',
            'hasCORS': False,
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'hasFetchTickers': True,
            'hasFetchMyTrades': True,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27982022-75aea828-63a0-11e7-9511-ca584a8edd74.jpg',
                'api': {
                    'public': 'https://api.liqui.io/api',
                    'private': 'https://api.liqui.io/tapi',
                },
                'www': 'https://liqui.io',
                'doc': 'https://liqui.io/api',
                'fees': 'https://liqui.io/fee',
            },
            'api': {
                'public': {
                    'get': [
                        'info',
                        'ticker/{pair}',
                        'depth/{pair}',
                        'trades/{pair}',
                    ],
                },
                'private': {
                    'post': [
                        'getInfo',
                        'Trade',
                        'ActiveOrders',
                        'OrderInfo',
                        'CancelOrder',
                        'TradeHistory',
                        'TransHistory',
                        'CoinDepositAddress',
                        'WithdrawCoin',
                        'CreateCoupon',
                        'RedeemCoupon',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.001,
                    'taker': 0.0025,
                },
                'funding': 0.0,
            },
        }
        params.update(config)
        super(liqui, self).__init__(params)

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        response = self.privatePostWithdrawCoin(self.extend({
            'coinName': currency,
            'amount': float(amount),
            'address': address,
        }, params))
        return {
            'info': response,
            'id': response['return']['tId'],
        }

# -----------------------------------------------------------------------------


class luno (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'luno',
            'name': 'luno',
            'countries': ['GB', 'SG', 'ZA'],
            'rateLimit': 3000,
            'version': '1',
            'hasCORS': False,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766607-8c1a69d8-5ede-11e7-930c-540b5eb9be24.jpg',
                'api': 'https://api.mybitx.com/api',
                'www': 'https://www.luno.com',
                'doc': [
                    'https://www.luno.com/en/api',
                    'https://npmjs.org/package/bitx',
                    'https://github.com/bausmeier/node-bitx',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'orderbook',
                        'ticker',
                        'tickers',
                        'trades',
                    ],
                },
                'private': {
                    'get': [
                        'accounts/{id}/pending',
                        'accounts/{id}/transactions',
                        'balance',
                        'fee_info',
                        'funding_address',
                        'listorders',
                        'listtrades',
                        'orders/{id}',
                        'quotes/{id}',
                        'withdrawals',
                        'withdrawals/{id}',
                    ],
                    'post': [
                        'accounts',
                        'postorder',
                        'marketorder',
                        'stoporder',
                        'funding_address',
                        'withdrawals',
                        'send',
                        'quotes',
                        'oauth2/grant',
                    ],
                    'put': [
                        'quotes/{id}',
                    ],
                    'delete': [
                        'quotes/{id}',
                        'withdrawals/{id}',
                    ],
                },
            },
        }
        params.update(config)
        super(luno, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetTickers()
        result = []
        for p in range(0, len(markets['tickers'])):
            market = markets['tickers'][p]
            id = market['pair']
            base = id[0:3]
            quote = id[3:6]
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalance()
        balances = response['balance']
        result = {'info': response}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = self.common_currency_code(balance['asset'])
            reserved = float(balance['reserved'])
            unconfirmed = float(balance['unconfirmed'])
            account = {
                'free': float(balance['balance']),
                'used': self.sum(reserved, unconfirmed),
                'total': 0.0,
            }
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetOrderbook(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = orderbook['timestamp']
        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'volume')

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['timestamp']
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last_trade']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['rolling_24_hour_volume']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetTickers(params)
        tickers = self.index_by(response['tickers'], 'pair')
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetTicker(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        side = 'buy' if (trade['is_buy']) else 'sell'
        return {
            'info': trade,
            'id': None,
            'order': None,
            'timestamp': trade['timestamp'],
            'datetime': self.iso8601(trade['timestamp']),
            'symbol': market['symbol'],
            'type': None,
            'side': side,
            'price': float(trade['price']),
            'amount': float(trade['volume']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response['trades'], market)

    def create_order(self, market, type, side, amount, price=None, params={}):
        self.load_markets()
        method = 'privatePost'
        order = {'pair': self.market_id(market)}
        if type == 'market':
            method += 'Marketorder'
            order['type'] = side.upper()
            if side == 'buy':
                order['counter_volume'] = amount
            else:
                order['base_volume'] = amount
        else:
            method += 'Order'
            order['volume'] = amount
            order['price'] = price
            if side == 'buy':
                order['type'] = 'BID'
            else:
                order['type'] = 'ASK'
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['order_id'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostStoporder({'order_id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if query:
            url += '?' + self.urlencode(query)
        if api == 'private':
            auth = self.encode(self.apiKey + ':' + self.secret)
            auth = base64.b64encode(auth)
            headers = {'Authorization': 'Basic ' + self.decode(auth)}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class mercado (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'mercado',
            'name': 'Mercado Bitcoin',
            'countries': 'BR',  # Brazil
            'rateLimit': 1000,
            'version': 'v3',
            'hasCORS': True,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27837060-e7c58714-60ea-11e7-9192-f05e86adb83f.jpg',
                'api': {
                    'public': 'https://www.mercadobitcoin.net/api',
                    'private': 'https://www.mercadobitcoin.net/tapi',
                },
                'www': 'https://www.mercadobitcoin.com.br',
                'doc': [
                    'https://www.mercadobitcoin.com.br/api-doc',
                    'https://www.mercadobitcoin.com.br/trade-api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        '{coin}/orderbook/',  # last slash critical
                        '{coin}/ticker/',
                        '{coin}/trades/',
                        '{coin}/trades/{from}/',
                        '{coin}/trades/{from}/{to}',
                        '{coin}/day-summary/{year}/{month}/{day}/',
                    ],
                },
                'private': {
                    'post': [
                        'cancel_order',
                        'get_account_info',
                        'get_order',
                        'get_withdrawal',
                        'list_system_messages',
                        'list_orders',
                        'list_orderbook',
                        'place_buy_order',
                        'place_sell_order',
                        'withdraw_coin',
                    ],
                },
            },
            'markets': {
                'BTC/BRL': {'id': 'BRLBTC', 'symbol': 'BTC/BRL', 'base': 'BTC', 'quote': 'BRL', 'suffix': 'Bitcoin'},
                'LTC/BRL': {'id': 'BRLLTC', 'symbol': 'LTC/BRL', 'base': 'LTC', 'quote': 'BRL', 'suffix': 'Litecoin'},
                'BCH/BRL': {'id': 'BCHBTC', 'symbol': 'BCH/BRL', 'base': 'BCH', 'quote': 'BRL', 'suffix': 'BCash'},
            },
        }
        params.update(config)
        super(mercado, self).__init__(params)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderbook = self.publicGetCoinOrderbook(self.extend({
            'coin': market['base'],
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetCoinTicker(self.extend({
            'coin': market['base'],
        }, params))
        ticker = response['ticker']
        timestamp = int(ticker['date']) * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['vol']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': str(trade['tid']),
            'order': None,
            'type': None,
            'side': trade['type'],
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetCoinTrades(self.extend({
            'coin': market['base'],
        }, params))
        return self.parse_trades(response, market)

    def fetch_balance(self, params={}):
        response = self.privatePostGetAccountInfo()
        balances = response['balance']
        result = {'info': response}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = self.account()
            if lowercase in balances:
                account['free'] = float(balances[lowercase]['available'])
                account['total'] = float(balances[lowercase]['total'])
                account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        method = 'privatePostPlace' + self.capitalize(side) + 'Order'
        order = {
            'coin_pair': self.market_id(symbol),
            'quantity': amount,
            'limit_price': price,
        }
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['response_data']['order']['order_id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder(self.extend({
            'order_id': id,
        }, params))

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        request = {
            'coin': currency,
            'quantity': '{:.10f}'.format(amount),
            'address': address,
        }
        if currency == 'BRL':
            account_ref = ('account_ref' in list(params.keys()))
            if not account_ref:
                raise ExchangeError(self.id + ' requires account_ref parameter to withdraw ' + currency)
        elif currency != 'LTC':
            tx_fee = ('tx_fee' in list(params.keys()))
            if not tx_fee:
                raise ExchangeError(self.id + ' requires tx_fee parameter to withdraw ' + currency)
        response = self.privatePostWithdrawCoin(self.extend(request, params))
        return {
            'info': response,
            'id': response['response_data']['withdrawal']['id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/'
        if api == 'public':
            url += self.implode_params(path, params)
        else:
            url += self.version + '/'
            nonce = self.nonce()
            body = self.urlencode(self.extend({
                'tapi_method': path,
                'tapi_nonce': nonce,
            }, params))
            auth = '/tapi/' + self.version + '/' + '?' + body
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'TAPI-ID': self.apiKey,
                'TAPI-MAC': self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error_message' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class mixcoins (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'mixcoins',
            'name': 'MixCoins',
            'countries': ['GB', 'HK'],
            'rateLimit': 1500,
            'version': 'v1',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30237212-ed29303c-9535-11e7-8af8-fcd381cfa20c.jpg',
                'api': 'https://mixcoins.com/api',
                'www': 'https://mixcoins.com',
                'doc': 'https://mixcoins.com/help/api/',
            },
            'api': {
                'public': {
                    'get': [
                        'ticker',
                        'trades',
                        'depth',
                    ],
                },
                'private': {
                    'post': [
                        'cancel',
                        'info',
                        'orders',
                        'order',
                        'transactions',
                        'trade',
                    ],
                },
            },
            'markets': {
                'BTC/USD': {'id': 'btc_usd', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'ETH/BTC': {'id': 'eth_btc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
                'BCH/BTC': {'id': 'bcc_btc', 'symbol': 'BCH/BTC', 'base': 'BCH', 'quote': 'BTC'},
                'LSK/BTC': {'id': 'lsk_btc', 'symbol': 'LSK/BTC', 'base': 'LSK', 'quote': 'BTC'},
                'BCH/USD': {'id': 'bcc_usd', 'symbol': 'BCH/USD', 'base': 'BCH', 'quote': 'USD'},
                'ETH/USD': {'id': 'eth_usd', 'symbol': 'ETH/USD', 'base': 'ETH', 'quote': 'USD'},
            },
        }
        params.update(config)
        super(mixcoins, self).__init__(params)

    def fetch_balance(self, params={}):
        response = self.privatePostInfo()
        balance = response['result']['wallet']
        result = {'info': balance}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = self.account()
            if lowercase in balance:
                account['free'] = float(balance[lowercase]['avail'])
                account['used'] = float(balance[lowercase]['lock'])
                account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        response = self.publicGetDepth(self.extend({
            'market': self.market_id(symbol),
        }, params))
        return self.parse_order_book(response['result'])

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetTicker(self.extend({
            'market': self.market_id(symbol),
        }, params))
        ticker = response['result']
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['vol']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = int(trade['date']) * 1000
        return {
            'id': str(trade['id']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_trades(response['result'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        order = {
            'market': self.market_id(symbol),
            'op': side,
            'amount': amount,
        }
        if type == 'market':
            order['order_type'] = 1
            order['price'] = price
        else:
            order['order_type'] = 0
        response = self.privatePostTrade(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['result']['id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancel({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            nonce = self.nonce()
            body = self.urlencode(self.extend({
                'nonce': nonce,
            }, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': self.hmac(self.encode(body), self.secret, hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] == 200:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))

# -----------------------------------------------------------------------------


class nova (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'nova',
            'name': 'Novaexchange',
            'countries': 'TZ',  # Tanzania
            'rateLimit': 2000,
            'version': 'v2',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30518571-78ca0bca-9b8a-11e7-8840-64b83a4a94b2.jpg',
                'api': 'https://novaexchange.com/remote',
                'www': 'https://novaexchange.com',
                'doc': 'https://novaexchange.com/remote/faq',
            },
            'api': {
                'public': {
                    'get': [
                        'markets/',
                        'markets/{basecurrency}/',
                        'market/info/{pair}/',
                        'market/orderhistory/{pair}/',
                        'market/openorders/{pair}/buy/',
                        'market/openorders/{pair}/sell/',
                        'market/openorders/{pair}/both/',
                        'market/openorders/{pair}/{ordertype}/',
                    ],
                },
                'private': {
                    'post': [
                        'getbalances/',
                        'getbalance/{currency}/',
                        'getdeposits/',
                        'getwithdrawals/',
                        'getnewdepositaddress/{currency}/',
                        'getdepositaddress/{currency}/',
                        'myopenorders/',
                        'myopenorders_market/{pair}/',
                        'cancelorder/{orderid}/',
                        'withdraw/{currency}/',
                        'trade/{pair}/',
                        'tradehistory/',
                        'getdeposithistory/',
                        'getwithdrawalhistory/',
                        'walletstatus/',
                        'walletstatus/{currency}/',
                    ],
                },
            },
        }
        params.update(config)
        super(nova, self).__init__(params)

    def fetch_markets(self):
        response = self.publicGetMarkets()
        markets = response['markets']
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            if not market['disabled']:
                id = market['marketname']
                quote, base = id.split('_')
                symbol = base + '/' + quote
                result.append({
                    'id': id,
                    'symbol': symbol,
                    'base': base,
                    'quote': quote,
                    'info': market,
                })
        return result

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetMarketOpenordersPairBoth(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'buyorders', 'sellorders', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetMarketInfoPair(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        ticker = response['markets'][0]
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high24h']),
            'low': float(ticker['low24h']),
            'bid': self.safe_float(ticker, 'bid'),
            'ask': self.safe_float(ticker, 'ask'),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last_price']),
            'change': float(ticker['change24h']),
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume24h']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['unix_t_datestamp'] * 1000
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': None,
            'order': None,
            'type': None,
            'side': trade['tradetype'].lower(),
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketOrderhistoryPair(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response['items'], market)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetbalances()
        balances = response['balances']
        result = {'info': response}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            lockbox = float(balance['amount_lockbox'])
            trades = float(balance['amount_trades'])
            account = {
                'free': float(balance['amount']),
                'used': self.sum(lockbox, trades),
                'total': float(balance['amount_total']),
            }
            result[currency] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        self.load_markets()
        amount = str(amount)
        price = str(price)
        market = self.market(symbol)
        order = {
            'tradetype': side.upper(),
            'tradeamount': amount,
            'tradeprice': price,
            'tradebase': 1,
            'pair': market['id'],
        }
        response = self.privatePostTradePair(self.extend(order, params))
        return {
            'info': response,
            'id': None,
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelorder(self.extend({
            'orderid': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/'
        if api == 'private':
            url += api + '/'
        url += self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = str(self.nonce())
            url += '?' + self.urlencode({'nonce': nonce})
            signature = self.hmac(self.encode(url), self.encode(self.secret), hashlib.sha512, 'base64')
            body = self.urlencode(self.extend({
                'apikey': self.apiKey,
                'signature': signature,
            }, query))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] != 'success':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class okcoincny (okcoin):

    def __init__(self, config={}):
        params = {
            'id': 'okcoincny',
            'name': 'OKCoin CNY',
            'countries': 'CN',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766792-8be9157a-5ee5-11e7-926c-6d69b8d3378d.jpg',
                'api': {
                    'web': 'https://www.okcoin.cn',
                    'public': 'https://www.okcoin.cn/pai',
                    'private': 'https://www.okcoin.cn/api',
                },
                'www': 'https://www.okcoin.cn',
                'doc': 'https://www.okcoin.cn/rest_getStarted.html',
            },
            'markets': {
                'BTC/CNY': {'id': 'btc_cny', 'symbol': 'BTC/CNY', 'base': 'BTC', 'quote': 'CNY', 'type': 'spot', 'spot': True, 'future': False},
                'LTC/CNY': {'id': 'ltc_cny', 'symbol': 'LTC/CNY', 'base': 'LTC', 'quote': 'CNY', 'type': 'spot', 'spot': True, 'future': False},
                'ETH/CNY': {'id': 'eth_cny', 'symbol': 'ETH/CNY', 'base': 'ETH', 'quote': 'CNY', 'type': 'spot', 'spot': True, 'future': False},
                'ETC/CNY': {'id': 'etc_cny', 'symbol': 'ETC/CNY', 'base': 'ETC', 'quote': 'CNY', 'type': 'spot', 'spot': True, 'future': False},
                'BCH/CNY': {'id': 'bcc_cny', 'symbol': 'BCH/CNY', 'base': 'BCH', 'quote': 'CNY', 'type': 'spot', 'spot': True, 'future': False},
            },
        }
        params.update(config)
        super(okcoincny, self).__init__(params)

# -----------------------------------------------------------------------------


class okcoinusd (okcoin):

    def __init__(self, config={}):
        params = {
            'id': 'okcoinusd',
            'name': 'OKCoin USD',
            'countries': ['CN', 'US'],
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766791-89ffb502-5ee5-11e7-8a5b-c5950b68ac65.jpg',
                'api': {
                    'web': 'https://www.okcoin.com',
                    'public': 'https://www.okcoin.com/api',
                    'private': 'https://www.okcoin.com/api',
                },
                'www': 'https://www.okcoin.com',
                'doc': [
                    'https://www.okcoin.com/rest_getStarted.html',
                    'https://www.npmjs.com/package/okcoin.com',
                ],
            },
            'markets': {
                'BTC/USD': {'id': 'btc_usd', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD', 'type': 'spot', 'spot': True, 'future': False},
                'LTC/USD': {'id': 'ltc_usd', 'symbol': 'LTC/USD', 'base': 'LTC', 'quote': 'USD', 'type': 'spot', 'spot': True, 'future': False},
                'ETH/USD': {'id': 'eth_usd', 'symbol': 'ETH/USD', 'base': 'ETH', 'quote': 'USD', 'type': 'spot', 'spot': True, 'future': False},
                'ETC/USD': {'id': 'etc_usd', 'symbol': 'ETC/USD', 'base': 'ETC', 'quote': 'USD', 'type': 'spot', 'spot': True, 'future': False},
            },
        }
        params.update(config)
        super(okcoinusd, self).__init__(params)

# -----------------------------------------------------------------------------


class okex (okcoin):

    def __init__(self, config={}):
        params = {
            'id': 'okex',
            'name': 'OKEX',
            'countries': ['CN', 'US'],
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/29562593-9038a9bc-8742-11e7-91cc-8201f845bfc1.jpg',
                'api': {
                    'www': 'https://www.okex.com',
                    'public': 'https://www.okex.com/api',
                    'private': 'https://www.okex.com/api',
                },
                'www': 'https://www.okex.com',
                'doc': 'https://www.okex.com/rest_getStarted.html',
            },
            'markets': {
                'BTC/USD': {'id': 'btc_usd', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD', 'type': 'future', 'spot': False, 'future': True},
                'LTC/USD': {'id': 'ltc_usd', 'symbol': 'LTC/USD', 'base': 'LTC', 'quote': 'USD', 'type': 'future', 'spot': False, 'future': True},
                'LTC/BTC': {'id': 'ltc_btc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC', 'type': 'spot', 'spot': True, 'future': False},
                'ETH/BTC': {'id': 'eth_btc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC', 'type': 'spot', 'spot': True, 'future': False},
                'ETC/BTC': {'id': 'etc_btc', 'symbol': 'ETC/BTC', 'base': 'ETC', 'quote': 'BTC', 'type': 'spot', 'spot': True, 'future': False},
                'BCH/BTC': {'id': 'bcc_btc', 'symbol': 'BCH/BTC', 'base': 'BCH', 'quote': 'BTC', 'type': 'spot', 'spot': True, 'future': False},
            },
        }
        params.update(config)
        super(okex, self).__init__(params)

# -----------------------------------------------------------------------------


class paymium (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'paymium',
            'name': 'Paymium',
            'countries': ['FR', 'EU'],
            'rateLimit': 2000,
            'version': 'v1',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27790564-a945a9d4-5ff9-11e7-9d2d-b635763f2f24.jpg',
                'api': 'https://paymium.com/api',
                'www': 'https://www.paymium.com',
                'doc': [
                    'https://github.com/Paymium/api-documentation',
                    'https://www.paymium.com/page/developers',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'countries',
                        'data/{id}/ticker',
                        'data/{id}/trades',
                        'data/{id}/depth',
                        'bitcoin_charts/{id}/trades',
                        'bitcoin_charts/{id}/depth',
                    ],
                },
                'private': {
                    'get': [
                        'merchant/get_payment/{UUID}',
                        'user',
                        'user/addresses',
                        'user/addresses/{btc_address}',
                        'user/orders',
                        'user/orders/{UUID}',
                        'user/price_alerts',
                    ],
                    'post': [
                        'user/orders',
                        'user/addresses',
                        'user/payment_requests',
                        'user/price_alerts',
                        'merchant/create_payment',
                    ],
                    'delete': [
                        'user/orders/{UUID}/cancel',
                        'user/price_alerts/{id}',
                    ],
                },
            },
            'markets': {
                'BTC/EUR': {'id': 'eur', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
            },
        }
        params.update(config)
        super(paymium, self).__init__(params)

    def fetch_balance(self, params={}):
        balances = self.privateGetUser()
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = self.account()
            balance = 'balance_' + lowercase
            locked = 'locked_' + lowercase
            if balance in balances:
                account['free'] = balances[balance]
            if locked in balances:
                account['used'] = balances[locked]
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetDataIdDepth(self.extend({
            'id': self.market_id(symbol),
        }, params))
        result = self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'amount')
        result['bids'] = self.sort_by(result['bids'], 0, True)
        return result

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetDataIdTicker(self.extend({
            'id': self.market_id(symbol),
        }, params))
        timestamp = ticker['at'] * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': float(ticker['vwap']),
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['price']),
            'change': None,
            'percentage': float(ticker['variation']),
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = int(trade['created_at_int']) * 1000
        volume = 'traded_' + market['base'].lower()
        return {
            'info': trade,
            'id': trade['uuid'],
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['side'],
            'price': trade['price'],
            'amount': trade[volume],
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetDataIdTrades(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, market, type, side, amount, price=None, params={}):
        order = {
            'type': self.capitalize(type) + 'Order',
            'currency': self.market_id(market),
            'direction': side,
            'amount': amount,
        }
        if type == 'market':
            order['price'] = price
        response = self.privatePostUserOrders(self.extend(order, params))
        return {
            'info': response,
            'id': response['uuid'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder(self.extend({
            'orderNumber': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            body = self.json(params)
            nonce = str(self.nonce())
            auth = nonce + url + body
            headers = {
                'Api-Key': self.apiKey,
                'Api-Signature': self.hmac(self.encode(auth), self.secret),
                'Api-Nonce': nonce,
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'errors' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class poloniex (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'poloniex',
            'name': 'Poloniex',
            'countries': 'US',
            'rateLimit': 1000,  # up to 6 calls per second
            'hasCORS': True,
            'hasFetchMyTrades': True,
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'hasFetchTickers': True,
            'hasWithdraw': True,
            'hasFetchOHLCV': True,
            'timeframes': {
                '5m': 300,
                '15m': 900,
                '30m': 1800,
                '2h': 7200,
                '4h': 14400,
                '1d': 86400,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766817-e9456312-5ee6-11e7-9b3c-b628ca5626a5.jpg',
                'api': {
                    'public': 'https://poloniex.com/public',
                    'private': 'https://poloniex.com/tradingApi',
                },
                'www': 'https://poloniex.com',
                'doc': [
                    'https://poloniex.com/support/api/',
                    'http://pastebin.com/dMX7mZE0',
                ],
                'fees': 'https://poloniex.com/fees',
            },
            'api': {
                'public': {
                    'get': [
                        'return24hVolume',
                        'returnChartData',
                        'returnCurrencies',
                        'returnLoanOrders',
                        'returnOrderBook',
                        'returnTicker',
                        'returnTradeHistory',
                    ],
                },
                'private': {
                    'post': [
                        'buy',
                        'cancelLoanOffer',
                        'cancelOrder',
                        'closeMarginPosition',
                        'createLoanOffer',
                        'generateNewAddress',
                        'getMarginPosition',
                        'marginBuy',
                        'marginSell',
                        'moveOrder',
                        'returnActiveLoans',
                        'returnAvailableAccountBalances',
                        'returnBalances',
                        'returnCompleteBalances',
                        'returnDepositAddresses',
                        'returnDepositsWithdrawals',
                        'returnFeeInfo',
                        'returnLendingHistory',
                        'returnMarginAccountSummary',
                        'returnOpenLoanOffers',
                        'returnOpenOrders',
                        'returnOrderTrades',
                        'returnTradableBalances',
                        'returnTradeHistory',
                        'sell',
                        'toggleAutoRenew',
                        'transferBalance',
                        'withdraw',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.0015,
                    'taker': 0.0025,
                },
                'funding': 0.0,
            },
            'limits': {
                'amount': {
                    'min': 0.00000001,
                    'max': 1000000000,
                },
                'price': {
                    'min': 0.00000001,
                    'max': 1000000000,
                },
                'cost': {
                    'min': 0.00000000,
                    'max': 1000000000,
                }
            },
            'precision': {
                'amount': 8,
                'price': 8,
            },
        }
        params.update(config)
        super(poloniex, self).__init__(params)

    def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='taker', params={}):
        market = self.markets[symbol]
        key = 'quote'
        rate = market[takerOrMaker]
        cost = float(self.cost_to_precision(symbol, amount * rate))
        if side == 'sell':
            cost *= price
        else:
            key = 'base'
        return {
            'currency': market[key],
            'rate': rate,
            'cost': float(self.fee_to_precision(symbol, cost)),
        }

    def common_currency_code(self, currency):
        if currency == 'BTM':
            return 'Bitmark'
        return currency

    def parse_ohlcv(self, ohlcv, market=None, timeframe='5m', since=None, limit=None):
        return [
            ohlcv['date'] * 1000,
            ohlcv['open'],
            ohlcv['high'],
            ohlcv['low'],
            ohlcv['close'],
            ohlcv['volume'],
        ]

    def fetch_ohlcv(self, symbol, timeframe='5m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        if not since:
            since = 0
        request = {
            'currencyPair': market['id'],
            'period': self.timeframes[timeframe],
            'start': int(since / 1000),
        }
        if limit:
            request['end'] = self.sum(request['start'], limit * self.timeframes[timeframe])
        response = self.publicGetReturnChartData(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def fetch_markets(self):
        markets = self.publicGetReturnTicker()
        keys = list(markets.keys())
        result = []
        for p in range(0, len(keys)):
            id = keys[p]
            market = markets[id]
            quote, base = id.split('_')
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append(self.extend(self.fees['trading'], {
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'lot': self.limits['amount']['min'],
                'info': market,
            }))
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privatePostReturnCompleteBalances({
            'account': 'all',
        })
        result = {'info': balances}
        currencies = list(balances.keys())
        for c in range(0, len(currencies)):
            id = currencies[c]
            balance = balances[id]
            currency = self.common_currency_code(id)
            account = {
                'free': float(balance['available']),
                'used': float(balance['onOrders']),
                'total': 0.0,
            }
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetchFees(self, params={}):
        self.load_markets()
        fees = self.privatePostReturnFeeInfo()
        return {
            'info': fees,
            'maker': float(fees['makerFee']),
            'taker': float(fees['takerFee']),
            'withdraw': 0.0,
        }

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetReturnOrderBook(self.extend({
            'currencyPair': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high24hr']),
            'low': float(ticker['low24hr']),
            'bid': float(ticker['highestBid']),
            'ask': float(ticker['lowestAsk']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': float(ticker['percentChange']),
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['quoteVolume']),
            'quoteVolume': float(ticker['baseVolume']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetReturnTicker(params)
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        tickers = self.publicGetReturnTicker(params)
        ticker = tickers[market['id']]
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(trade['date'])
        symbol = None
        if (not market) and('currencyPair' in list(trade.keys())):
            market = self.markets_by_id[trade['currencyPair']]['symbol']
        if market:
            symbol = market['symbol']
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'id': self.safe_string(trade, 'tradeID'),
            'order': self.safe_string(trade, 'orderNumber'),
            'type': 'limit',
            'side': trade['type'],
            'price': float(trade['rate']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        trades = self.publicGetReturnTradeHistory(self.extend({
            'currencyPair': market['id'],
            'end': self.seconds(),  # last 50000 trades by default
        }, params))
        return self.parse_trades(trades, market)

    def fetch_my_trades(self, symbol=None, params={}):
        self.load_markets()
        market = None
        if symbol:
            market = self.market(symbol)
        pair = market['id'] if market else 'all'
        request = self.extend({
            'currencyPair': pair,
            # 'start': self.seconds() - 86400,  # last 24 hours by default
            # 'end': self.seconds(),  # last 50000 trades by default
        }, params)
        response = self.privatePostReturnTradeHistory(request)
        result = []
        if market:
            result = self.parse_trades(response, market)
        else:
            if response:
                ids = list(response.keys())
                for i in range(0, len(ids)):
                    id = ids[i]
                    market = self.markets_by_id[id]
                    symbol = market['symbol']
                    trades = self.parse_trades(response[id], market)
                    for j in range(0, len(trades)):
                        result.append(trades[j])
        return result

    def parse_order(self, order, market=None):
        timestamp = self.safe_integer(order, 'timestamp')
        if not timestamp:
            timestamp = self.parse8601(order['date'])
        trades = None
        if 'resultingTrades' in order:
            trades = self.parse_trades(order['resultingTrades'], market)
        symbol = None
        if market:
            symbol = market['symbol']
        price = float(order['price'])
        cost = self.safe_float(order, 'total', 0.0)
        remaining = self.safe_float(order, 'amount')
        amount = self.safe_float(order, 'startingAmount', remaining)
        filled = amount - remaining
        return {
            'info': order,
            'id': order['orderNumber'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': order['status'],
            'symbol': symbol,
            'type': order['type'],
            'side': order['side'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': trades,
            'fee': None,
        }

    def parseOpenOrders(self, orders, market, result=[]):
        for i in range(0, len(orders)):
            order = orders[i]
            extended = self.extend(order, {
                'status': 'open',
                'type': 'limit',
                'side': order['type'],
                'price': order['rate'],
            })
            result.append(self.parse_order(extended, market))
        return result

    def fetch_orders(self, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        pair = market['id'] if market else 'all'
        response = self.privatePostReturnOpenOrders(self.extend({
            'currencyPair': pair,
        }))
        openOrders = []
        if market:
            openOrders = self.parseOpenOrders(response, market, openOrders)
        else:
            marketIds = list(response.keys())
            for i in range(0, len(marketIds)):
                marketId = marketIds[i]
                orders = response[marketId]
                market = self.markets_by_id[marketId]
                openOrders = self.parseOpenOrders(orders, market, openOrders)
        for j in range(0, len(openOrders)):
            self.orders[openOrders[j]['id']] = openOrders[j]
        openOrdersIndexedById = self.index_by(openOrders, 'id')
        cachedOrderIds = list(self.orders.keys())
        result = []
        for k in range(0, len(cachedOrderIds)):
            id = cachedOrderIds[k]
            if id in openOrdersIndexedById:
                self.orders[id] = self.extend(self.orders[id], openOrdersIndexedById[id])
            else:
                order = self.orders[id]
                if order['status'] == 'open':
                    self.orders[id] = self.extend(order, {
                        'status': 'closed',
                        'cost': order['amount'] * order['price'],
                        'filled': order['amount'],
                        'remaining': 0.0,
                    })
            order = self.orders[id]
            if market:
                if order['symbol'] == symbol:
                    result.append(order)
            else:
                result.append(order)
        return result

    def fetch_order(self, id, symbol=None, params={}):
        orders = self.fetch_orders(symbol, params)
        for i in range(0, len(orders)):
            if orders[i]['id'] == id:
                return orders[i]
        return None

    def filterOrdersByStatus(self, orders, status):
        result = []
        for i in range(0, len(orders)):
            if orders[i]['status'] == status:
                result.append(orders[i])
        return result

    def fetch_open_orders(self, symbol=None, params={}):
        orders = self.fetch_orders(symbol, params)
        return self.filterOrdersByStatus(orders, 'open')

    def fetchClosedOrders(self, symbol=None, params={}):
        orders = self.fetch_orders(symbol, params)
        return self.filterOrdersByStatus(orders, 'closed')

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        self.load_markets()
        method = 'privatePost' + self.capitalize(side)
        market = self.market(symbol)
        price = float(price)
        amount = float(amount)
        response = getattr(self, method)(self.extend({
            'currencyPair': market['id'],
            'rate': self.price_to_precision(symbol, price),
            'amount': self.amount_to_precision(symbol, amount),
        }, params))
        timestamp = self.milliseconds()
        order = self.parse_order(self.extend({
            'timestamp': timestamp,
            'status': 'open',
            'type': type,
            'side': side,
            'price': price,
            'amount': amount,
        }, response), market)
        id = order['id']
        self.orders[id] = order
        return self.extend({'info': response}, order)

    def edit_order(self, id, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        price = float(price)
        amount = float(amount)
        request = {
            'orderNumber': id,
            'rate': self.price_to_precision(symbol, price),
            'amount': self.amount_to_precision(symbol, amount),
        }
        response = self.privatePostMoveOrder(self.extend(request, params))
        result = None
        if id in self.orders:
            self.orders[id] = self.extend(self.orders[id], {
                'price': price,
                'amount': amount,
            })
            result = self.extend(self.orders[id], {'info': response})
        else:
            result = {
                'info': response,
                'id': response['orderNumber'],
            }
        return result

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = None
        try:
            response = self.privatePostCancelOrder(self.extend({
                'orderNumber': id,
            }, params))
            if id in self.orders:
                self.orders[id]['status'] = 'canceled'
        except Exception as e:
            if self.last_json_response:
                message = self.safe_string(self.last_json_response, 'error')
                if message.find('Invalid order') >= 0:
                    raise OrderNotFound(self.id + ' cancelOrder() error: ' + self.last_http_response)
            raise e
        return response

    def fetch_order_status(self, id, symbol=None):
        self.load_markets()
        orders = self.fetch_open_orders(symbol)
        indexed = self.index_by(orders, 'id')
        return 'open' if (id in list(indexed.keys())) else 'closed'

    def fetch_order_trades(self, id, symbol=None, params={}):
        self.load_markets()
        trades = self.privatePostReturnOrderTrades(self.extend({
            'orderNumber': id,
        }, params))
        return self.parse_trades(trades)

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        result = self.privatePostWithdraw(self.extend({
            'currency': currency,
            'amount': amount,
            'address': address,
        }, params))
        return {
            'info': result,
            'id': result['response'],
        }

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        query = self.extend({'command': path}, params)
        if api == 'public':
            url += '?' + self.urlencode(query)
        else:
            query['nonce'] = self.nonce()
            body = self.urlencode(query)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            error = self.id + ' ' + self.json(response)
            failed = response['error'].find('Not enough') >= 0
            if failed:
                raise InsufficientFunds(error)
            raise ExchangeError(error)
        return response

# -----------------------------------------------------------------------------


class quadrigacx (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'quadrigacx',
            'name': 'QuadrigaCX',
            'countries': 'CA',
            'rateLimit': 1000,
            'version': 'v2',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766825-98a6d0de-5ee7-11e7-9fa4-38e11a2c6f52.jpg',
                'api': 'https://api.quadrigacx.com',
                'www': 'https://www.quadrigacx.com',
                'doc': 'https://www.quadrigacx.com/api_info',
            },
            'api': {
                'public': {
                    'get': [
                        'order_book',
                        'ticker',
                        'transactions',
                    ],
                },
                'private': {
                    'post': [
                        'balance',
                        'bitcoin_deposit_address',
                        'bitcoin_withdrawal',
                        'buy',
                        'cancel_order',
                        'ether_deposit_address',
                        'ether_withdrawal',
                        'lookup_order',
                        'open_orders',
                        'sell',
                        'user_transactions',
                    ],
                },
            },
            'markets': {
                'BTC/CAD': {'id': 'btc_cad', 'symbol': 'BTC/CAD', 'base': 'BTC', 'quote': 'CAD'},
                'BTC/USD': {'id': 'btc_usd', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'ETH/BTC': {'id': 'eth_btc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
                'ETH/CAD': {'id': 'eth_cad', 'symbol': 'ETH/CAD', 'base': 'ETH', 'quote': 'CAD'},
            },
        }
        params.update(config)
        super(quadrigacx, self).__init__(params)

    def fetch_balance(self, params={}):
        balances = self.privatePostBalance()
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = {
                'free': float(balances[lowercase + '_available']),
                'used': float(balances[lowercase + '_reserved']),
                'total': float(balances[lowercase + '_balance']),
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        orderbook = self.publicGetOrderBook(self.extend({
            'book': self.market_id(symbol),
        }, params))
        timestamp = int(orderbook['timestamp']) * 1000
        return self.parse_order_book(orderbook, timestamp)

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetTicker(self.extend({
            'book': self.market_id(symbol),
        }, params))
        timestamp = int(ticker['timestamp']) * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': float(ticker['vwap']),
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = int(trade['date']) * 1000
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': str(trade['tid']),
            'order': None,
            'type': None,
            'side': trade['side'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, params={}):
        market = self.market(symbol)
        response = self.publicGetTransactions(self.extend({
            'book': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        method = 'privatePost' + self.capitalize(side)
        order = {
            'amount': amount,
            'book': self.market_id(symbol),
        }
        if type == 'limit':
            order['price'] = price
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder(self.extend({
            'id': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            url += '?' + self.urlencode(params)
        else:
            if not self.uid:
                raise AuthenticationError(self.id + ' requires `' + self.id + '.uid` property for authentication')
            nonce = self.nonce()
            request = ''.join([str(nonce), self.uid, self.apiKey])
            signature = self.hmac(self.encode(request), self.encode(self.secret))
            query = self.extend({
                'key': self.apiKey,
                'nonce': nonce,
                'signature': signature,
            }, params)
            body = self.json(query)
            headers = {
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class qryptos (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'qryptos',
            'name': 'QRYPTOS',
            'countries': ['CN', 'TW'],
            'version': '2',
            'rateLimit': 1000,
            'hasFetchTickers': True,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30953915-b1611dc0-a436-11e7-8947-c95bd5a42086.jpg',
                'api': 'https://api.qryptos.com',
                'www': 'https://www.qryptos.com',
                'doc': 'https://developers.quoine.com',
            },
            'api': {
                'public': {
                    'get': [
                        'products',
                        'products/{id}',
                        'products/{id}/price_levels',
                        'executions',
                        'ir_ladders/{currency}',
                    ],
                },
                'private': {
                    'get': [
                        'accounts/balance',
                        'crypto_accounts',
                        'executions/me',
                        'fiat_accounts',
                        'loan_bids',
                        'loans',
                        'orders',
                        'orders/{id}',
                        'orders/{id}/trades',
                        'trades',
                        'trades/{id}/loans',
                        'trading_accounts',
                        'trading_accounts/{id}',
                    ],
                    'post': [
                        'fiat_accounts',
                        'loan_bids',
                        'orders',
                    ],
                    'put': [
                        'loan_bids/{id}/close',
                        'loans/{id}',
                        'orders/{id}',
                        'orders/{id}/cancel',
                        'trades/{id}',
                        'trades/{id}/close',
                        'trades/close_all',
                        'trading_accounts/{id}',
                    ],
                },
            },
        }
        params.update(config)
        super(qryptos, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetProducts()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['id']
            base = market['base_currency']
            quote = market['quoted_currency']
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privateGetAccountsBalance()
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            total = float(balance['balance'])
            account = {
                'free': total,
                'used': 0.0,
                'total': total,
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetProductsIdPriceLevels(self.extend({
            'id': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'buy_price_levels', 'sell_price_levels')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        last = None
        if 'last_traded_price' in ticker:
            if ticker['last_traded_price']:
                length = len(ticker['last_traded_price'])
                if length > 0:
                    last = float(ticker['last_traded_price'])
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high_market_ask']),
            'low': float(ticker['low_market_bid']),
            'bid': float(ticker['market_bid']),
            'ask': float(ticker['market_ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': last,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['volume_24h']),
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetProducts(params)
        result = {}
        for t in range(0, len(tickers)):
            ticker = tickers[t]
            base = ticker['base_currency']
            quote = ticker['quoted_currency']
            symbol = base + '/' + quote
            market = self.markets[symbol]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetProductsId(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = trade['created_at'] * 1000
        return {
            'info': trade,
            'id': str(trade['id']),
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['taker_side'],
            'price': float(trade['price']),
            'amount': float(trade['quantity']),
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetExecutions(self.extend({
            'product_id': market['id'],
        }, params))
        return self.parse_trades(response['models'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'order_type': type,
            'product_id': self.market_id(symbol),
            'side': side,
            'quantity': amount,
        }
        if type == 'limit':
            order['price'] = price
        response = self.privatePostOrders(self.extend({
            'order': order,
        }, params))
        return {
            'info': response,
            'id': str(response['id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePutOrdersIdCancel(self.extend({
            'id': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        headers = {
            'X-Quoine-API-Version': self.version,
            'Content-Type': 'application/json',
        }
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            nonce = self.nonce()
            request = {
                'path': url,
                'nonce': nonce,
                'token_id': self.apiKey,
                'iat': int(math.floor(nonce / 1000)),  # issued at
            }
            if query:
                body = self.json(query)
            headers['X-Quoine-Auth'] = self.jwt(request, self.secret)
        url = self.urls['api'] + url
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'message' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class quoine (qryptos):

    def __init__(self, config={}):
        params = {
            'id': 'quoine',
            'name': 'QUOINE',
            'countries': ['JP', 'SG', 'VN'],
            'version': '2',
            'rateLimit': 1000,
            'hasFetchTickers': True,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766844-9615a4e8-5ee8-11e7-8814-fcd004db8cdd.jpg',
                'api': 'https://api.quoine.com',
                'www': 'https://www.quoine.com',
                'doc': 'https://developers.quoine.com',
            },
        }
        params.update(config)
        super(quoine, self).__init__(params)

# -----------------------------------------------------------------------------


class southxchange (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'southxchange',
            'name': 'SouthXchange',
            'countries': 'AR',  # Argentina
            'rateLimit': 1000,
            'hasFetchTickers': True,
            'hasCORS': False,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27838912-4f94ec8a-60f6-11e7-9e5d-bbf9bd50a559.jpg',
                'api': 'https://www.southxchange.com/api',
                'www': 'https://www.southxchange.com',
                'doc': 'https://www.southxchange.com/Home/Api',
            },
            'api': {
                'public': {
                    'get': [
                        'markets',
                        'price/{symbol}',
                        'prices',
                        'book/{symbol}',
                        'trades/{symbol}',
                    ],
                },
                'private': {
                    'post': [
                        'cancelMarketOrders',
                        'cancelOrder',
                        'generatenewaddress',
                        'listOrders',
                        'listBalances',
                        'placeOrder',
                        'withdraw',
                    ],
                },
            },
        }
        params.update(config)
        super(southxchange, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetMarkets()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            base = market[0]
            quote = market[1]
            symbol = base + '/' + quote
            id = symbol
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privatePostListBalances()
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['Currency']
            uppercase = currency.upper()
            free = float(balance['Available'])
            used = float(balance['Unconfirmed'])
            total = self.sum(free, used)
            account = {
                'free': free,
                'used': used,
                'total': total,
            }
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetBookSymbol(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'BuyOrders', 'SellOrders', 'Price', 'Amount')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': self.safe_float(ticker, 'Bid'),
            'ask': self.safe_float(ticker, 'Ask'),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': self.safe_float(ticker, 'Last'),
            'change': self.safe_float(ticker, 'Variation24Hr'),
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': self.safe_float(ticker, 'Volume24Hr'),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetPrices(params)
        tickers = self.index_by(response, 'Market')
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetPriceSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = trade['At'] * 1000
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': None,
            'order': None,
            'type': None,
            'side': trade['Type'],
            'price': trade['Price'],
            'amount': trade['Amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTradesSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        order = {
            'listingCurrency': market['base'],
            'referenceCurrency': market['quote'],
            'type': side,
            'amount': amount,
        }
        if type == 'limit':
            order['limitPrice'] = price
        response = self.privatePostPlaceOrder(self.extend(order, params))
        return {
            'info': response,
            'id': str(response),
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostCancelOrder(self.extend({
            'orderCode': id,
        }, params))

    def withdraw(self, currency, amount, address, params={}):
        response = self.privatePostWithdraw(self.extend({
            'currency': currency,
            'address': address,
            'amount': amount,
        }, params))
        return {
            'info': response,
            'id': None,
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            nonce = self.nonce()
            query = self.extend({
                'key': self.apiKey,
                'nonce': nonce,
            }, query)
            body = self.json(query)
            headers = {
                'Content-Type': 'application/json',
                'Hash': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        return response

# -----------------------------------------------------------------------------


class surbitcoin (blinktrade):

    def __init__(self, config={}):
        params = {
            'id': 'surbitcoin',
            'name': 'SurBitcoin',
            'countries': 'VE',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27991511-f0a50194-6481-11e7-99b5-8f02932424cc.jpg',
                'api': {
                    'public': 'https://api.blinktrade.com/api',
                    'private': 'https://api.blinktrade.com/tapi',
                },
                'www': 'https://surbitcoin.com',
                'doc': 'https://blinktrade.com/docs',
            },
            'comment': 'Blinktrade API',
            'markets': {
                'BTC/VEF': {'id': 'BTCVEF', 'symbol': 'BTC/VEF', 'base': 'BTC', 'quote': 'VEF', 'brokerId': 1, 'broker': 'SurBitcoin'},
            },
        }
        params.update(config)
        super(surbitcoin, self).__init__(params)

# -----------------------------------------------------------------------------


class tidex (btce):

    def __init__(self, config={}):
        params = {
            'id': 'tidex',
            'name': 'Tidex',
            'countries': 'UK',
            'rateLimit': 1000,
            'version': '3',
            # 'hasCORS': False,
            # 'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30781780-03149dc4-a12e-11e7-82bb-313b269d24d4.jpg',
                'api': {
                    'public': 'https://api.tidex.com/api',
                    'private': 'https://api.tidex.com/tapi',
                },
                'www': 'https://tidex.com',
                'doc': 'https://tidex.com/public-api',
                'fees': 'https://tidex.com/pairs-spec'
            },
        }
        params.update(config)
        super(tidex, self).__init__(params)

# -----------------------------------------------------------------------------


class therock (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'therock',
            'name': 'TheRockTrading',
            'countries': 'MT',
            'rateLimit': 1000,
            'version': 'v1',
            'hasCORS': False,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766869-75057fa2-5ee9-11e7-9a6f-13e641fa4707.jpg',
                'api': 'https://api.therocktrading.com',
                'www': 'https://therocktrading.com',
                'doc': [
                    'https://api.therocktrading.com/doc/v1/index.html',
                    'https://api.therocktrading.com/doc/',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'funds/{id}/orderbook',
                        'funds/{id}/ticker',
                        'funds/{id}/trades',
                        'funds/tickers',
                    ],
                },
                'private': {
                    'get': [
                        'balances',
                        'balances/{id}',
                        'discounts',
                        'discounts/{id}',
                        'funds',
                        'funds/{id}',
                        'funds/{id}/trades',
                        'funds/{fund_id}/orders',
                        'funds/{fund_id}/orders/{id}',
                        'funds/{fund_id}/position_balances',
                        'funds/{fund_id}/positions',
                        'funds/{fund_id}/positions/{id}',
                        'transactions',
                        'transactions/{id}',
                        'withdraw_limits/{id}',
                        'withdraw_limits',
                    ],
                    'post': [
                        'atms/withdraw',
                        'funds/{fund_id}/orders',
                    ],
                    'delete': [
                        'funds/{fund_id}/orders/{id}',
                        'funds/{fund_id}/orders/remove_all',
                    ],
                },
            },
        }
        params.update(config)
        super(therock, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetFundsTickers()
        result = []
        for p in range(0, len(markets['tickers'])):
            market = markets['tickers'][p]
            id = market['fund_id']
            base = id[0:3]
            quote = id[3:6]
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalances()
        balances = response['balances']
        result = {'info': response}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            free = balance['trading_balance']
            total = balance['balance']
            used = total - free
            account = {
                'free': free,
                'used': used,
                'total': total,
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetFundsIdOrderbook(self.extend({
            'id': self.market_id(symbol),
        }, params))
        timestamp = self.parse8601(orderbook['date'])
        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'amount')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.parse8601(ticker['date'])
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': float(ticker['open']),
            'close': float(ticker['close']),
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['volume_traded']),
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetFundsTickers(params)
        tickers = self.index_by(response['tickers'], 'fund_id')
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetFundsIdTicker(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market=None):
        if not market:
            market = self.markets_by_id[trade['fund_id']]
        timestamp = self.parse8601(trade['date'])
        return {
            'info': trade,
            'id': str(trade['id']),
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['side'],
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetFundsIdTrades(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_trades(response['trades'], market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        response = self.privatePostFundsFundIdOrders(self.extend({
            'fund_id': self.market_id(symbol),
            'side': side,
            'amount': amount,
            'price': price,
        }, params))
        return {
            'info': response,
            'id': str(response['id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privateDeleteFundsFundIdOrdersId(self.extend({
            'id': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            nonce = str(self.nonce())
            auth = nonce + url
            headers = {
                'X-TRT-KEY': self.apiKey,
                'X-TRT-NONCE': nonce,
                'X-TRT-SIGN': self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha512),
            }
            if query:
                body = self.json(query)
                headers['Content-Type'] = 'application/json'
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'errors' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class urdubit (blinktrade):

    def __init__(self, config={}):
        params = {
            'id': 'urdubit',
            'name': 'UrduBit',
            'countries': 'PK',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27991453-156bf3ae-6480-11e7-82eb-7295fe1b5bb4.jpg',
                'api': {
                    'public': 'https://api.blinktrade.com/api',
                    'private': 'https://api.blinktrade.com/tapi',
                },
                'www': 'https://urdubit.com',
                'doc': 'https://blinktrade.com/docs',
            },
            'comment': 'Blinktrade API',
            'markets': {
                'BTC/PKR': {'id': 'BTCPKR', 'symbol': 'BTC/PKR', 'base': 'BTC', 'quote': 'PKR', 'brokerId': 8, 'broker': 'UrduBit'},
            },
        }
        params.update(config)
        super(urdubit, self).__init__(params)

# -----------------------------------------------------------------------------


class vaultoro (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'vaultoro',
            'name': 'Vaultoro',
            'countries': 'CH',
            'rateLimit': 1000,
            'version': '1',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766880-f205e870-5ee9-11e7-8fe2-0d5b15880752.jpg',
                'api': 'https://api.vaultoro.com',
                'www': 'https://www.vaultoro.com',
                'doc': 'https://api.vaultoro.com',
            },
            'api': {
                'public': {
                    'get': [
                        'bidandask',
                        'buyorders',
                        'latest',
                        'latesttrades',
                        'markets',
                        'orderbook',
                        'sellorders',
                        'transactions/day',
                        'transactions/hour',
                        'transactions/month',
                    ],
                },
                'private': {
                    'get': [
                        'balance',
                        'mytrades',
                        'orders',
                    ],
                    'post': [
                        'buy/{symbol}/{type}',
                        'cancel/{id}',
                        'sell/{symbol}/{type}',
                        'withdraw',
                    ],
                },
            },
        }
        params.update(config)
        super(vaultoro, self).__init__(params)

    def fetch_markets(self):
        result = []
        markets = self.publicGetMarkets()
        market = markets['data']
        base = market['BaseCurrency']
        quote = market['MarketCurrency']
        symbol = base + '/' + quote
        baseId = base
        quoteId = quote
        id = market['MarketName']
        result.append({
            'id': id,
            'symbol': symbol,
            'base': base,
            'quote': quote,
            'baseId': baseId,
            'quoteId': quoteId,
            'info': market,
        })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalance()
        balances = response['data']
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency_code']
            uppercase = currency.upper()
            free = balance['cash']
            used = balance['reserved']
            total = self.sum(free, used)
            account = {
                'free': free,
                'used': used,
                'total': total,
            }
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetOrderbook(params)
        orderbook = {
            'bids': response['data'][0]['b'],
            'asks': response['data'][1]['s'],
        }
        result = self.parse_order_book(orderbook, None, 'bids', 'asks', 'Gold_Price', 'Gold_Amount')
        result['bids'] = self.sort_by(result['bids'], 0, True)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        quote = self.publicGetBidandask(params)
        bidsLength = len(quote['bids'])
        bid = quote['bids'][bidsLength - 1]
        ask = quote['asks'][0]
        response = self.publicGetMarkets(params)
        ticker = response['data']
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['24hHigh']),
            'low': float(ticker['24hLow']),
            'bid': bid[0],
            'ask': ask[0],
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['LastPrice']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['24hVolume']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = self.parse8601(trade['Time'])
        return {
            'id': None,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': None,
            'type': None,
            'side': None,
            'price': trade['Gold_Price'],
            'amount': trade['Gold_Amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTransactionsDay(params)
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = 'privatePost' + self.capitalize(side) + 'SymbolType'
        response = getattr(self, method)(self.extend({
            'symbol': market['quoteId'].lower(),
            'type': type,
            'gld': amount,
            'price': price or 1,
        }, params))
        return {
            'info': response,
            'id': response['data']['Order_ID'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostCancelId(self.extend({
            'id': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/'
        if api == 'public':
            url += path
        else:
            nonce = self.nonce()
            url += self.version + '/' + self.implode_params(path, params)
            query = self.extend({
                'nonce': nonce,
                'apikey': self.apiKey,
            }, self.omit(params, self.extract_params(path)))
            url += '?' + self.urlencode(query)
            headers = {
                'Content-Type': 'application/json',
                'X-Signature': self.hmac(self.encode(url), self.encode(self.secret))
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class vbtc (blinktrade):

    def __init__(self, config={}):
        params = {
            'id': 'vbtc',
            'name': 'VBTC',
            'countries': 'VN',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27991481-1f53d1d8-6481-11e7-884e-21d17e7939db.jpg',
                'api': {
                    'public': 'https://api.blinktrade.com/api',
                    'private': 'https://api.blinktrade.com/tapi',
                },
                'www': 'https://vbtc.exchange',
                'doc': 'https://blinktrade.com/docs',
            },
            'comment': 'Blinktrade API',
            'markets': {
                'BTC/VND': {'id': 'BTCVND', 'symbol': 'BTC/VND', 'base': 'BTC', 'quote': 'VND', 'brokerId': 3, 'broker': 'VBTC'},
            },
        }
        params.update(config)
        super(vbtc, self).__init__(params)

# -----------------------------------------------------------------------------


class virwox (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'virwox',
            'name': 'VirWoX',
            'countries': ['AT', 'EU'],
            'rateLimit': 1000,
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766894-6da9d360-5eea-11e7-90aa-41f2711b7405.jpg',
                'api': {
                    'public': 'http://api.virwox.com/api/json.php',
                    'private': 'https://www.virwox.com/api/trading.php',
                },
                'www': 'https://www.virwox.com',
                'doc': 'https://www.virwox.com/developers.php',
            },
            'api': {
                'public': {
                    'get': [
                        'getInstruments',
                        'getBestPrices',
                        'getMarketDepth',
                        'estimateMarketOrder',
                        'getTradedPriceVolume',
                        'getRawTradeData',
                        'getStatistics',
                        'getTerminalList',
                        'getGridList',
                        'getGridStatistics',
                    ],
                    'post': [
                        'getInstruments',
                        'getBestPrices',
                        'getMarketDepth',
                        'estimateMarketOrder',
                        'getTradedPriceVolume',
                        'getRawTradeData',
                        'getStatistics',
                        'getTerminalList',
                        'getGridList',
                        'getGridStatistics',
                    ],
                },
                'private': {
                    'get': [
                        'cancelOrder',
                        'getBalances',
                        'getCommissionDiscount',
                        'getOrders',
                        'getTransactions',
                        'placeOrder',
                    ],
                    'post': [
                        'cancelOrder',
                        'getBalances',
                        'getCommissionDiscount',
                        'getOrders',
                        'getTransactions',
                        'placeOrder',
                    ],
                },
            },
        }
        params.update(config)
        super(virwox, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetInstruments()
        keys = list(markets['result'].keys())
        result = []
        for p in range(0, len(keys)):
            market = markets['result'][keys[p]]
            id = market['instrumentID']
            symbol = market['symbol']
            base = market['longCurrency']
            quote = market['shortCurrency']
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetBalances()
        balances = response['result']['accountList']
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            total = balance['balance']
            account = {
                'free': total,
                'used': 0.0,
                'total': total,
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetchMarketPrice(self, symbol, params={}):
        self.load_markets()
        response = self.publicPostGetBestPrices(self.extend({
            'symbols': [symbol],
        }, params))
        result = response['result']
        return {
            'bid': self.safe_float(result[0], 'bestBuyPrice'),
            'ask': self.safe_float(result[0], 'bestSellPrice'),
        }

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        response = self.publicPostGetMarketDepth(self.extend({
            'symbols': [symbol],
            'buyDepth': 100,
            'sellDepth': 100,
        }, params))
        orderbook = response['result'][0]
        return self.parse_order_book(orderbook, None, 'buy', 'sell', 'price', 'volume')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        end = self.milliseconds()
        start = end - 86400000
        response = self.publicGetTradedPriceVolume(self.extend({
            'instrument': symbol,
            'endDate': self.YmdHMS(end),
            'startDate': self.YmdHMS(start),
            'HLOC': 1,
        }, params))
        marketPrice = self.fetchMarketPrice(symbol, params)
        tickers = response['result']['priceVolumeList']
        keys = list(tickers.keys())
        length = len(keys)
        lastKey = keys[length - 1]
        ticker = tickers[lastKey]
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': marketPrice['bid'],
            'ask': marketPrice['ask'],
            'vwap': None,
            'open': float(ticker['open']),
            'close': float(ticker['close']),
            'first': None,
            'last': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['longVolume']),
            'quoteVolume': float(ticker['shortVolume']),
            'info': ticker,
        }

    def fetch_trades(self, market, params={}):
        self.load_markets()
        return self.publicGetRawTradeData(self.extend({
            'instrument': market,
            'timespan': 3600,
        }, params))

    def create_order(self, market, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'instrument': self.symbol(market),
            'orderType': side.upper(),
            'amount': amount,
        }
        if type == 'limit':
            order['price'] = price
        response = self.privatePostPlaceOrder(self.extend(order, params))
        return {
            'info': response,
            'id': str(response['orderID']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder(self.extend({
            'orderID': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        auth = {}
        if api == 'private':
            auth['key'] = self.apiKey
            auth['user'] = self.login
            auth['pass'] = self.password
        nonce = self.nonce()
        if method == 'GET':
            url += '?' + self.urlencode(self.extend({
                'method': path,
                'id': nonce,
            }, auth, params))
        else:
            headers = {'Content-Type': 'application/json'}
            body = self.json({
                'method': path,
                'params': self.extend(auth, params),
                'id': nonce,
            })
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            if response['error']:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response

# -----------------------------------------------------------------------------


class wex (btce):

    def __init__(self, config={}):
        params = {
            'id': 'wex',
            'name': 'WEX',
            'countries': 'NZ',  # New Zealand
            'version': '3',
            'hasFetchTickers': True,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30652751-d74ec8f8-9e31-11e7-98c5-71469fcef03e.jpg',
                'api': {
                    'public': 'https://wex.nz/api',
                    'private': 'https://wex.nz/tapi',
                },
                'www': 'https://wex.nz',
                'doc': [
                    'https://wex.nz/api/3/docs',
                    'https://wex.nz/tapi/docs',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'info',
                        'ticker/{pair}',
                        'depth/{pair}',
                        'trades/{pair}',
                    ],
                },
                'private': {
                    'post': [
                        'getInfo',
                        'Trade',
                        'ActiveOrders',
                        'OrderInfo',
                        'CancelOrder',
                        'TradeHistory',
                        'TransHistory',
                        'CoinDepositAddress',
                        'WithdrawCoin',
                        'CreateCoupon',
                        'RedeemCoupon',
                    ],
                }
            },
        }
        params.update(config)
        super(wex, self).__init__(params)

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['updated'] * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'sell'),
            'ask': self.safe_float(ticker, 'buy'),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': self.safe_float(ticker, 'last'),
            'change': None,
            'percentage': None,
            'average': self.safe_float(ticker, 'avg'),
            'baseVolume': self.safe_float(ticker, 'vol_cur'),
            'quoteVolume': self.safe_float(ticker, 'vol'),
            'info': ticker,
        }

# -----------------------------------------------------------------------------


class xbtce (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'xbtce',
            'name': 'xBTCe',
            'countries': 'RU',
            'rateLimit': 2000,  # responses are cached every 2 seconds
            'version': 'v1',
            'hasPublicAPI': False,
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasFetchOHLCV': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28059414-e235970c-662c-11e7-8c3a-08e31f78684b.jpg',
                'api': 'https://cryptottlivewebapi.xbtce.net:8443/api',
                'www': 'https://www.xbtce.com',
                'doc': [
                    'https://www.xbtce.com/tradeapi',
                    'https://support.xbtce.info/Knowledgebase/Article/View/52/25/xbtce-exchange-api',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'currency',
                        'currency/{filter}',
                        'level2',
                        'level2/{filter}',
                        'quotehistory/{symbol}/{periodicity}/bars/ask',
                        'quotehistory/{symbol}/{periodicity}/bars/bid',
                        'quotehistory/{symbol}/level2',
                        'quotehistory/{symbol}/ticks',
                        'symbol',
                        'symbol/{filter}',
                        'tick',
                        'tick/{filter}',
                        'ticker',
                        'ticker/{filter}',
                        'tradesession',
                    ],
                },
                'private': {
                    'get': [
                        'tradeserverinfo',
                        'tradesession',
                        'currency',
                        'currency/{filter}',
                        'level2',
                        'level2/{filter}',
                        'symbol',
                        'symbol/{filter}',
                        'tick',
                        'tick/{filter}',
                        'account',
                        'asset',
                        'asset/{id}',
                        'position',
                        'position/{id}',
                        'trade',
                        'trade/{id}',
                        'quotehistory/{symbol}/{periodicity}/bars/ask',
                        'quotehistory/{symbol}/{periodicity}/bars/ask/info',
                        'quotehistory/{symbol}/{periodicity}/bars/bid',
                        'quotehistory/{symbol}/{periodicity}/bars/bid/info',
                        'quotehistory/{symbol}/level2',
                        'quotehistory/{symbol}/level2/info',
                        'quotehistory/{symbol}/periodicities',
                        'quotehistory/{symbol}/ticks',
                        'quotehistory/{symbol}/ticks/info',
                        'quotehistory/cache/{symbol}/{periodicity}/bars/ask',
                        'quotehistory/cache/{symbol}/{periodicity}/bars/bid',
                        'quotehistory/cache/{symbol}/level2',
                        'quotehistory/cache/{symbol}/ticks',
                        'quotehistory/symbols',
                        'quotehistory/version',
                    ],
                    'post': [
                        'trade',
                        'tradehistory',
                    ],
                    'put': [
                        'trade',
                    ],
                    'delete': [
                        'trade',
                    ],
                },
            },
        }
        params.update(config)
        super(xbtce, self).__init__(params)

    def fetch_markets(self):
        markets = self.privateGetSymbol()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['Symbol']
            base = market['MarginCurrency']
            quote = market['ProfitCurrency']
            if base == 'DSH':
                base = 'DASH'
            symbol = base + '/' + quote
            symbol = symbol if market['IsTradeAllowed'] else id
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privateGetAsset()
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['Currency']
            uppercase = currency.upper()
            # xbtce names DASH incorrectly as DSH
            if uppercase == 'DSH':
                uppercase = 'DASH'
            account = {
                'free': balance['FreeAmount'],
                'used': balance['LockedAmount'],
                'total': balance['Amount'],
            }
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        orderbook = self.privateGetLevel2Filter(self.extend({
            'filter': market['id'],
        }, params))
        orderbook = orderbook[0]
        timestamp = orderbook['Timestamp']
        return self.parse_order_book(orderbook, timestamp, 'Bids', 'Asks', 'Price', 'Volume')

    def parse_ticker(self, ticker, market=None):
        timestamp = 0
        last = None
        if 'LastBuyTimestamp' in ticker:
            if timestamp < ticker['LastBuyTimestamp']:
                timestamp = ticker['LastBuyTimestamp']
                last = ticker['LastBuyPrice']
        if 'LastSellTimestamp' in ticker:
            if timestamp < ticker['LastSellTimestamp']:
                timestamp = ticker['LastSellTimestamp']
                last = ticker['LastSellPrice']
        if not timestamp:
            timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': ticker['DailyBestBuyPrice'],
            'low': ticker['DailyBestSellPrice'],
            'bid': ticker['BestBid'],
            'ask': ticker['BestAsk'],
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': last,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': ticker['DailyTradedTotalVolume'],
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTicker(params)
        tickers = self.index_by(tickers, 'Symbol')
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = None
            symbol = None
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            else:
                base = id[0:3]
                quote = id[3:6]
                if base == 'DSH':
                    base = 'DASH'
                if quote == 'DSH':
                    quote = 'DASH'
                symbol = base + '/' + quote
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        tickers = self.publicGetTickerFilter(self.extend({
            'filter': market['id'],
        }, params))
        length = len(tickers)
        if length < 1:
            raise ExchangeError(self.id + ' fetchTicker returned empty response, xBTCe public API error')
        tickers = self.index_by(tickers, 'Symbol')
        ticker = tickers[market['id']]
        return self.parse_ticker(ticker, market)

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        # no method for trades?
        return self.privateGetTrade(params)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv['Timestamp'],
            ohlcv['Open'],
            ohlcv['High'],
            ohlcv['Low'],
            ohlcv['Close'],
            ohlcv['Volume'],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        raise NotSupported(self.id + ' fetchOHLCV is disabled by the exchange')
        minutes = int(timeframe / 60)  # 1 minute by default
        periodicity = str(minutes)
        self.load_markets()
        market = self.market(symbol)
        if not since:
            since = self.seconds() - 86400 * 7  # last day by defulat
        if not limit:
            limit = 1000  # default
        response = self.privateGetQuotehistorySymbolPeriodicityBarsBid(self.extend({
            'symbol': market['id'],
            'periodicity': periodicity,
            'timestamp': since,
            'count': limit,
        }, params))
        return self.parse_ohlcvs(response['Bars'], market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        response = self.tapiPostTrade(self.extend({
            'pair': self.market_id(symbol),
            'type': side,
            'amount': amount,
            'rate': price,
        }, params))
        return {
            'info': response,
            'id': str(response['Id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privateDeleteTrade(self.extend({
            'Type': 'Cancel',
            'Id': id,
        }, params))

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        if not self.apiKey:
            raise AuthenticationError(self.id + ' requires apiKey for all requests, their public API is always busy')
        if not self.uid:
            raise AuthenticationError(self.id + ' requires uid property for authentication and trading')
        url = self.urls['api'] + '/' + self.version
        if api == 'public':
            url += '/' + api
        url += '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            headers = {'Accept-Encoding': 'gzip, deflate'}
            nonce = str(self.nonce())
            if method == 'POST':
                if query:
                    headers['Content-Type'] = 'application/json'
                    body = self.json(query)
                else:
                    url += '?' + self.urlencode(query)
            auth = nonce + self.uid + self.apiKey + method + url
            if body:
                auth += body
            signature = self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha256, 'base64')
            credentials = self.uid + ':' + self.apiKey + ':' + nonce + ':' + self.binary_to_string(signature)
            headers['Authorization'] = 'HMAC ' + credentials
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

# -----------------------------------------------------------------------------


class yobit (btce):

    def __init__(self, config={}):
        params = {
            'id': 'yobit',
            'name': 'YoBit',
            'countries': 'RU',
            'rateLimit': 3000,  # responses are cached every 2 seconds
            'version': '3',
            'hasCORS': False,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766910-cdcbfdae-5eea-11e7-9859-03fea873272d.jpg',
                'api': {
                    'public': 'https://yobit.net/api',
                    'private': 'https://yobit.net/tapi',
                },
                'www': 'https://www.yobit.net',
                'doc': 'https://www.yobit.net/en/api/',
            },
            'api': {
                'public': {
                    'get': [
                        'depth/{pair}',
                        'info',
                        'ticker/{pair}',
                        'trades/{pair}',
                    ],
                },
                'private': {
                    'post': [
                        'ActiveOrders',
                        'CancelOrder',
                        'GetDepositAddress',
                        'getInfo',
                        'OrderInfo',
                        'Trade',
                        'TradeHistory',
                        'WithdrawCoinsToAddress',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.002,
                    'taker': 0.002,
                },
                'funding': 0.0,
            },
        }
        params.update(config)
        super(yobit, self).__init__(params)

    def common_currency_code(self, currency):
        substitutions = {
            'AIR': 'AirCoin',
            'ANI': 'ANICoin',
            'ANT': 'AntsCoin',
            'ATM': 'Autumncoin',
            'BCC': 'BCH',
            'BTS': 'Bitshares2',
            'DCT': 'Discount',
            'DGD': 'DarkGoldCoin',
            'ICN': 'iCoin',
            'LIZI': 'LiZi',
            'LUN': 'LunarCoin',
            'NAV': 'NavajoCoin',
            'OMG': 'OMGame',
            'PAY': 'EPAY',
            'REP': 'Republicoin',
        }
        if currency in substitutions:
            return substitutions[currency]
        return currency

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetInfo()
        balances = response['return']
        result = {'info': balances}
        sides = {'free': 'funds', 'total': 'funds_incl_orders'}
        keys = list(sides.keys())
        for i in range(0, len(keys)):
            key = keys[i]
            side = sides[key]
            if side in balances:
                currencies = list(balances[side].keys())
                for j in range(0, len(currencies)):
                    lowercase = currencies[j]
                    uppercase = lowercase.upper()
                    currency = self.common_currency_code(uppercase)
                    account = None
                    if currency in result:
                        account = result[currency]
                    else:
                        account = self.account()
                    account[key] = balances[side][lowercase]
                    if account['total'] and account['free']:
                        account['used'] = account['total'] - account['free']
                    result[currency] = account
        return self.parse_balance(result)

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        response = self.privatePostWithdrawCoinsToAddress(self.extend({
            'coinName': currency,
            'amount': amount,
            'address': address,
        }, params))
        return {
            'info': response,
            'id': None,
        }

# -----------------------------------------------------------------------------


class yunbi (acx):

    def __init__(self, config={}):
        params = {
            'id': 'yunbi',
            'name': 'YUNBI',
            'countries': 'CN',
            'rateLimit': 1000,
            'version': 'v2',
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasFetchOHLCV': True,
            'timeframes': {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '2h': '120',
                '4h': '240',
                '12h': '720',
                '1d': '1440',
                '3d': '4320',
                '1w': '10080',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28570548-4d646c40-7147-11e7-9cf6-839b93e6d622.jpg',
                'extension': '.json',  # default extension appended to endpoint URLs
                'api': 'https://yunbi.com',
                'www': 'https://yunbi.com',
                'doc': [
                    'https://yunbi.com/documents/api/guide',
                    'https://yunbi.com/swagger/',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'tickers',
                        'tickers/{market}',
                        'markets',
                        'order_book',
                        'k',
                        'depth',
                        'trades',
                        'k_with_pending_trades',
                        'timestamp',
                        'addresses/{address}',
                        'partners/orders/{id}/trades',
                    ],
                },
                'private': {
                    'get': [
                        'deposits',
                        'members/me',
                        'deposit',
                        'deposit_address',
                        'order',
                        'orders',
                        'trades/my',
                    ],
                    'post': [
                        'order/delete',
                        'orders',
                        'orders/multi',
                        'orders/clear',
                    ],
                },
            },
        }
        params.update(config)
        super(yunbi, self).__init__(params)

# -----------------------------------------------------------------------------


class zaif (Exchange):

    def __init__(self, config={}):
        params = {
            'id': 'zaif',
            'name': 'Zaif',
            'countries': 'JP',
            'rateLimit': 2000,
            'version': '1',
            'hasCORS': False,
            'hasFetchOpenOrders': True,
            'hasFetchClosedOrders': True,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766927-39ca2ada-5eeb-11e7-972f-1b4199518ca6.jpg',
                'api': 'https://api.zaif.jp',
                'www': 'https://zaif.jp',
                'doc': [
                    'http://techbureau-api-document.readthedocs.io/ja/latest/index.html',
                    'https://corp.zaif.jp/api-docs',
                    'https://corp.zaif.jp/api-docs/api_links',
                    'https://www.npmjs.com/package/zaif.jp',
                    'https://github.com/you21979/node-zaif',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'depth/{pair}',
                        'currencies/{pair}',
                        'currencies/all',
                        'currency_pairs/{pair}',
                        'currency_pairs/all',
                        'last_price/{pair}',
                        'ticker/{pair}',
                        'trades/{pair}',
                    ],
                },
                'private': {
                    'post': [
                        'active_orders',
                        'cancel_order',
                        'deposit_history',
                        'get_id_info',
                        'get_info',
                        'get_info2',
                        'get_personal_info',
                        'trade',
                        'trade_history',
                        'withdraw',
                        'withdraw_history',
                    ],
                },
                'ecapi': {
                    'post': [
                        'createInvoice',
                        'getInvoice',
                        'getInvoiceIdsByOrderNumber',
                        'cancelInvoice',
                    ],
                },
            },
        }
        params.update(config)
        super(zaif, self).__init__(params)

    def fetch_markets(self):
        markets = self.publicGetCurrencyPairsAll()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['currency_pair']
            symbol = market['name']
            base, quote = symbol.split('/')
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetInfo()
        balances = response['return']
        result = {'info': balances}
        currencies = list(balances['funds'].keys())
        for c in range(0, len(currencies)):
            currency = currencies[c]
            balance = balances['funds'][currency]
            uppercase = currency.upper()
            account = {
                'free': balance,
                'used': 0.0,
                'total': balance,
            }
            if 'deposit' in balances:
                if currency in balances['deposit']:
                    account['total'] = balances['deposit'][currency]
                    account['used'] = account['total'] - account['free']
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetDepthPair(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        ticker = self.publicGetTickerPair(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': ticker['high'],
            'low': ticker['low'],
            'bid': ticker['bid'],
            'ask': ticker['ask'],
            'vwap': ticker['vwap'],
            'open': None,
            'close': None,
            'first': None,
            'last': ticker['last'],
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': ticker['volume'],
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        side = 'buy' if (trade['trade_type'] == 'bid') else 'sell'
        timestamp = trade['date'] * 1000
        id = self.safe_string(trade, 'id')
        id = self.safe_string(trade, 'tid', id)
        if not market:
            market = self.markets_by_id[trade['currency_pair']]
        return {
            'id': str(id),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTradesPair(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        response = self.privatePostTrade(self.extend({
            'currency_pair': self.market_id(symbol),
            'action': 'bid' if (side == 'buy') else 'ask',
            'amount': amount,
            'price': price,
        }, params))
        return {
            'info': response,
            'id': str(response['return']['order_id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder(self.extend({
            'order_id': id,
        }, params))

    def parse_order(self, order, market=None):
        side = 'buy' if (order['action'] == 'bid') else 'sell'
        timestamp = int(order['timestamp']) * 1000
        if not market:
            market = self.markets_by_id[order['currency_pair']]
        price = order['price']
        amount = order['amount']
        return {
            'id': str(order['id']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': 'open',
            'symbol': market['symbol'],
            'type': 'limit',
            'side': side,
            'price': price,
            'cost': price * amount,
            'amount': amount,
            'filled': None,
            'remaining': None,
            'trades': None,
            'fee': None,
        }

    def parse_orders(self, orders, market=None):
        ids = list(orders.keys())
        result = []
        for i in range(0, len(ids)):
            id = ids[i]
            order = orders[id]
            extended = self.extend(order, {'id': id})
            result.append(self.parse_order(extended, market))
        return result

    def fetch_open_orders(self, symbol=None, params={}):
        self.load_markets()
        market = None
        request = {
            # 'is_token': False,
            # 'is_token_both': False,
        }
        if symbol:
            market = self.market(symbol)
            request['currency_pair'] = market['id']
        response = self.privatePostActiveOrders(self.extend(request, params))
        return self.parse_orders(response['return'], market)

    def fetchClosedOrders(self, symbol=None, params={}):
        self.load_markets()
        market = None
        request = {
            # 'from': 0,
            # 'count': 1000,
            # 'from_id': 0,
            # 'end_id': 1000,
            # 'order': 'DESC',
            # 'since': 1503821051,
            # 'end': 1503821051,
            # 'is_token': False,
        }
        if symbol:
            market = self.market(symbol)
            request['currency_pair'] = market['id']
        response = self.privatePostTradeHistory(self.extend(request, params))
        return self.parse_orders(response['return'], market)

    def withdraw(self, currency, amount, address, params={}):
        self.load_markets()
        if currency == 'JPY':
            raise ExchangeError(self.id + ' does not allow ' + currency + ' withdrawals')
        result = self.privatePostWithdraw(self.extend({
            'currency': currency,
            'amount': amount,
            'address': address,
            # 'message': 'Hinot ',  # XEM only
            # 'opt_fee': 0.003,  # BTC and MONA only
        }, params))
        return {
            'info': result,
            'id': result['return']['txid'],
            'fee': result['return']['fee'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/'
        if api == 'public':
            url += 'api/' + self.version + '/' + self.implode_params(path, params)
        else:
            url += 'ecapi' if (api == 'ecapi') else 'tapi'
            nonce = self.nonce()
            body = self.urlencode(self.extend({
                'method': path,
                'nonce': nonce,
            }, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='api', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + response['error'])
        if 'success' in response:
            if not response['success']:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response
