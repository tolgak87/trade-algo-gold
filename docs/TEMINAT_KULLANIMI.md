# 💰 Teminat (Margin) Kullanımı - Detaylı Açıklama

## 📊 Senin Hesabın

**Balance:** $11,000  
**Leverage:** 1:100 (muhtemelen)  
**Risk per trade:** 1% = $110  

---

## 🎯 Risk vs Teminat (Çok Önemli!)

### ⚠️ Karıştırılmaması Gereken 2 Kavram:

#### 1. **Risk (Kayıp riski)**
- Trade kapanırsa kaybedebileceğin para
- SL vurduğunda ne kadar kaybedersin
- **Senin ayarın:** %1 = $110

#### 2. **Teminat (Margin - Pozisyon açmak için gereken)**
- MT5'in pozisyonu açmak için bloke ettiği para
- Leverage ile azalır
- Kayıp DEĞİL, sadece rezervasyon

---

## 💡 Örnek Hesaplama (Senin için)

### Senaryo: 0.55 Lot Gold Trade

```
Entry: 4200
SL: 4180 (20 pip)
Risk: $110 (hesap riskinin %1'i)
Lot size: 0.55
```

### 1️⃣ Risk Hesabı (Risk Manager'dan)

```python
# dashboard_app.py - Line 121
risk_percentage = 1.0   # ← Burada belirliyorsun (değiştirebilirsin)

# risk_manager.py - Line 197
risk_amount = account_balance * (risk_percentage / 100)
risk_amount = $11,000 × 1% = $110

# Lot size hesaplama
lot_size = risk_amount / (SL_pips × contract_size)
lot_size = $110 / (20 × 100)
lot_size = 0.55 lots
```

### 2️⃣ Teminat Hesabı (MT5'ten)

```
Gold contract size: 100 oz
Current price: $4200
Lot size: 0.55
Leverage: 1:100

Teminat = (Lot × Contract Size × Price) / Leverage
Teminat = (0.55 × 100 × 4200) / 100
Teminat = 231,000 / 100
Teminat = $2,310 ← Bloke edilen teminat
```

### 📊 Karşılaştırma:

| Kavram | Miktar | Yüzde | Açıklama |
|--------|--------|-------|----------|
| **Risk** | $110 | 1% | SL vurursa kaybedersin |
| **Teminat** | $2,310 | 21% | MT5'in bloke ettiği |
| **Free Margin** | $8,690 | 79% | Kalan serbest |

---

## 🔧 Kodda Nerede Belirleniyor?

### 1. Risk Yüzdesi (Ana Ayar)

**Dosya:** `dashboard_app.py`  
**Satır:** 121

```python
risk_percentage = 1.0   # ← BURADAN DEĞİŞTİR
```

**Değiştirebileceğin değerler:**
```python
risk_percentage = 0.5   # Çok konservatif (0.5% risk)
risk_percentage = 1.0   # Normal (1% risk) ← Şu an bu
risk_percentage = 1.5   # Agresif (1.5% risk)
risk_percentage = 2.0   # Çok agresif (2% risk) ⚠️
```

### 2. Risk Hesaplama (Otomatik)

**Dosya:** `src/risk_manager.py`  
**Satır:** 197

```python
def calculate_position_size_by_risk(self, ...):
    # Risk tutarını hesapla
    risk_amount = account_balance * (risk_percentage / 100)
    
    # Lot size hesapla
    price_difference = abs(entry_price - stop_loss_price)
    lot_size = risk_amount / (price_difference * contract_size)
    
    return lot_size
```

**Bu fonksiyon otomatik çağrılır:**
- `trading_bot.py` → `execute_trade()` içinde
- Her trade öncesi lot size hesaplanır
- Risk yüzdesine göre ayarlanır

### 3. Trading Bot'ta Kullanımı

**Dosya:** `src/trading_bot.py`  
**Satır:** 303

