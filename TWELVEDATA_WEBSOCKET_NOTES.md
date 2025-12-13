# TwelveData WebSocket Implementation

## API Key
**Hardcoded**: `5e7a5daaf41d46a8966963106ebef210`

## WebSocket URL
```
wss://ws.twelvedata.com/v1/{route}?apikey=your_api_key
```

Or pass API key separately in header:
```
X-TD-APIKEY: your_api_key
```

## Real-Time Price Streaming

### Endpoint
```
wss://ws.twelvedata.com/v1/quotes/price?apikey=5e7a5daaf41d46a8966963106ebef210
```

### Features
- Real-time price streaming from exchange
- Equities include day volume information
- 1 per symbol, API credits are NOT used

### Subscribe to Multiple Symbols
```json
{
  "action": "subscribe",
  "params": {
    "symbols": "AAPL,RY,RY:TSX,EUR/USD,BTC/USD"
  }
}
```

### Subscribe Using Extended Format
```json
{
  "action": "subscribe",
  "params": {
    "symbols": [{
      "symbol": "AAPL",
      "exchange": "NASDAQ"
    }, {
      "symbol": "RY",
      "mic_code": "XNYS"
    }, {
      "symbol": "EUR/USD",
      "type": "Forex"
    }]
  }
}
```

### Response Structure

**Two Event Types:**
1. `status` - Subscription confirmation
2. `price` - Real-time tick prices

**Price Event Fields:**
- `event`: type of event
- `symbol`: symbol ticker of instrument
- `type`: general instrument type
- `timestamp`: timestamp in UNIX format
- `price`: real-time tick price
- `day_volume`: day volume (equities only)

### Example Price Event
```json
{
  "event": "price",
  "symbol": "AAPL",
  "type": "Stock",
  "timestamp": 1639152000,
  "price": 175.32,
  "day_volume": 12345678
}
```

## WebSocket Limitations

- Server limits to receive up to **100 events** from client-side
- No limit on number of input symbols
- Input message size cannot exceed **1 MB**
- Up to **3 connections** (typically used in production, stage, and local environments)
- Full access available for users on **Pro plan and above**
- Testing can be done on Basic and Grow tier plans with only one symbol

## Implementation Strategy

### For Oracle Scanner

1. **Connection Management**
   - Establish websocket connection on app startup
   - Maintain persistent connection
   - Reconnect on disconnect with exponential backoff

2. **Symbol Subscription**
   - Subscribe to symbol when user analyzes a stock
   - Unsubscribe from previous symbol to stay within limits
   - Use extended format for precise exchange matching

3. **Real-Time Data Processing**
   - Receive price ticks in real-time
   - Calculate VWAP from tick data
   - Update support/resistance levels dynamically
   - Track intraday action (close position in range)

4. **VWAP Calculation**
   - Accumulate: `(price × volume)` for each tick
   - Accumulate: `total_volume`
   - VWAP = `sum(price × volume) / total_volume`
   - Reset at market open (9:30 AM EST)

5. **Intraday Range Tracking**
   - Track daily high and low
   - Calculate current position: `(current_price - low) / (high - low)`
   - Determine if close is in top 20% of range

## Python Implementation

### Using websockets library

```python
import websockets
import json
import asyncio

API_KEY = "5e7a5daaf41d46a8966963106ebef210"
WS_URL = f"wss://ws.twelvedata.com/v1/quotes/price?apikey={API_KEY}"

async def stream_prices(symbol):
    async with websockets.connect(WS_URL) as websocket:
        # Subscribe to symbol
        subscribe_msg = {
            "action": "subscribe",
            "params": {
                "symbols": symbol
            }
        }
        await websocket.send(json.dumps(subscribe_msg))
        
        # Receive real-time data
        async for message in websocket:
            data = json.loads(message)
            
            if data.get('event') == 'price':
                price = data['price']
                volume = data.get('day_volume', 0)
                timestamp = data['timestamp']
                
                print(f"{symbol}: ${price} | Volume: {volume}")
                
                # Process for VWAP, support/resistance, etc.
                # ...

# Run
asyncio.run(stream_prices("AAPL"))
```

### Integration with Streamlit

**Challenge:** Streamlit is synchronous, websockets are asynchronous

**Solution:** Use threading or background tasks

```python
import threading
import queue

# Global queue for price updates
price_queue = queue.Queue()

def websocket_thread(symbol):
    async def stream():
        async with websockets.connect(WS_URL) as ws:
            subscribe_msg = {
                "action": "subscribe",
                "params": {"symbols": symbol}
            }
            await ws.send(json.dumps(subscribe_msg))
            
            async for message in ws:
                data = json.loads(message)
                if data.get('event') == 'price':
                    price_queue.put(data)
    
    asyncio.run(stream())

# Start websocket in background
thread = threading.Thread(target=websocket_thread, args=("AAPL",))
thread.daemon = True
thread.start()

# In Streamlit, check queue for updates
if not price_queue.empty():
    latest_price = price_queue.get()
    st.write(f"Real-time price: ${latest_price['price']}")
```

## Alternative: Use REST API for Now

**For MVP, use REST API instead of websocket:**

1. **Advantages:**
   - Simpler implementation
   - No threading complexity
   - Works well with Streamlit
   - Sufficient for single-stock analysis

2. **Disadvantages:**
   - Not true real-time (delayed by API call)
   - Uses API credits
   - Slower than websocket

**REST Endpoint:**
```
https://api.twelvedata.com/price?symbol=AAPL&apikey=5e7a5daaf41d46a8966963106ebef210
```

**Response:**
```json
{
  "price": "175.32"
}
```

## Recommendation

**Phase 2A: Use REST API for now**
- Simpler, faster to implement
- Works seamlessly with Streamlit
- Good enough for Oracle Scanner MVP

**Phase 2B: Add websocket later**
- For multi-stock scanning
- For real-time dashboard updates
- When scaling to multiple users

## Next Steps

1. Implement REST API price fetching
2. Add VWAP calculation from intraday data
3. Track intraday high/low/close
4. Calculate close position in range
5. Save websocket implementation for future enhancement
