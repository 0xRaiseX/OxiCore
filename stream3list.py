import requests
import time
import json
from create_order import create_order, create_binance_market_order





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


def get_symbols_websocket_connect():
    settings = settings_connect()
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

    P = set(i for j in tickers_all for i in j)

    tickers_iteration = []
    for iteration in tickers_all:
        for symbol in iteration:
            if symbol[-4:] != 'USDT':
                for symbol2 in iteration:
                    if symbol2[-4:] != 'USDT':
                        if symbol != symbol2:
                            tickers_iteration.append([symbol, symbol2])

    symbols_dict_list = []

    for iteration in tickers_iteration:
        symbol = iteration[0]
        symbol2 = iteration[1]

        pair1 = settings[symbol]
        pair2 = settings[symbol2]

        type_pair = 0
        pair3 = pair1['symbol1'] + 'USDT'

        if pair3 not in P:
            pair3 = 'USDT' + pair1['symbol1']
            type_pair = 1 
        
        type_pair2 = 0
        pair4 = pair2['symbol1'] + 'USDT'

        if pair4 not in P:
            pair4 = 'USDT' + pair2['symbol1']
            type_pair2 = 1 

        symbols_dict_list.append([symbol, symbol2, pair3, pair4, type_pair, type_pair2])


    return symbols_dict_list
            

def symbols_webscoket_exchange(queue):

    symbols = get_symbols_websocket_connect()
    print('Stream 3 запущен')

    while True:
        data = queue.get()
        iter = 0
        start = time.time()

        for iteration in symbols:
           
            symbol = iteration[0]
            symbol2 = iteration[1]

            try:

                symbol_price = data[symbol]['ask']
                symbol2_price = data[symbol2]['bid']

                pair3 = iteration[2]
                if iteration[4] == 0:

                    pair3_price = data[pair3]['ask']
                    symbol3_price = float(symbol_price) * float(pair3_price)

                else:
        
                    pair3_price = data[pair3]['bid']
                    symbol3_price = float(symbol_price) / float(pair3_price)
                
                pair4 = iteration[3]
                if iteration[5] == 0:

                    pair4_price = data[pair4]['bid']
                    symbol4_price = float(symbol2_price) * float(pair4_price)

                else:

                    pair4_price = data[pair4]['ask']
                    symbol4_price = float(symbol2_price) / float(pair4_price)

                end = 100 - symbol3_price / symbol4_price * 100
                # print(end, symbol, symbol2)
                
                iter += 1
                if end > 0.3:
                    # print('Stream 3: ', end, symbol, symbol2)
                    continue

                    amount = 15 / float(pair3_price)
                    symbol3_step_amount = create_binance_FOKorder(pair3, pair3_price, amount, 'buy')

                    if symbol3_step_amount == 'CANCEL':
                        continue
                    amount_symbol = amount / float(symbol_price)
                    symbol_step2_amount = create_binance_FOKorder(symbol, symbol_price, amount_symbol, 'buy')

                    if symbol_step2_amount == 'CANCEL':
                        create_binance_market_order(pair3, amount, 'sell')
                        print('Stream 3  Step 2. Стоп по цене')
                        continue

                    symbol2_step3_amount = create_binance_FOKorder(symbol2, symbol2_price, symbol_step2_amount, 'sell')

                    if symbol2_step3_amount == 'CANCEL':
                        create_binance_market_order(symbol, amount_symbol, 'sell')
                        create_binance_market_order(pair3, amount, 'sell')
                        print('Stream 3  Step 3. Стоп по цене')
                        continue

                    symbol4_step4_amount = create_binance_FOKorder(pair4, pair4_price, symbol2_step3_amount, 'sell')
                    if symbol4_step4_amount == 'CANCEL':
                        create_binance_market_order(pair4, symbol2_step3_amount, 'sell')
                        print('Stream 3  Step 4. Стоп по цене')
                        continue
                    print('Stream 3  Все ордера исполнены')
            except KeyError:
     
                continue 

    
        end = time.time() - start
        # print('Stream 3  Итераций: ',iter)
        # print('Stream 3  Время: ',end)
  


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
                     

                        
def start_stream_3(queue):

    symbols_webscoket_exchange(queue)