```python
def execute_trade(self, position_type: str = 'BUY', 
                 risk_percentage: float = 1.0,  # ← Default %1
                 use_sar_sl: bool = True):
    
    # Risk manager ile lot size hesapla
    lot_size = self.risk_manager.calculate_position_size_by_risk(
        account_balance=self.account_balance,
        risk_percentage=risk_percentage,  # ← Buraya geliyor
        entry_price=entry_price,
        stop_loss_price=sl
    )
```

---

## 📈 Farklı Risk Ayarları İçin Örnekler

### Hesap: $11,000 | SL: 20 pip | Entry: 4200

| Risk % | Risk $ | Lot Size | Teminat | Teminat % |
|--------|--------|----------|---------|-----------|
| 0.5% | $55 | 0.28 | $1,176 | 10.7% |
| 1.0% | $110 | 0.55 | $2,310 | 21.0% |
| 1.5% | $165 | 0.83 | $3,486 | 31.7% |
| 2.0% | $220 | 1.10 | $4,620 | 42.0% |

### ⚠️ Dikkat:

**Teminat %30'un üzerindeyse:**
- Çok fazla exposure
- Margin call riski artar
- Diğer trade'ler için yer kalmaz

**Önerilen:**
- Risk: %1
- Teminat: %20-25
- Güvenli bölge

---

## 🔍 Teminat Kullanımını Görme

### 1. MT5'te Kontrol

```
Terminal → Trade → 
- Balance: $11,000
- Equity: $11,xxx (pozisyon P/L dahil)
- Margin: $2,310 (kullanılan teminat)
- Free Margin: $8,690 (serbest)
- Margin Level: 476% (equity / margin)
```

### 2. Kodda Kontrol

**Dosya:** `src/collect_account_info.py`

```python
account_info = mt5.account_info()

print(f"Balance: ${account_info.balance}")
print(f"Equity: ${account_info.equity}")
print(f"Margin: ${account_info.margin}")  # ← Kullanılan teminat
print(f"Free Margin: ${account_info.margin_free}")
print(f"Margin Level: {account_info.margin_level}%")
```

### 3. Dashboard'da Görüntüleme

Bot çalışırken dashboard'da görebilirsin:
- Real-time balance
- Equity
- Free margin

---

## 💡 Leverage'ın Etkisi

### Leverage 1:100 (Senin hesabın - muhtemelen)

```
0.55 lot trade:
Pozisyon değeri: $231,000
Gereken teminat: $231,000 / 100 = $2,310
```

### Eğer Leverage 1:50 olsaydı

```
0.55 lot trade:
Pozisyon değeri: $231,000
Gereken teminat: $231,000 / 50 = $4,620 (2x daha fazla!)
```

### Eğer Leverage 1:500 olsaydı

```
0.55 lot trade:
Pozisyon değeri: $231,000
Gereken teminat: $231,000 / 500 = $462 (5x daha az!)
```

