# 📊 Daily Loss Limit - Nasıl Çalışır?

## 🎯 Özet

Daily Loss Limit, **günün tüm trade'lerinden** (bot + manuel) toplam loss'u hesaplar ve limite ulaşıldığında **sadece trade'i durdurur** (kodu kapatmaz).

---

## ❓ Sıkça Sorulan Sorular

### 1️⃣ "Kodda o günün bütün işlemlerini manuel de olsa tutuyor değil mi?"

**EVET! ✅** Kod şu an:
- ✅ Bot'un açtığı tüm trade'leri tutuyor (trade_logs/ klasöründe)
- ✅ Manuel MT5'te kapattığın trade'leri de tutuyor (bot çalışırken)
- ✅ Günün başından beri TOPLAM profit/loss'u hesaplıyor

**Nasıl tutuyor?**
```python
# TradeLogger sınıfı kullanılıyor
stats = self.trade_logger.get_trade_statistics()
total_daily_profit = stats.get("total_profit", 0)  # Günün toplam P/L'si

# Eğer loss varsa (negatif değer)
daily_loss = abs(total_daily_profit)
```

**Örnek:**
```
Gün içinde trade'ler:
1. Bot trade: -$200 loss
2. Manuel trade: -$150 loss  
3. Bot trade: +$50 profit
4. Bot trade: -$300 loss

TOPLAM = -$200 - $150 + $50 - $300 = -$600 loss ✅
```

### 2️⃣ "Günün başlangıcından beri toplam kayba bakıyor değil mi?"

**EVET! ✅** 

Kod şöyle çalışıyor:

**Sabah ilk başladığında:**
```python
today = "2025-12-01"
starting_balance = $10,000  # Günün başlangıcı kaydedilir
```

**Gün boyunca:**
```python
# Her trade öncesi kontrol edilir
total_daily_loss = abs(today_all_trades_profit_loss)

# Örnek:
# Trade 1: -$200
# Trade 2: -$300
# Trade 3: +$100
# Trade 4: -$200
# TOPLAM LOSS = -$600 ✅
```

### 3️⃣ "Bu geliştirme kodu kapatıyor mu yoksa saat olarak trade'i mi durduruyor?"

**SADECE TRADE'İ DURDURUYOR! ⏸️** (Kodu kapatmıyor)

**Ne oluyor:**
- ✅ **Bot çalışmaya DEVAM eder** (kod kapanmaz)
- ✅ **Dashboard AÇIK kalır** (görebilirsin)
- ✅ **MT5 bağlantısı AKTİF** (monitoring devam eder)
- ❌ **Yeni trade AÇAMAZ** (blocked)
- ⏰ **Gece yarısına kadar bekler**
- ✅ **Gece yarısında otomatik DEVAM eder**

**Terminal çıktısı:**
```
🔴 TRADE BLOCKED: DAILY LOSS LIMIT: $1000.00 (10.0%) | Max: 10%

Bot çalışmaya devam ediyor... (sadece yeni trade açmıyor)
Gece yarısında otomatik devam edecek.
```

### 4️⃣ "protection_config dosyasında percentage 10 demişsin. Bir de 1000 dolar kaybedersen de mi durduruyor?"

**HAYIR! Sadece BİRİ aktif ❗**

**Şu an config:**
```json
{
    "max_daily_loss_dollars": 1000,      // ← Bu KULLANILMIYOR ❌
    "max_daily_loss_percentage": 10,     // ← Bu KULLANILIYOR ✅
    "use_percentage": true               // ← Bu açık olduğu için
}
```

