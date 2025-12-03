# 📡 MQL Bridge - MetaTrader ↔ Python Communication

Bu klasör, Python trading botunun MT4 ve MT5 ile iletişim kurmasını sağlayan Expert Advisor (EA) kodlarını içerir.

---

## 📁 Dosyalar

### 1. `PythonBridge_MT5.mq5`
**MetaTrader 5 Expert Advisor**
- Socket tabanlı gerçek zamanlı iletişim
- JSON formatında veri alışverişi
- Otomatik reconnection

### 2. `PythonBridge_MT4.mq4`
**MetaTrader 4 Expert Advisor**
- Dosya tabanlı iletişim (MT4 socket desteği yok)
- JSON formatında veri alışverişi
- `Experts/Files/` klasörü üzerinden çalışır

---

## 🚀 Kurulum

### MT5 Kurulumu:

1. **MQ5 dosyasını kopyala:**
   ```
   PythonBridge_MT5.mq5 → MetaTrader5/MQL5/Experts/
   ```

2. **MetaEditor'de aç ve derle** (F7)

3. **Grafiğe sürükle:**
   - XAUUSD (veya istediğin sembol) grafiğini aç
   - Navigator'dan EA'yı grafiğe sürükle
   
4. **Ayarlar:**
   - `PythonHost`: `127.0.0.1` (varsayılan)
   - `PythonPort`: `9090` (Python server portu)
   - `MagicNumber`: `234000`
   - `EnableAutoTrading`: `true`
   - **Allow DLL imports**: ✅ İşaretle
   - **Allow Live Trading**: ✅ İşaretle

### MT4 Kurulumu:

1. **MQ4 dosyasını kopyala:**
   ```
   PythonBridge_MT4.mq4 → MetaTrader4/MQL4/Experts/
   ```

2. **MetaEditor'de aç ve derle** (F7)

3. **Grafiğe sürükle:**
   - XAUUSD grafiğini aç
   - Navigator'dan EA'yı grafiğe sürükle

4. **Ayarlar:**
   - `MagicNumber`: `234000`
   - `EnableAutoTrading`: `true`
   - **Allow DLL imports**: ✅ İşaretle
   - **Allow Live Trading**: ✅ İşaretle

---

## 📡 İletişim Protokolü

### MT5 → Python (Socket)

