__author__ = 'yardenst'
from CryptoCoinChartsApi import API
import csv
from datetime import datetime

# some settings
ALL = 999999999
TRADE_VOLUME_PAIR_FIELD = 'volume_first'  # the field of TRADE VOLUME in the response
PRICE_PAIR_FIELD = 'price'  # the field of PRICE in the response
NULL_COLUMN = 'X'  # what to write on cells of the same pair [usd_usd],[btc_btc]....
ERROR_COLUMN = 'ERR'  # what to write when there is an error getting the data
NO_INFO_COLUMN = 'N/A'  # what to write when there is no data
coins_max = ALL  # how many coins to work on (after the filter, see below)
min_price = 0.001  # will only filter on coins with price > than this
min_volume_btc = 0.001  # will only filter on coins with volume > than this
coins_filter = lambda _coin: (
    float(_coin.price_btc) > min_price and float(_coin.volume_btc) > min_volume_btc)  # the filter func

if __name__ == '__main__':
    api = API()
    api.API_PATH = 'http://api.cryptocoincharts.info/'
    coins = filter(coins_filter, api.listcoins())[:coins_max]
    print("working on %d" % len(coins))

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

    with open('cryptodata-%s.csv' % datetime.now(), 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # write header row
        header_row = ['coin id', 'coin name']
        for coin in coins:
            header_row.append('%s tv' % coin.id)
            header_row.append('%s prc' % coin.id)
        spamwriter.writerow(header_row)
        # write rows
        for coin in coins:
            spamwriter.writerow(write_coin_row(coin))