**Açıklama:**
- `use_percentage: true` ise → **SADECE yüzde kontrolü** (10% = $10,000'dan $1,000 loss)
- `use_percentage: false` ise → **SADECE dolar kontrolü** ($1,000 sabit loss)

**Örnek 1: Yüzde Kontrolü (Şu an aktif)**
```
Başlangıç: $10,000
Max loss: 10%
Loss limiti: $10,000 × 10% = $1,000 ✅

$500 loss → ✅ İzin verilir (5%)
$1,000 loss → 🔴 DURDURULUR (10%)
$1,500 loss → 🔴 DURDURULUR (15%)
```

**Örnek 2: Dolar Kontrolü (Kapalı)**
```
use_percentage: false yap

Başlangıç: $10,000 veya $20,000 farketmez
Max loss: $1,000 (sabit)

$500 loss → ✅ İzin verilir
$1,000 loss → 🔴 DURDURULUR
$1,500 loss → 🔴 DURDURULUR
```

---

## 🔧 Nasıl Değiştiririm?

### Seçenek 1: Yüzde tabanlı (Önerilen)
```json
{
    "use_percentage": true,
    "max_daily_loss_percentage": 5    // %5 yap (daha sıkı)
}
```

**Avantaj:** Hesap büyüdükçe/küçüldükçe otomatik ayarlanır

### Seçenek 2: Sabit dolar
```json
{
    "use_percentage": false,
    "max_daily_loss_dollars": 500     // $500 sabit limit
}
```

**Avantaj:** Net rakam, değişmez

---

## 📊 Gerçek Örnekler

### Örnek 1: Normal Gün
```
Başlangıç: $10,000
Limit: 10% ($1,000)

Trade 1: -$100 (loss)
Trade 2: +$50 (profit)
Trade 3: -$200 (loss)
Trade 4: +$150 (profit)

Toplam: -$100 ✅ DEVAM EDİYOR (1% loss)
```

### Örnek 2: Kötü Gün - Limit Aşıldı
```
Başlangıç: $10,000
Limit: 10% ($1,000)

Trade 1: -$300 (loss)
Trade 2: -$400 (loss)
Trade 3: -$200 (loss)
Manuel: -$150 (loss)

Toplam: -$1,050 🔴 DURDURULDU! (10.5% loss)

Bot mesajı: 
"🔴 DAILY LOSS LIMIT: $1050.00 (10.5%) | Max: 10%"
"⏸️ Trading paused until midnight"
"✅ Bot still running, monitoring only"
```

### Örnek 3: Gece Yarısında Reset
```
23:59 → Loss $1,050 → 🔴 Durdurulmuş
00:00 → YENİ GÜN başladı
00:01 → Starting balance: $8,950 (yeni başlangıç)
        Loss counter: $0 (sıfırlandı)
        Status: ✅ Trading resumed
```

---

## 🎛️ Hangi Ayar Sana Uygun?

### Muhafazakar (Az risk)
```json
{
    "use_percentage": true,
    "max_daily_loss_percentage": 5    // %5 çok sıkı
}
```
👍 Güvenli, sermaye koruma
👎 Erken durabilir

### Normal (Orta risk) - **ŞU AN AKTİF**
```json
{
    "use_percentage": true,
    "max_daily_loss_percentage": 10   // %10 dengeli
}
```
👍 Dengeli, çoğu trader için uygun
👎 Kötü günde geç durabilir

### Agresif (Yüksek risk)
```json
{
    "use_percentage": true,
    "max_daily_loss_percentage": 15   // %15 gevşek
}
```
👍 Daha fazla fırsat
👎 Daha fazla risk

---

## 🧪 Test Et

```bash
python test_daily_loss_limit.py
```

**Çıktı:**
```
📊 Current Account Balance: $9,500.00

💡 Daily Loss Limit Details:
   Starting Balance: $10,000.00
   Max Loss Allowed: 10% ($1,000.00)
   Current Loss: $500.00
   Remaining: $500.00 (5.0%)

✅ Daily loss limit OK - Trading allowed
```

---

## ⚠️ Önemli Notlar

1. **Bot kapanmaz** - Sadece yeni trade açmaz
2. **Gece yarısı reset** - Her gün sıfırdan başlar
3. **Trade log'larına bakar** - Gerçek loss hesabı
4. **Manuel trade'ler dahil** - MT5'te manuel kapattıkların sayılır
5. **Email gönderir** - Limit aşıldığında bilgilendirir

---

## 🔗 İlgili Dosyalar

- `protection_config.json` - Ayarlar burada
- `circuit_breaker_state.json` - Güncel durum burada
- `trade_logs/trades_2025_12_01.json` - Günün trade'leri burada
- `src/circuit_breaker.py` - Ana kod burada

---

**Özet:** Kod günün TÜM trade'lerine bakıyor, TOPLAM loss'u hesaplıyor, limite ulaşınca SADECE trade'i durduruyor (kodu kapatmıyor), gece yarısında otomatik devam ediyor. ✅
