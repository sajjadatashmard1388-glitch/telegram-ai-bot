راهنمای خیلی کوتاه راه‌اندازی

1. پروژه را در GitHub بگذار.
2. در Koyeb یک Web Service از repository بساز.
3. Build/Run را روی Dockerfile بگذار (یا Buildpack Python).
4. Environment Variables را اضافه کن:
   TELEGRAM_TOKEN
   AI_API_KEY
   AI_URL
   AI_MODEL
   WEBHOOK_SECRET
   PUBLIC_URL
5. Deploy کن.
6. بعد از موفقیت Deploy، به ربات /start بفرست.

PUBLIC_URL باید دقیقاً آدرس HTTPS سرویس Koyeb باشد، بدون / آخر.

مثال:
PUBLIC_URL=https://my-bot-abc.koyeb.app

این برنامه خودش webhook را هنگام شروع تنظیم می‌کند.