**Ama dikkat:**
- Yüksek leverage = Daha az teminat
- Ama risk aynı kalır ($110 loss SL'de)
- Leverage sadece teminatı etkiler, riski değil!

---

## 🎯 Risk Ayarını Değiştirme

### Yöntem 1: Dashboard App'te (Önerilen)

**Dosya:** `dashboard_app.py`  
**Satır:** 121

```python
# Mevcut
risk_percentage = 1.0

# Değiştir
risk_percentage = 0.75  # Daha konservatif
```

**Sonra:**
```bash
python dashboard_app.py
```

### Yöntem 2: Config Dosyası (Gelecek özellik)

```json
{
    "trading_config": {
        "risk_percentage": 1.0,
        "max_position_size": 2.0,
        "min_position_size": 0.01
    }
}
```

---

## 📊 Güvenli Teminat Kullanımı

### Kurallar:

1. **Tek pozisyon için teminat < %30**
   - Senin durumun: %21 ✅ Güvenli

2. **Total açık pozisyon teminatı < %50**
   - Birden fazla trade varsa toplamı

3. **Margin Level > 200%**
   - 200%'in altı = Tehlikeli
   - 100%'in altı = Margin call!

### Senin Hesabın İçin:

```
Balance: $11,000
Leverage: 1:100
Risk: %1 = $110
Lot: 0.55
Teminat: $2,310 (21%)
Margin Level: 476% ✅ Çok güvenli!
```

---

## 🚨 Margin Call Nedir?

**Margin Level:**
```
Margin Level = (Equity / Margin) × 100
```

**Senaryolar:**

### Normal Durum (Şu an)
```
Equity: $11,000
Margin: $2,310
Margin Level: 476% ✅
```

### Loss durumu
```
Equity: $9,500 (kayıp var)
Margin: $2,310
Margin Level: 411% ✅ Hala güvenli
```

### Tehlikeli durum
```
Equity: $3,000 (çok kayıp!)
Margin: $2,310
Margin Level: 130% ⚠️ Dikkat!
```

### Margin Call
```
Equity: $2,310 veya daha az
Margin Level: 100% veya altı
🔴 MARGIN CALL → Pozisyon kapatılır!
```

---

## 💻 Teminat Hesaplayıcı Script

```python
# Kullanım:
# python calculate_margin.py

import MetaTrader5 as mt5

def calculate_margin_usage(lot_size, leverage=100):
    """Calculate margin usage for Gold trade"""
    
    if not mt5.initialize():
        print("MT5 initialization failed")
        return
    
    symbol = "XAUUSD"
    symbol_info = mt5.symbol_info(symbol)
    
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        mt5.shutdown()
        return
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    current_price = tick.ask
    
    # Get contract size
    contract_size = symbol_info.trade_contract_size
    
    # Calculate margin
    position_value = lot_size * contract_size * current_price
    margin_required = position_value / leverage
    
    print(f"\n{'='*60}")
    print(f"💰 MARGIN CALCULATOR - GOLD")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Lot Size: {lot_size}")
    print(f"Contract Size: {contract_size} oz")
    print(f"Leverage: 1:{leverage}")
    print(f"\n📊 Calculations:")
    print(f"Position Value: ${position_value:,.2f}")
    print(f"Margin Required: ${margin_required:,.2f}")
    print(f"\n💡 For $11,000 account:")
    print(f"Margin %: {(margin_required/11000)*100:.1f}%")
    print(f"{'='*60}")
    
    mt5.shutdown()

if __name__ == "__main__":
    # Test with your typical lot size
    calculate_margin_usage(lot_size=0.55, leverage=100)
```

**Kullanım:**
```bash
python calculate_margin.py
```

**Çıktı:**
```
💰 MARGIN CALCULATOR - GOLD
============================================================
Symbol: XAUUSD
Current Price: $4200.00
Lot Size: 0.55
Contract Size: 100 oz
Leverage: 1:100

📊 Calculations:
Position Value: $231,000.00
Margin Required: $2,310.00

💡 For $11,000 account:
Margin %: 21.0%
============================================================
```

---

## 🎯 Özet

### Risk Ayarı (Sen kontrol ediyorsun):
```python
# dashboard_app.py - Line 121
risk_percentage = 1.0   # ← BURASI
```

### Sonuç (Otomatik hesaplanıyor):
- **Risk:** $110 (kayıp riski)
- **Lot:** 0.55 (otomatik)
- **Teminat:** $2,310 (MT5'in bloke ettiği)
- **Teminat %:** 21% (hesabının %21'i)

### Önerilen Ayarlar:
```python
risk_percentage = 1.0   # Normal ✅
# risk_percentage = 0.75  # Konservatif
# risk_percentage = 1.5   # Agresif ⚠️
```

### Güvenlik:
- ✅ Risk: %1 → Güvenli
- ✅ Teminat: %21 → Güvenli
- ✅ Margin Level: 476% → Çok güvenli

**Herhangi bir sorun yok, ayarlar iyi! 🚀**
