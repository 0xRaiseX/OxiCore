### STREAM ПАРА 1 /USDT

import requests
import time
import json
from create_order import create_order, create_binance_market_order

def get_symbols_websocket_connect():
    res = requests.get('https://api.binance.com/api/v3/exchangeInfo')
    symbols = json.loads(res.text)
    symbols = symbols['symbols']
    
    curr = [i['baseAsset'] for i in symbols]
    
    tickers_dict = {}
    for i in curr:
        tickers_dict[i] = [j['symbol'] for j in symbols if j['baseAsset'] == i]
    
    tickers_all = []
    for tickers_add in tickers_dict.values():
        tickers_all.append([j for j in tickers_add])

    tickers_iteration = []
    for iteration in tickers_all:
        for symbol in iteration:
            if symbol[-4:] == 'USDT':
                for symbol2 in iteration:
                    if symbol != symbol2:
                        tickers_iteration.append([symbol, symbol2])
 
    return tickers_iteration


def settings_connect():
    res = requests.get('https://api.binance.com/api/v3/exchangeInfo')
    symbols = json.loads(res.text)

    settings = {}
    for i in symbols['symbols']:
        settings[i['symbol']] = {
            'symbol': i['baseAsset'],
            'symbol1': i['quoteAsset'],
        }  

    return settings
            

def symbols_webscoket_exchange(queue):
    symbols = get_symbols_websocket_connect()
    settings = settings_connect()
    print('Stream 1 запущен')
    while True:

        data = queue.get()
        errors = 0
        iter = 0
        start = time.time()
        for iteration in symbols:

            symbol = iteration[0]
            symbol2 = iteration[1]
            try:

                pair2 = settings[symbol2]
                
                symbol_price = data[symbol]['ask']
                symbol2_price = data[symbol2]['bid']

                try:

                    pair3 = pair2['symbol1'] + 'USDT'
                    pair3_price = data[pair3]['bid']
                    symbol3_price = float(symbol2_price) * float(pair3_price)

                except KeyError:

                    pair3 = 'USDT' + pair2['symbol1']
                    pair3_price = data[pair3]['ask']
                    symbol3_price = float(symbol2_price) / float(pair3_price)

                end = 100 - float(symbol_price) / symbol3_price * 100
                # print(end, symbol, symbol2)
                if end > 0.225:
                    # print('Stream 1: ',end, symbol, symbol2)
                    continue
                    symbol1 = symbol
                    symbol2 = symbol2
                    
                    amount_symbol = 15 / float(symbol_price)
                    symbol_step_amount = create_order(symbol1, symbol_price, amount_symbol, 'buy')

                    if symbol_step_amount == 'CANCEL':
                        continue

                    symbol2_step2_amount = create_order(symbol2, symbol2_price, symbol_step_amount, 'sell')
                    if symbol2_step2_amount == 'CANCEL':
                        create_binance_market_order(symbol1, symbol_step_amount, 'sell')
                        print('Stream 1  Step 2. Стоп по цене')
                        continue
                    

                    symbol3_step3_amount = create_order(pair3, pair3_price, symbol2_step2_amount, 'sell')

                    if symbol3_step3_amount == 'CANCEL':
                        create_binance_market_order(pair3, symbol2_step2_amount, 'sell')
                        print('Stream 1  Step 3. Стоп по цене')
                        continue
                    print('Stream 1  Все оредра выполнены')


                iter += 1

            except KeyError:
                errors += 1
                continue 

    
        end = time.time() - start
        # print('Stream 1  Итераций: ',iter)
        # print('Stream 1  Время: ',end)
        # print('Stream 1  Длинна данных: ', len(data.keys()))

def mon(queue):

    while True:
        try:
            a = queue.get()
            b = a['BTCUSDT']
            print('Ask: ', b['ask'])
            print('Bid: ',b['bid'])
            # if ask != a['WTCBTC']['ask'] or bid != a['WTCBTC']['bid']:
            #     ask = a['WTCBTC']['ask']
            #     bid = a['WTCBTC']['bid']
            #     print('Ask: ', a['WTCBTC']['ask'])
            #     print('Bid: ',a['WTCBTC']['bid'])
            time.sleep(1)
        except KeyError:
            continue
                        


def start_stream_1(data):

    symbols_webscoket_exchange(data)

