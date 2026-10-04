# Telegram AI Personality Bot

یک ربات تلگرامی فارسی با شخصیت حاضر جواب + پاسخ‌گویی درسی.

## چیزی که این پروژه انجام می‌دهد

- Telegram Webhook
- پاسخ با مدل هوش مصنوعی OpenAI-compatible
- شخصیت حاضر جواب و شوخ
- کل‌کل غیرخشونت‌آمیز
- عدم تولید محتوای جنسی
- پاسخ به سؤالات درسی
- حافظه کوتاه مکالمه برای هر کاربر
- `/start`
- `/help`
- `/reset`
- مناسب برای Koyeb Free
- قابلیت Scale-to-Zero: پس از یک ساعت بدون ترافیک سرویس Free می‌خوابد و با درخواست جدید بیدار می‌شود.

## ساده‌ترین روش استقرار: Koyeb

### 1) ساخت ربات

در Telegram، به `@BotFather` برو و `/newbot` را بزن.

توکن را نگه دار.

### 2) ساخت AI API Key

این پروژه با endpointهای OpenAI-compatible کار می‌کند.
نمونه پیش‌فرض OpenRouter است.

مقدار `AI_API_KEY` را از سرویس مدل خودت بگیر.

### 3) ساخت سرویس در Koyeb

در Koyeb یک Web Service بساز و این پروژه را از GitHub یا فایل‌های پروژه deploy کن.

Port را روی متغیر `$PORT` بگذار؛ برنامه خودش روی همان port اجرا می‌شود.

### 4) Environment Variables

این متغیرها را در Koyeb اضافه کن:

TELEGRAM_TOKEN=توکن ربات
AI_API_KEY=کلید سرویس AI
AI_URL=https://openrouter.ai/api/v1/chat/completions
AI_MODEL=openai/gpt-4o-mini
WEBHOOK_SECRET=یک عبارت تصادفی طولانی
PUBLIC_URL=https://آدرس-سرویس-koyeb-تو.koyeb.app

### 5) Deploy

بعد از Deploy، برنامه خودش webhook را روی این مسیر ثبت می‌کند:

/telegram/WEBHOOK_SECRET

مثلاً:

https://example.koyeb.app/telegram/my-secret

### 6) تست

در تلگرام `/start` بفرست.

بعد یک سؤال مثل:

«قانون دوم نیوتن را توضیح بده»

یا:

«تو بلدی جواب بدی؟»

بفرست.

## اجرای محلی

نصب:

pip install -r requirements.txt

سپس متغیرها را تنظیم کن و:

python bot.py

## درباره توکن داخل کد

در ابتدای `bot.py` دو مقدار placeholder وجود دارد:

TELEGRAM_TOKEN = ...
AI_API_KEY = ...

کد ابتدا Environment Variable را می‌خواند و اگر وجود نداشته باشد از مقدار داخل کد استفاده می‌کند.

برای آموزش می‌توانی مقدار واقعی را آنجا قرار بدهی، اما برای GitHub این کار توصیه نمی‌شود.

## نکته مهم درباره Sleep

این پروژه از Webhook استفاده می‌کند، نه polling.

این انتخاب برای سرویس‌های Scale-to-Zero مناسب‌تر است، چون Telegram درخواست webhook را به URL عمومی سرویس می‌فرستد.

Koyeb Free طبق مستندات فعلی پس از یک ساعت بدون ترافیک به zero scale می‌شود. با درخواست جدید سرویس wake می‌شود. اولین پاسخ پس از sleep ممکن است کمی تأخیر cold-start داشته باشد.

## محدودیت حافظه

حافظه مکالمه در RAM است.

اگر سرویس restart شود، تاریخچه مکالمه پاک می‌شود.
برای حافظه دائمی باید بعداً Redis/PostgreSQL یا دیتابیس اضافه شود.
