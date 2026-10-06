# Kino va Serial Bot (aiogram 3 + SQLite)

## Lokal ishga tushirish
1. `pip install -r requirements.txt`
2. `.env.example` → `.env`, BOT_TOKEN va ADMINS ni yozing.
3. `python main.py` (lokalda polling), `/admin` — admin panel.

## GitHub + Render (bepul) ga joylash
1. GitHub'da **private** repo oching va kodni yuklang:
   ```
   git init && git add . && git commit -m "kino bot"
   git branch -M main
   git remote add origin https://github.com/USERNAME/kino-bot.git
   git push -u origin main
   ```
   (`.env` va `*.db` `.gitignore` da — token GitHub'ga tushmaydi.)
2. render.com → **New → Blueprint** → repo'ni tanlang (render.yaml avtomatik o'qiladi).
   Yoki **New → Web Service**: Build `pip install -r requirements.txt`, Start `python main.py`, Plan **Free**.
3. Environment: `BOT_TOKEN`, `ADMINS` (ID lar, vergul bilan). `PYTHON_VERSION=3.11.9`.
4. Deploy tugagach botga `/start` yuboring (birinchi admin — eng kichik ID — zaxira oladi).

## Muhim: bepul tarif cheklovlari
- **Disk vaqtinchalik**: har deploy/restartda `kino.db` o'chadi. Shu uchun bot bazani har `BACKUP_HOURS` (6) soatda,
  o'chishdan oldin va `/backup` bilan **asosiy admin chatiga yuboradi va pin qiladi**. Qayta ishga tushganda
  baza o'sha pin qilingan fayldan **avtomatik tiklanadi**. Pin qilingan zaxira xabarini **o'chirmang**.
- Qo'lda tiklash: `.db` faylni botga **caption `/restore`** bilan yuboring.
- 15 daqiqa trafik bo'lmasa Render uxlatadi: bot o'ziga har 10 daqiqada ping yuboradi. Ishonchlilik uchun
  qo'shimcha ravishda UptimeRobot'da `https://SIZNING-APP.onrender.com/health` ni 5 daqiqada tekshirishga qo'ying.
- Jiddiy yuklama/doimiy ma'lumot uchun pullik disk (Render Starter + Disk) yoki tashqi baza tavsiya etiladi.

## Yangi imkoniyatlar
- Premium tugashiga 3 kun qolganda eslatma, tugaganda avtomatik oddiyga o'tkazish.
- To'lov cheki: foydalanuvchi "🧾 To'lov qildim" → tarif → chek rasmi → adminlarga ✅/❌ tugmalar bilan boradi,
  tasdiqlansa Premium avtomatik beriladi.
