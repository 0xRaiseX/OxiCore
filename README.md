# OxiCore (LEGACY)

> ⚠️ Legacy repository — kept for historical and educational purposes.

## 📌 Description

OxiCore is an early experimental core for automated trading on a cryptocurrency exchange.  
It connects to the exchange via WebSocket, receives real-time market data, and can automatically place buy/sell orders.

The project uses multiprocessing to handle parallel tasks. While this was an interesting approach at the time, a modern version would likely use asyncio for better efficiency and scalability.

This is not a production-ready solution. The code is kept as part of my learning journey and as a snapshot of how I explored parallel computing in Python.

---

## ⚙️ Main Features

- Connects to an exchange via WebSocket
- Parses and processes real-time market data
- Algorithmically places trading orders
- Uses multiprocessing for task execution

---

## ❗️Why Legacy?

This was one of my early attempts at writing a trading core.  
Today, I understand that:

- asyncio would be a more appropriate tool
- The architecture needs simplification
- Concepts like resilience, logging, and scaling need rethinking

I still value this code as part of my development process and curiosity-driven learning.

---

## 🧠 Lessons Learned

- WebSocket usage in Python
- Basics of algorithmic trading
- Parallel processing with multiprocessing
- The limitations of native architecture

---

## 🗃️ Tech Stack

- Python 3.x
- multiprocessing
- websockets
- requests
- httpx
- ccxt
- Binance API

---

## 🚧 Status

Not maintained  
Code is provided "as is" — expect bugs, inefficiencies, and outdated patterns.

---

## 🧾 License

[MIT](./LICENSE) — free to use for learning and experimentation.
