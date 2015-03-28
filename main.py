from CryptoCoinChartsApi.Models import TradingPair

__author__ = 'yardenst'
from CryptoCoinChartsApi import API
import csv
import requests

api = API()
api.API_PATH = 'http://api.cryptocoincharts.info/'


def tradingpair(pair):
    url = api.API_PATH + 'tradingPair/' + pair

    json_data = requests.get(url).json()

    tradingpair = TradingPair()
    tradingpair.id = json_data['id']
    tradingpair.price = json_data['price']
    tradingpair.price_before_24h = json_data['price_before_24h']
    tradingpair.volume_first = json_data['volume_first']
    tradingpair.volume_second = json_data['volume_second']
    tradingpair.volume_btc = json_data['volume_btc']
    tradingpair.best_market = json_data['best_market']
    tradingpair.latest_trade = json_data['latest_trade']
    tradingpair.markets = json_data['markets']

    return tradingpair

# some settings
ALL = 10
VOLUME_TITLE_TEXT = 'vol'  # what to wirte on the header for volumes
PRICE_TITLE_TEXT = 'prc'  # what to wirte on the header for prices
TRADE_VOLUME_PAIR_FIELD = 'volume'  # the field of TRADE VOLUME in the response
PRICE_PAIR_FIELD = 'price'  # the field of PRICE in the response
MARKETS_PAIR_FIELD = 'markets'
MARKET_PAIR_FIELD = 'market'
NULL_COLUMN = 'X'  # what to write on cells of the same pair [usd_usd],[btc_btc]....
ERROR_COLUMN = 'ERR'  # what to write when there is an error getting the data
NO_INFO_COLUMN = 'N/A'  # what to write when there is no data
coins_max = ALL  # how many coins to work on (after the filter, see below)
min_price = 0.001  # will only filter on coins with price > than this
min_volume_btc = 0.001  # will only filter on coins with volume > than this
coins_filter = lambda _coin: (
    float(_coin.price_btc) > min_price and float(_coin.volume_btc) > min_volume_btc)  # the filter func
# coins_filter = lambda _coin: _coin.id in ['btc', 'usd']  # the filter func

if __name__ == '__main__':

    coins = filter(coins_filter, api.listcoins())[:coins_max]
    print("working on %d" % len(coins))

    def write_markets_for_coin(coin, csv_writer):
        print "extracting data for %s ..." % coin.id
        for other_coin in coins:
            if other_coin.id != coin.id:
                print "- pair with %s" % other_coin.id,
                try:
                    pair_id = "[%s_%s]" % (coin.id, other_coin.id)
                    trading_pair = tradingpair(pair_id)
                    markets = getattr(trading_pair, MARKETS_PAIR_FIELD) or []
                    print " --- markets found"
                    for market in markets:
                        csv_writer.writerow(['%s %s %s %s' % (
                            coin.id, other_coin.id, market.get(MARKET_PAIR_FIELD, NO_INFO_COLUMN), VOLUME_TITLE_TEXT),
                                             market.get(TRADE_VOLUME_PAIR_FIELD, NO_INFO_COLUMN),

                        ])

                        csv_writer.writerow(['%s %s %s %s' % (
                            coin.id, other_coin.id, market.get(MARKET_PAIR_FIELD, NO_INFO_COLUMN), PRICE_TITLE_TEXT),
                                             market.get(PRICE_PAIR_FIELD, NO_INFO_COLUMN),

                        ])

                except TypeError, e:
                    pass
                except AttributeError, e:
                    print("no markets for %s-%s" % (coin.id, other_coin.id))


    def write_coin_row(coin):
        print "extracting data for %s ..." % coin.id
        row = [coin.id, coin.name]

        for other_coin in coins:
            print "- pair with %s" % other_coin.id
            if other_coin.id != coin.id:
                try:
                    pair_id = "[%s_%s]" % (coin.id, other_coin.id)
                    trading_pair = api.tradingpair(pair_id)
                    row.append(getattr(trading_pair, TRADE_VOLUME_PAIR_FIELD) or NO_INFO_COLUMN)
                    row.append(getattr(trading_pair, PRICE_PAIR_FIELD) or NO_INFO_COLUMN)
                except TypeError:
                    row.append(ERROR_COLUMN)
                    row.append(ERROR_COLUMN)
            else:
                row.append(NULL_COLUMN)
                row.append(NULL_COLUMN)
        return row


    with open('cryptodata.csv', 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for coin in coins:
            write_markets_for_coin(coin, csv_writer)



