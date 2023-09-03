import asyncio
import websockets
import json
import requests
import asyncio
import json
from time import time

shared_dict = {}

def get_symbols_connect():
    global tickers
    connect = []
    connections = 800
    iteration = 0 
    for i in tickers:
        if iteration != connections:
            connect.append(i)
            iteration += 1
            tickers.remove(i)

    return connect

def get_symbols_websocket_connect():
    res = requests.get('https://api.binance.com/api/v3/exchangeInfo')
    symbols = json.loads(res.text)
    symbols = symbols['symbols']

    symbols_res = []
    for i in symbols:
        symbols_res.append(i['symbol'])

    return symbols_res

tickers = get_symbols_websocket_connect()


async def connect_first_websocket(queue):
    await asyncio.sleep(5)
    symbols = get_symbols_connect()

    url = "wss://stream.binance.com:9443/ws"

    for i in symbols:
        url_add = f'/{i.lower()}@bookTicker'
        url = url+url_add


    while True:
        print('Connect 1. Подключаюсь к серверу...')
        try:
            async with websockets.connect(url) as websocket:
                while True:
                    message = await websocket.recv()
                    data_json = json.loads(message)                    
                    try:
                        shared_dict[data_json['s']] = {
                                'bid': data_json['b'], 
                                'ask': data_json['a'], 
                                'askVolume': data_json['A'], 
                                'bidVolume': data_json['B']
                            }
                   
                        try:
                            queue.put(shared_dict, block=False)
                        except Exception:
                            continue
                    except KeyError:
                        continue

        except (websockets.ConnectionClosed, websockets.exceptions.InvalidStatusCode, TimeoutError):
            print('Websocket 1. Connection closed. Reconnection...')
            await asyncio.sleep(5)


async def connect_second_websocket(queue):
    await asyncio.sleep(10)

    symbols = get_symbols_connect()
    url = "wss://stream.binance.com:9443/ws"

    for i in symbols:
        url_add = f'/{i.lower()}@bookTicker'
        url = url+url_add

   
    while True:
        print('Connect 2. Подключаюсь к серверу...')
        try:
            async with websockets.connect(url) as websocket:
                while True:
                    message = await websocket.recv()
                    data_json = json.loads(message)
                    try:
                        shared_dict[data_json['s']] = {
                                'bid': data_json['b'], 
                                'ask': data_json['a'], 
                                'askVolume': data_json['A'], 
                                'bidVolume': data_json['B']
                            }
                        # try:
                        #     queue.get(block=False)
                        # except Exception:
                        #     continue
                        try:
                            queue.put(shared_dict, block=False)            
                        except Exception:
                            continue
                    except KeyError:
                        continue
                    
        except (websockets.ConnectionClosed, websockets.exceptions.InvalidStatusCode, TimeoutError):
            print('Websocket 2. Connection closed. Reconnecting...')
            await asyncio.sleep(5)
            continue

async def connect_websocket3(queue):
    await asyncio.sleep(15)
    symbols = tickers

    url = "wss://stream.binance.com:9443/ws"
    for i in symbols:  
        url_add = f'/{i.lower()}@bookTicker'
        url = url+url_add

    while True:
        print('Connect 3. Подключаюсь к серверу...')
        try:
            async with websockets.connect(url) as websocket:

                while True:
                    message = await websocket.recv()
                    data_json = json.loads(message)
                    try:
                        shared_dict[data_json['s']] = {
                            'bid': data_json['b'], 
                            'ask': data_json['a'], 
                            'askVolume': data_json['A'], 
                            'bidVolume': data_json['B']
                        }
                       
                        try:
                            queue.put(shared_dict, block=False)
                        except Exception:
                            continue
                    except KeyError:
                        continue   

        except (websockets.ConnectionClosed, websockets.exceptions.InvalidStatusCode, TimeoutError):
            print('Websocket 3. Connection closed. Reconnecting...')
            await asyncio.sleep(5)
            continue


async def subscribe_to_user_trades():
    listen_key = get_listen_key()
    uri = f"wss://stream.binance.com:9443/ws/{listen_key}"
    symbols_tag = {}
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                if data["e"] == "executionReport":
                    if data['X'] == 'FILLED':
                        key = f'{data["s"]}FILLED'
                        try:
                           
                            tag = symbols_tag[key]
                            tag = int(tag) + 1
                        except KeyError:
                            tag = 0
                        shared_dict[key] = {
                                'tag': tag,
                                'symbol': data['s'], 
                                'price': data['p'], 
                                'quantity': data['q'], 
                                'quantity2': data['Z'], 
                                'side': data['S']
                            }
                        symbols_tag[key] = tag
                
                    # print(f"Symbol: {data['s']}, Price: {data['p']}, Quantity: {data['q']}, Side: {data['S']}")
            except (websockets.ConnectionClosed, websockets.exceptions.InvalidStatusCode, TimeoutError):
                await asyncio.sleep(5)
                continue

def get_listen_key():
    api_key = 'lWTBXXMNTUcKXaqekyoq4kswEtfur0gdUVOPE4WYeiFuK1dBfIT21TG7KMNxVsXL'
    listen_key_url = "https://api.binance.com/api/v3/userDataStream"
    headers = {
        "X-MBX-APIKEY": api_key
    }
    response = requests.post(listen_key_url, headers=headers)
    data = response.json()
    return data["listenKey"]


async def update_queue(queue):
    while True:
            try:
                start = time()
                queue.put(shared_dict, block=False)
                print(time() - start)
                await asyncio.sleep(0.001)
            except Exception:
                pass
        


def load_symbols():
    res = requests.get('https://api.binance.com/api/v3/ticker/bookTicker')
    data = json.loads(res.text)

    symbols_new = []
    for i in data:
        if float(i['bidPrice']) != 0:
            symbols_new.append(i['symbol'])

    cancel = ['BUSDNGN', ] 
    for i in data:
        if float(i['bidPrice']) != 0 or float(i['askPrice']) != 0.0:
            if i['symbol'] not in cancel and i['symbol'][-3:] != 'NGN':
                shared_dict[i['symbol']] = {
                    'bid': i['bidPrice'], 
                    'ask': i['askPrice'],
                    'askVolume': i['askQty'], 
                    'bidVolume': i['bidQty']
                }
                print('Symbol: ', i['symbol'], 'Ask: ', i['askPrice'], 'Bid: ', i['bidPrice'])


async def main(queue, queue1, queue2, queue3):
    load_symbols()
    await asyncio.gather(connect_first_websocket(queue1), connect_second_websocket(queue2), connect_websocket3(queue3), subscribe_to_user_trades())
    # await asyncio.gather(connect_first_websocket(), connect_second_websocket(), update_queue(queue),)


def start_process(queue, queue1,queue2,queue3):
    asyncio.run(main(queue, queue1, queue2, queue3))


