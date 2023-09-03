import requests
import time
import json
from create_order import create_binance_FOKorder_FOK, create_binance_market_order, cancel_binance_order

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
            for symbol2 in iteration:
                if symbol2[-4:] == 'USDT':
                    if symbol != symbol2:
                        tickers_iteration.append([symbol, symbol2])

    return tickers_iteration
profit = {}
def print_orders(symbol1, symbol2, symbol3, prochent, symbol4=None):
    if symbol4:
        prochent -= 0.3
        prochent_new = float("{:.3f}".format(prochent))
        profit['all'] += prochent_new
        print(f'-------------------------------Orders-------------------------------\n{symbol1} -> {symbol2} -> {symbol3} -> {symbol4}               Profit: + {prochent_new}%({profit["all"]}%)\n\n                      All orders have been placed! ')
    else:
        prochent -= 0.225
        prochent_new = float("{:.3f}".format(prochent))
        profit['all'] += prochent_new
        print(f'-------------------------------Orders-------------------------------\n{symbol1} -> {symbol2} -> {symbol3}              Profit: + {prochent_new}%({profit["all"]}%)\n\n                   All orders have been placed! ')


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
    print('Stream 2 запущен')
    while True:
        data = queue.get()
        start = time.time()
        for iteration in symbols:

            symbol = iteration[0]
            symbol2 = iteration[1]
            try:
                
                pair2 = settings[symbol]
                
                symbol_price = data[symbol]['ask']
                symbol2_price = data[symbol2]['bid']

                try:

                    pair3 = pair2['symbol1'] + 'USDT'
                    pair3_price = data[pair3]['ask']
                    symbol3_price = float(symbol_price) * float(pair3_price)

                except KeyError:

                    pair3 = 'USDT' + pair2['symbol1']
                    pair3_price = data[pair3]['bid']
                    symbol3_price = float(symbol_price) / float(pair3_price)
            
                end = 100 - symbol3_price / float(symbol2_price) * 100
             
                if end > 0.225:        
                    print('Stream 2: ',end, symbol, symbol2)

                    pair3_side = ''
                    if pair3[-4:] == 'USDT':
                        pair3_side = 'buy'
                        pair3_amount = 15 / float(pair3_price)
                    else:
                        pair3_side = 'sell'
                        pair3_amount = 15 

                    symbol3_step_amount = create_binance_FOKorder_FOK(pair3, pair3_price, pair3_amount, pair3_side)
                    # create_binance_market_order(pair3, pair3_amount, pair3_side)
                    if symbol3_step_amount == 'CANCEL':
                        print('Stream 2. Step 1. Стоп по цене')
                        queue.get()
                        continue
                    
                    if pair3_side == 'buy':
                        symbol_amount = float(symbol3_step_amount) / float(symbol_price) 
                    else:
                        symbol_amount = float(symbol3_step_amount) / float(symbol_price) 

                    symbol_step2_amount = create_binance_FOKorder_FOK(symbol, symbol_price, symbol_amount, 'buy')
                    if symbol_step2_amount == 'CANCEL':
                        print('Stream 2. Step 2. Стоп по цене')
                        side = ''
                        if pair3_side == 'buy':
                            side = 'sell'
                        else:
                            side = 'buy'
                        create_binance_market_order(pair3, pair3_amount, side)
                        queue.get()
                        continue

                    
                    symbol2_step3_amount = create_binance_FOKorder_FOK(symbol2, symbol2_price, symbol_step2_amount, 'sell')
                    if symbol2_step3_amount == 'CANCEL':
                        print('Stream 2. Step 3. Стоп по цене')
                        create_binance_market_order(symbol2, symbol_step2_amount, 'sell')
                        queue.get()
                        continue
                    
                    print_orders(symbol, symbol2, pair3, end)
                    print('Stream 2  Все ордера выполнены')
        
            except KeyError:
                continue 

    
        end = time.time() - start
        # print('Stream 2  Итераций: ',iter)
        # print('Stream 2  Время: ',end)


def mon(queue):
    ask = 0
    bid = 0
    while True:
        try:
            a = queue.get()
            b = a['FILLED']
            print(b)
            time.sleep(1)
        except KeyError:
            continue
                        
def start_stream_2(queue):
    symbols_webscoket_exchange(queue)




