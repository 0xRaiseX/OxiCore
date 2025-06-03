import requests
import time
import asyncio
import aiohttp
import hashlib
import hmac
import time
import ccxt
import json
from config import API_KEY, SECRET_KEY
from decimal import Decimal, ROUND_HALF_UP

start_program = time.time()

def time_start():
    seconds = time.time() - start_program 
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    return f"{hours} часов, {minutes} минут, {remaining_seconds} секунд"

async def place_orders_async(orders):
    api_key = API_KEY
    api_secret = SECRET_KEY
    
    base_url = "https://api.binance.com/api/v3/order"
    headers = {
        "X-MBX-APIKEY": api_key
    }

    async def place_order(session, order):
        await asyncio.sleep(0.03)
        try:
            query_string = "&".join([f"{key}={order[key]}" for key in order])
            signature = hmac.new(api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
            order["signature"] = signature
            order['timestamp'] == int((time.time() - 0.10) * 1000) 
      
            async with session.post(base_url, params=order, headers=headers) as response:
                response_json = await response.json()
                if response.status == 200:
                    # print(f"Order placed successfully: {response_json}")
                    pass
                else:
                    print(f"Error placing order: {response_json}")
        except Exception as e:
            print(f"Error placing order: {e}")

    async with aiohttp.ClientSession() as session:
        tasks = [place_order(session, order) for order in orders]
        await asyncio.gather(*tasks)
orders_c = 0

def send_order(orders):
    global orders_c
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(place_orders_async(orders))
    orders_c += 1
    end_time = time.time() - start
    end_time = float("{:.4f}".format(end_time))
    print(f'Время выполнения: {end_time}mc   Шаг ордера: {orders_c}   Время работы: {time_start()}')

def load_lot_size():
    res = requests.get('https://api.binance.com/api/v3/exchangeInfo')
    lot_size = {}
    data = json.loads(res.text)
    for i in data['symbols']:
        symbol = i['symbol']
        lot = i['filters']
        for j in lot:
            if j['filterType'] == 'LOT_SIZE':
                lot_size[symbol] = j['stepSize']
    return lot_size


################# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
def cancel_binance_order(orderId, symbol):
    binance.cancel_order(orderId, symbol)


def round_to_step(value, step):
    value = Decimal(value)
    step = Decimal(step)
    rounded_value = (value / step).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * step
    return rounded_value

def create_order(symbol, price, quantity, side):

    api_key = API_KEY
    api_secret = SECRET_KEY

    base_url = 'https://api.binance.com/api/v3/order'
    headers = {
        'X-MBX-APIKEY': api_key
    }

    step_size = load_lot_size()
    step = step_size[symbol]
   
    timestamp = int(time.time() * 1000)
    payload = {
        'symbol': symbol,
        'side': side,
        'quantity': quantity,
        'price': price,
        'type': 'LIMIT',  
        'timeInForce': 'GTC',  
        'timestamp': timestamp
    }

    query_string = '&'.join([f'{key}={payload[key]}' for key in payload])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    payload['signature'] = signature

    start = time.time()
    order = requests.post(base_url, params=payload, headers=headers)
    end = time.time() - start
    print(end)

    if order.status_code == 200:
        print("Ордер успешно отправлен!")
        print(order.text)
    else:
        print("Произошла ошибка при отправке ордера.")
        print("Статус код:", order.status_code)
        print("Ответ сервера:", order.text)

binance = ccxt.binance({
    'enbaleRateLimit': False,
    'api_key': '',
    'secret': ''
})

def create_binance_market_order(symbol, amount, side):
    start = time.time()
    print('Данные получены: ',symbol, amount, side)
    type = 'market'
    order = binance.create_order(symbol, type, side, amount)
    end = time.time() - start
    print('Время ордера: ', end)

    if side == 'buy':
        return order['info']['executedQty']
    if side == 'sell':
        return order['info']['cummulativeQuoteQty']

def create_binance_FOKorder1(symbol, price, amount, side):
    print('Данные получены: ',symbol, price, amount, side)
    
    type = 'limit'
    start = time.time()
    order = binance.create_order(symbol, type, side, amount, price)
    end = time.time() - start
    print('Время ордера: ', end)
    return order['info']['orderId']
    

def create_binance_FOKorder_FOK(symbol, price, amount, side):
    print('Данные получены: ',symbol, price, amount, side)
    
    type = 'limit'
    start1 = time.time()
    order = binance.create_order(symbol, type, side, amount, price, {'timeInForce': 'FOK'})
    end = time.time() - start1
    print('Время ордера: ', end)

    if order['info']['status'] == 'FILLED':
        if side == 'buy':
            return order['info']['executedQty']
        if side == 'sell':
            return order['info']['cummulativeQuoteQty']
    else:
        return 'CANCEL'

def start_load(data):
    while True:
        if data:
            symbol = ''
            price_symbol = ''
            for i in data.keys():
                if i[-4:] == 'USDT':
                    symbol = i
                    price_symbol = data[i]['ask']
                    break
                else:
                    continue
            amount = 15 / float(price_symbol)
            price = float(price_symbol) - float(price_symbol) * 0.7 / 100
            order = binance.create_order(symbol, 'limit', 'buy', amount, price, {'timeInForce': 'FOK'})
            if order['info']['status'] == 'FILLED':
                print('Начальный ордер исполнен')
                break
            else:
                break

def create_binance_FOKorder_trail(symbol, price, amount, side):
    print('Данные получены: ',symbol, price, amount, side)
    
    type = 'STOP'
    trail_stop = 0.5
    start = time.time()
    order = binance.create_order(symbol, type, side, amount, price, params={'stopPrice': price, 'close': 'last_price', 'trailValue': trail_stop})
    end = time.time() - start
    print('Время ордера: ', end)
    return order['info']['orderId']
