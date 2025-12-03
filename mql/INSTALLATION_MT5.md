# 🚀 MT5 Expert Advisor (EA) Kurulum Rehberi

Bu rehber, `PythonBridge_MT5.mq5` Expert Advisor'ı MT5'e kurmanız için adım adım talimatlar içerir.

---

## 📋 Gereksinimler

- ✅ MetaTrader 5 yüklü olmalı
- ✅ Demo veya Live hesap açılmış olmalı
- ✅ Python bridge server hazır olmalı (port 9090)

---

## 🔧 ADIM 1: MQ5 Dosyasını Kopyala

### 1.1 MT5 Data Klasörünü Bul

1. **MetaTrader 5'i aç**

2. **Üst menüden:**
   ```
   File → Open Data Folder
   ```
   
3. **Klasör açılacak**, örnek yol:
   ```
   C:\Users\[KULLANICI_ADIN]\AppData\Roaming\MetaQuotes\Terminal\[BROKER_ID]\
   ```

### 1.2 MQ5 Dosyasını Expert Advisors Klasörüne Kopyala

1. **Açılan klasörde şu yolu takip et:**
   ```
   MQL5 → Experts
   ```

2. **`PythonBridge_MT5.mq5` dosyasını bu klasöre kopyala:**
   ```
   Kaynak:
   C:\Mac\Home\Desktop\Finans\trade\trade-algo-gold\mql\PythonBridge_MT5.mq5
   
   Hedef:
   C:\Users\[KULLANICI]\AppData\Roaming\MetaQuotes\Terminal\[BROKER_ID]\MQL5\Experts\
   ```

**💡 İpucu:** Dosyayı sürükle-bırak yapabilirsin.

---

## ⚙️ ADIM 2: MetaEditor'de Derle

### 2.1 MetaEditor'ü Aç

1. **MT5'te üst menüden:**
   ```
   Tools → MetaQuotes Language Editor
   ```
   
   VEYA kısayol: **F4**

### 2.2 Dosyayı Aç

1. **MetaEditor'de sol panelden:**
   ```
   Navigator → MQL5 → Experts → PythonBridge_MT5.mq5
   ```
   
2. **Dosyaya çift tıkla** (kod açılacak)

### 2.3 Derle (Compile)

1. **Üst menüden:**
   ```
   Compile → Compile
   ```
   
   VEYA kısayol: **F7**

2. **Alt panelde sonuç:**
   ```
   ✅ 0 error(s), 0 warning(s), compile time ... ms
   ```

**❌ Hata varsa:**
- Kod tam kopyalanmamış olabilir
- Syntax hatası olabilir
- Tekrar kopyala ve derle

---

## 📊 ADIM 3: Grafiğe EA'yı Ekle

### 3.1 Sembol Grafiğini Aç

1. **MT5'te XAUUSD sembolünü bul:**
   ```
   Market Watch → XAUUSD
   ```

2. **Sağ tık → Chart Window** (veya çift tıkla)

3. **Grafik açılacak**

### 3.2 EA'yı Grafiğe Sürükle

1. **Sol panelde Navigator'ü aç:**
   ```
   View → Navigator
   ```
   
   VEYA kısayol: **Ctrl+N**

2. **Navigator'de:**
   ```
   Expert Advisors → PythonBridge_MT5
   ```

3. **EA'yı grafiğe sürükle** (Drag & Drop)

### 3.3 Ayarları Yapılandır

**Pencere açılacak, şu ayarları yap:**

#### **Common Sekmesi:**
- ☑️ **Allow live trading** (İşaretle!)
- ☑️ **Allow DLL imports** (İşaretle!)
- ☑️ **Allow WebRequest** (İşaretle!)
- ☐ Allow external experts imports (İşaretleme)

#### **Inputs Sekmesi:**

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `PythonHost` | `127.0.0.1` | Python server IP (localhost) |
| `PythonPort` | `9090` | Python server portu |
| `TradingSymbol` | `""` (boş) | Boş bırak = aktif grafik sembolü |
| `MagicNumber` | `234000` | İşlem tanımlama numarası |
| `EnableAutoTrading` | `true` | Otomatik işlem izni |
| `HeartbeatSeconds` | `5` | Heartbeat aralığı (saniye) |

**💡 Önemli:** `PythonPort` değerini Python server'ınızın dinlediği port ile aynı yapın!

4. **OK'a bas**

---

## ✅ ADIM 4: EA'nın Çalıştığını Kontrol Et

### 4.1 Grafik Üstünde Kontrol

**Grafiğin sağ üst köşesinde:**

- ✅ **😊 (Gülen smiley)** = EA çalışıyor
- ❌ **😞 (Üzgün smiley)** = EA durdurulmuş
- ❌ **⚠️ (Uyarı)** = Hata var

### 4.2 Terminal Loglarını İzle

1. **Alt panelde Terminal'i aç:**
   ```
   View → Toolbox
   ```
   
   VEYA kısayol: **Ctrl+T**

2. **Experts sekmesine geç**

3. **Logları oku:**

**Başarılı bağlantı:**
```
=== Python Bridge MT5 EA Starting ===
Symbol: XAUUSD
Python Server: 127.0.0.1:9090
Magic Number: 234000
✅ Connected to Python successfully
```

**Bağlantı hatası:**
```
ERROR: Failed to connect to Python server
Make sure Python server is running on 127.0.0.1:9090
```