**Market Data (Her tick'te):**
```json
{
  "type": "market_data",
  "symbol": "XAUUSD",
  "bid": 2645.50,
  "ask": 2645.70,
  "spread": 20,
  "time": "2025-12-03 14:30:25",
  "point": 0.01,
  "digits": 2,
  "contract_size": 100.0,
  "min_lot": 0.01,
  "max_lot": 100.0,
  "lot_step": 0.01,
  "balance": 11541.25,
  "equity": 11650.30,
  "margin": 500.00,
  "free_margin": 11150.30,
  "profit": 109.05,
  "leverage": 500,
  "open_positions": 1
}
```

**Position Data (Talep üzerine):**
```json
{
  "type": "position",
  "ticket": 123456789,
  "symbol": "XAUUSD",
  "pos_type": "BUY",
  "volume": 0.06,
  "price_open": 2645.20,
  "price_current": 2647.80,
  "sl": 2627.00,
  "tp": 2682.00,
  "profit": 156.00,
  "comment": "Bot trade"
}
```

**Heartbeat (Her 5 saniyede):**
```json
{
  "type": "heartbeat",
  "time": "2025-12-03 14:30:25",
  "status": "alive"
}
```

### Python → MT5 (Socket)

**BUY Emri:**
```json
{
  "action": "BUY",
  "symbol": "XAUUSD",
  "volume": 0.06,
  "sl": 2627.00,
  "tp": 2682.00,
  "comment": "Uptrend detected"
}
```

**SELL Emri:**
```json
{
  "action": "SELL",
  "symbol": "XAUUSD",
  "volume": 0.06,
  "sl": 2664.00,
  "tp": 2609.00,
  "comment": "Downtrend detected"
}
```

**Pozisyon Kapat:**
```json
{
  "action": "CLOSE",
  "ticket": 123456789
}
```

**SL/TP Değiştir:**
```json
{
  "action": "MODIFY",
  "ticket": 123456789,
  "sl": 2630.00,
  "tp": 2685.00
}
```

**Pozisyonları Al:**
```json
{
  "action": "GET_POSITIONS"
}
```

**Geçmiş Veriler:**
```json
{
  "action": "GET_RATES",
  "count": 100,
  "timeframe": 15
}
```

---

## 🔧 MT4 Dosya İletişimi

MT4 socket desteği olmadığı için dosya tabanlı iletişim kullanır:

### Dosya Konumları:
```
MetaTrader4/MQL4/Files/
├── mt4_market_data.json      → MT4 market verilerini yazar
├── mt4_positions.json        → MT4 pozisyon bilgileri
├── mt4_rates.json            → Geçmiş fiyat veriler
├── mt4_heartbeat.json        → Heartbeat sinyali
├── mt4_response.json         → İşlem sonuçları
└── python_commands.json      → Python komutları (Python yazar)
```

### Python Kullanımı:

**Market verilerini oku:**
```python
import json

with open('MetaTrader4/MQL4/Files/mt4_market_data.json', 'r') as f:
    data = json.load(f)
    print(f"Bid: {data['bid']}, Ask: {data['ask']}")
```

**Komut gönder:**
```python
command = {
    "action": "BUY",
    "volume": 0.06,
    "sl": 2627.00,
    "tp": 2682.00,
    "comment": "Python bot"
}

with open('MetaTrader4/MQL4/Files/python_commands.json', 'w') as f:
    json.dump(command, f)
```

---

## 🎯 Python Entegrasyon Örneği

### MT5 Socket Sunucusu:

```python
import socket
import json
import threading

class MT5Bridge:
    def __init__(self, host='127.0.0.1', port=9090):
        self.host = host
        self.port = port
        self.server = None
        self.client = None
        self.market_data = {}
        
    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        print(f"✅ Listening on {self.host}:{self.port}")
        
        self.client, addr = self.server.accept()
        print(f"✅ MT5 connected from {addr}")
        
        # Start receiving thread
        thread = threading.Thread(target=self.receive_data)
        thread.daemon = True
        thread.start()
    
    def receive_data(self):
        buffer = ""
        while True:
            try:
                data = self.client.recv(4096).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                # Process complete JSON messages (ending with \n)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.process_message(json.loads(line))
            except Exception as e:
                print(f"Error: {e}")
                break
    
    def process_message(self, msg):
        msg_type = msg.get('type')
        
        if msg_type == 'market_data':
            self.market_data = msg
            print(f"📊 {msg['symbol']}: Bid={msg['bid']}, Ask={msg['ask']}")
        
        elif msg_type == 'position':
            print(f"📍 Position: {msg['pos_type']} {msg['volume']} lots, P/L=${msg['profit']}")
        
        elif msg_type == 'heartbeat':
            print(f"💓 Heartbeat: {msg['status']}")
    
    def send_buy_order(self, volume, sl, tp, comment=""):
        command = {
            "action": "BUY",
            "volume": volume,
            "sl": sl,
            "tp": tp,
            "comment": comment
        }
        self.send_command(command)
    
    def send_sell_order(self, volume, sl, tp, comment=""):
        command = {
            "action": "SELL",
            "volume": volume,
            "sl": sl,
            "tp": tp,
            "comment": comment
        }
        self.send_command(command)
    
    def close_position(self, ticket):
        command = {
            "action": "CLOSE",
            "ticket": ticket
        }
        self.send_command(command)
    
    def send_command(self, command):
        try:
            msg = json.dumps(command) + '\n'
            self.client.send(msg.encode('utf-8'))
            print(f"📤 Sent: {command['action']}")
        except Exception as e:
            print(f"Error sending: {e}")

# Kullanım
bridge = MT5Bridge()
bridge.start()

# Uptrend tespit edildiğinde
bridge.send_buy_order(volume=0.06, sl=2627.00, tp=2682.00, comment="Uptrend")
```

---

## ⚙️ Konfigürasyon

### trade_config.json'a ekle:

```json
{
  "broker": {
    "platform": "MT5",
    "connection": "socket",
    "host": "127.0.0.1",
    "port": 9090,
    "magic_number": 234000
  }
}
```

Veya MT4 için:

```json
{
  "broker": {
    "platform": "MT4",
    "connection": "file",
    "files_path": "C:/Users/YourName/AppData/Roaming/MetaQuotes/Terminal/XXXX/MQL4/Files/",
    "magic_number": 234000
  }
}
```

---

## 🔍 Sorun Giderme

### MT5 bağlanamıyor:

1. **Python server çalışıyor mu?**
   ```python
   python mt5_bridge_server.py
   ```

2. **Firewall portu engelliyor mu?**
   - Windows Firewall'da 9090 portunu aç

3. **EA loglarını kontrol et:**
   - MT5: Tools → Options → Expert Advisors → Journal
   - "ERROR: Failed to connect" mesajı varsa Python server çalışmıyor

### MT4 dosya yazamıyor:

1. **Dosya yolu doğru mu?**
   ```
   C:\Users\[USERNAME]\AppData\Roaming\MetaQuotes\Terminal\[BROKER_ID]\MQL4\Files\
   ```

2. **Yazma izni var mı?**
   - Klasöre sağ tık → Properties → Security → Tam izin ver

3. **EA çalışıyor mu?**
   - Grafikte sağ üstte gülen smiley olmalı 😊

---

## 📊 Avantajlar

### ✅ Broker Bağımsız:
- MT5 değiştirirsen sadece EA'yı yeniden yükle
- MT4'e geçiş yapabilirsin
- Farklı brokerlarla aynı Python kodunu kullan

### ✅ Python'da Tüm Kontrol:
- Karmaşık stratejiler Python'da
- Machine learning modelleri entegre et
- Kolay test ve debugging

### ✅ Gerçek Zamanlı:
- Socket ile milisaniye gecikme
- Tick bazında veri akışı
- Anında işlem iletimi

---

## 🎓 Sonraki Adımlar

1. **Python bridge server'ı oluştur** (`src/mt5_bridge_server.py`)
2. **TradingBot'u güncelle** (MQL bridge kullan)
3. **Test et:** Demo hesapta dene
4. **İzle:** Dashboard'dan takip et

---

**Not:** Bu EA'lar production-ready değil, temel bir bridge sağlar. Güvenlik, hata yönetimi ve performans optimizasyonları eklenebilir.
