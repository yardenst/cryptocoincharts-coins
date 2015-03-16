__author__ = 'yardenst'
from CryptoCoinChartsApi import API
import csv
from datetime import datetime

# some settings
ALL = 999999999
TRADE_VOLUME_PAIR_FIELD = 'volume_first'
PRICE_PAIR_FIELD = 'price'
NULL_COLUMN = 'X'
ERROR_COLUMN = 'ERR'
NO_INFO_COLUMN = 'N/A'
coins_max = ALL
#for filtering the coins list
min_price = 0.001
min_volume_btc = 0.001
coins_filter = lambda _coin: (float(_coin.price_btc) > min_price and float(_coin.volume_btc) > min_volume_btc )

if __name__ == '__main__':
    api = API()
    api.API_PATH = 'http://api.cryptocoincharts.info/'

    #######################################
    # let's save all coins before we start
    #######################################
    coins = filter(coins_filter, api.listcoins())[:coins_max]
    print(len(coins))

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


