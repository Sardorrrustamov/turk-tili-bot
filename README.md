# 🇹🇷 Turkcha So'z O'rganish Telegram Boti - V2.0

Turkcha til o'rganish uchun yaratilgan telegram bot.  
**python-telegram-bot v22** ga mos yozilgan.

---

## 🚀 Xususiyatlar

| Funksiya | Tavsif |
|---|---|
| 📚 **Dynamic Testlar** | lugat.json dan dinamik o'qilinadi |
| ✅ **Qism bo'yicha test** | Har bir qismda sonli savollar dinamik |
| ➕ **So'z qo'shish** | Darajalar, unitlar, qismlarga qo'shish |
| 🤖 **AI Yordamchi** | Gemini API orqali turkcha savollarga javob |
| 📊 **Statistika** | Qism bo'yicha natijalar va progress (unayl) |
| 🔊 **Audio qo'llab-quvvatlash** | Har qismga audio fayl qo'shish imkoni |
| 👥 **Admin panel** | Foydalanuvchilar va umumiy statistika |

---

## ⚙️ O'rnatish

### 1. Fayllarni yuklab oling

```bash
git clone <repo>
cd turkish_bot
```

### 2. Virtual muhit yarating

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Kutubxonalarni o'rnating

```bash
pip install -r requirements.txt
```

### 4. `.env` faylini sozlang

```bash
cp .env.example .env
```

`.env` faylini oching va to'ldiring:

```env
BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
ADMIN_ID=0
```

- **BOT_TOKEN** — [@BotFather](https://t.me/BotFather) dan olinadi
- **GEMINI_API_KEY** — [Google AI Studio](https://aistudio.google.com/app/apikey) dan olinadi (bepul)
- **ADMIN_ID** — Telegram ID ([@userinfobot](https://t.me/userinfobot) dan bilib olasiz); `0` qo'yilsa hamma test qo'sha oladi

### 5. Botni ishga tushiring

```bash
python bot.py
```

---

## 📂 Bo'limlar

1. Bog'lovchi so'zlar (aslında, özellikle...)
2. Fikr bildirish (kanımca, sanırım...)
3. Muhim sifatlar (etkileyici, karmaşık...)
4. Muhim fe'llar (vurgulamak, desteklemek...)
5. Muloqot iboralari (söz konusu, kısacası...)
6. His-tuyg'ular (memnunum, endişeleniyorum...)
7. Jamiyat va ish (toplum, süreç...)
8. Vaqt ifodalari (hâlâ, artık...)
9. Mavhum tushunchalar (fırsat, sorumluluk...)
10. B2 Daraja iboralari (bağlamında, karşın...)

---

## ➕ Yangi so'z qo'shish

1. `/start` → `➕ Test qo'shish`
2. Darajani kiriting (A1, A2, B1, ...)
3. Unit nomini kiriting
4. Qism nomini kiriting
5. Turkcha so'zni kiriting
6. O'zbekcha tarjimasini kiriting
7. Yana so'z qo'shasiz? → Ha/Yo'q

---

## 📁 Fayl tuzilmasi (Refactor v2.0)

```
turkish_bot/
├── bot.py                # Entrypoint (main.py ni chaqiradi)
├── main.py               # Application yaratish va handlerlarni ulash
├── handlers.py           # Barcha telegram handler'lari
├── keyboards.py          # Inline va ReplyKeyboard'lar
├── data_loader.py        # lugat.json dan data yuklash (ASOSIY!)
├── quiz_engine.py        # Test logikasi (dynamic savollar)
├── user_stats.py         # Foydalanuvchi statistikasi (qism bo'yicha)
├── admin_panel.py        # Admin paneli formatlari
├── gemini.py             # Gemini AI integratsiya
├── config.py             # .env dan konfiguratsiya
├── lugat.json            # 📚 BARCHA MA'LUMOT SHURASIDA (asosiy!)
├── requirements.txt
├── .env.example
├── users.json            # Foydalanuvchi ma'lumoti (TinyDB)
├── stats.json            # Statistika qism bo'yicha (TinyDB)
└── README.md             # Bu fayl
```

---

## 🏗️ Arxitektura (Refactored)

### data_loader.py
- `lugat.json` o'qish va parse qilish
- Levellar, unitlar, qismlarni olish
- So'z qidirish

### quiz_engine.py  
- Har qism uchun dinamik test yaratish
- Savollar va variantlarni tayyorlash
- Random variantlar

### user_stats.py
- **Qism bo'yicha** statistika saqlash
- Unique key: `user_id + level + unit + section`
- Update yoki yangi qo'shish

### admin_panel.py
- Dashboard formatlash
- Foydalanuvchilar ro'yxati
- Umumiy statistika

---

## 📊 Statistika Formati

```json
{
  "user_id": 123456,
  "username": "ali",
  "level": "A1",
  "unit": "Unit 1",
  "section": "1-qism",
  "correct_answers": 15,
  "wrong_answers": 5,
  "total_questions": 20,
  "date": "2026-04-27"
}
```

**Mustahim:** Takroriy testlarda **update** qilinadi, duplicate qo'shilmaydi!

---

## 🔄 Test Logikasi

1. User qismni tanlasa:
   - `quiz_engine` barcha so'zlardan savollar yaratadi
   - **Har bir so'z = 1 ta savol** ✅
   - 4 ta variant (to'g'ri + 3 ta noto'g'ri)

2. Test yakunida:
   - Natija `user_stats.save_section_result()` ga saqlanadi
   - **Qismning unique ID'si bilan unayl qilinadi**

3. Statistics:
   - User qismni qayta ishlasa → eski natija update qilinadi
   - Duplicate yozuv bo'lmaydi ✅