---

## 🐛 ADIM 5: Sorun Giderme

### 🔴 Problem: "Failed to connect to Python server"

**Çözüm 1: Python server çalışıyor mu?**
```powershell
# Python server'ı başlat
python src/mt_bridge_server.py
```

**Çözüm 2: Port 9090 kullanılabilir mi?**
```powershell
# Portu kontrol et
netstat -an | findstr :9090
```

Başka bir program kullanıyorsa, farklı port seç (örn: 9091).

**Çözüm 3: Firewall engelliyor mu?**
1. Windows Defender Firewall'ı aç
2. Inbound Rules → New Rule
3. Port → TCP → 9090 → Allow
4. Tüm profillerde izin ver

---

### 🔴 Problem: EA grafikte görünmüyor

**Çözüm 1: Auto Trading aktif mi?**
```
MT5 üst menü → Tools → Options → Expert Advisors
☑️ Allow automated trading
```

**Çözüm 2: EA doğru derlenmiş mi?**
```
MetaEditor'de F7 ile tekrar derle
0 error olmalı
```

**Çözüm 3: EA listede var mı?**
```
Navigator → Expert Advisors
PythonBridge_MT5 görünmüyorsa, dosya yanlış klasörde
```

---

### 🔴 Problem: "Allow DLL imports" seçeneği görünmüyor

**Çözüm:**
1. **MT5'i kapat**
2. **Yönetici olarak çalıştır** (Run as Administrator)
3. **EA'yı tekrar grafiğe ekle**
4. **Şimdi seçenek görünecek**

---

### 🔴 Problem: EA çalışıyor ama işlem açmıyor

**Kontrol 1: Auto Trading açık mı?**
```
Grafik üst menü: Tools → Options → Expert Advisors
☑️ Allow automated trading
```

**Kontrol 2: EA parametreleri doğru mu?**
```
EA üzerine sağ tık → Expert properties → Inputs
EnableAutoTrading = true olmalı
```

**Kontrol 3: Python komut gönderiyor mu?**
```
Experts sekmesinde log'a bak:
"Received command: ..." görmeli
```

---

## 🎯 ADIM 6: Test Et

### 6.1 Python Test Scripti

Python tarafından test komutu gönder:

```python
import socket
import json

# MT5'e bağlan
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 9090))

# Test komutu: Pozisyonları al
command = {"action": "GET_POSITIONS"}
sock.send((json.dumps(command) + '\n').encode())

# Cevap al
data = sock.recv(4096)
print(f"Received: {data.decode()}")

sock.close()
```

### 6.2 Manuel Test: Pozisyonları Görüntüle

EA çalışırken:

1. **MT5'te pozisyon aç** (Manuel veya Python ile)
2. **Experts sekmesinde log'a bak**
3. **Position bilgileri görünmeli**

---

## 📸 Görsel Kontrol Listesi

### ✅ Doğru Kurulum:

```
Grafik üstü:
┌─────────────────────────────────┐
│ XAUUSD  M15                     │
│                            😊   │  ← Gülen smiley
│         PythonBridge_MT5         │  ← EA adı
│                                 │
└─────────────────────────────────┘

Experts sekmesi:
=== Python Bridge MT5 EA Starting ===
Symbol: XAUUSD
✅ Connected to Python successfully
📊 XAUUSD: Bid=2645.50, Ask=2645.70
💓 Heartbeat: alive
```

### ❌ Yanlış Kurulum:

```
Grafik üstü:
┌─────────────────────────────────┐
│ XAUUSD  M15                     │
│                            😞   │  ← Üzgün smiley
│         PythonBridge_MT5         │  ← EA kapalı
└─────────────────────────────────┘

Experts sekmesi:
ERROR: Failed to connect to Python server
```

---

## 🎓 Sonraki Adımlar

EA başarıyla çalışıyorsa:

1. ✅ **Python bridge server'ı oluştur**
   ```
   src/mt_bridge_server.py
   ```

2. ✅ **TradingBot'u entegre et**
   ```python
   from mt_bridge_server import MT5Bridge
   
   bridge = MT5Bridge()
   bridge.start()
   ```

3. ✅ **Test et**
   - Demo hesapta dene
   - Küçük lot ile başla
   - Logları takip et

4. ✅ **Dashboard'dan izle**
   ```
   http://localhost:5000
   ```

---

## 📞 Yardım

### EA çalışmıyor mu?

1. **Experts sekmesindeki tüm logları kopyala**
2. **Grafik üstündeki smiley durumunu not et**
3. **Python server çıktısını kontrol et**

### Sorular:

- **Port değiştirebilir miyim?** → Evet, hem MT5 hem Python'da aynı portu kullan
- **Birden fazla sembolde çalışır mı?** → Evet, her sembol için ayrı grafik aç
- **Demo hesapta test edebilir miyim?** → Kesinlikle! Demo'da test et, sonra live'a geç
- **EA'yı durdurabilir miyim?** → Evet, EA'ya sağ tık → Remove

---

## ⚠️ Uyarılar

- 🔴 **Live hesapta ilk çalıştırmadan önce demo'da test et**
- 🔴 **Küçük lot ile başla** (örn: 0.01)
- 🔴 **Risk yönetimini atla** (1% risk)
- 🔴 **Circuit breaker'ı aktif tut**
- 🔴 **Stop loss her zaman koy**

---

**Başarılar! 🚀**
