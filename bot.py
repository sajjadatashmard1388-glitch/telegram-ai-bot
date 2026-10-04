import os
import logging
import requests
from flask import Flask, request, jsonify

# ============================================================
# EDUCATIONAL CONFIG
# ============================================================
# For local testing you MAY put your values here.
# For deployment, it is safer to leave these placeholders and
# use Koyeb Environment Variables instead.
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "PASTE_TELEGRAM_BOT_TOKEN_HERE")
AI_API_KEY = os.getenv("AI_API_KEY", "PASTE_AI_API_KEY_HERE")

# OpenAI-compatible endpoint. OpenRouter is the default example.
AI_URL = os.getenv(
    "AI_URL",
    "https://openrouter.ai/api/v1/chat/completions"
)
AI_MODEL = os.getenv(
    "AI_MODEL",
    "openai/gpt-4o-mini"
)

# Koyeb gives your service a public HTTPS URL.
# Example: https://my-bot-xxxxx.koyeb.app
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-this-secret")

PORT = int(os.getenv("PORT", "8000"))
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "12"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = Flask(__name__)

# Short-lived in-memory conversation history.
# It is intentionally simple; when a sleeping container is restarted,
# this memory can disappear.
histories = {}

SYSTEM_PROMPT = r"""
تو یک ربات تلگرامی فارسی‌زبان با شخصیت «حاضر جواب، باهوش، شوخ و کمی
کل‌کل‌کن» هستی.

هویت و لحن:
- طبیعی و محاوره‌ای فارسی صحبت کن.
- جواب‌ها کوتاه و زنده باشند، مگر اینکه کاربر توضیح مفصل بخواهد.
- اگر کاربر شوخی یا کل‌کل کرد، شوخی را بفهم و با طعنه‌ی بامزه جواب بده.
- اگر کاربر توهین غیرجنسی کرد، می‌توانی یک جواب حاضر جواب، کنایه‌آمیز
  و غیرخشونت‌آمیز بدهی؛ اما توهین جنسی، محتوای جنسی، تحقیر جنسی،
  تهدید و تشویق به خشونت تولید نکن.
- اگر کاربر فحش داد، لازم نیست سخنرانی اخلاقی کنی؛ یک جواب کنترل‌شده
  و بامزه بده و گفتگو را ادامه بده.
- از تهدید، نفرت‌پراکنی و حمله به گروه‌های هویتی خودداری کن.
- اگر کاربر ناراحت یا در وضعیت جدی است، لحن شوخی را کنار بگذار.

حالت درسی:
- اگر پیام سؤال درسی است، شخصیت کل‌کل‌کن را کنار بگذار و دقیق و آموزشی
  پاسخ بده.
- برای زیست، شیمی، فیزیک، ریاضی، زمین‌شناسی، فارسی، عربی، دینی و
  انگلیسی توضیح قابل فهم بده.
- برای مسائل محاسباتی، فرمول و مراحل حل را نشان بده.
- اگر مطمئن نیستی، با اطمینان الکی جواب نساز و بگو کدام بخش نیاز به
  بررسی دارد.
- اگر سؤال چندگزینه‌ای است، گزینه درست را مشخص و دلیلش را بگو.

نمونه لحن:
کاربر: «تو خیلی خنگی»
ربات: «بالاخره یکی پیدا شد اعتمادبه‌نفسش از اطلاعاتش بیشتره 😂»

کاربر: «بلدی جواب بدی؟»
ربات: «آره، ولی اول ببینم سؤال داری یا فقط اومدی امتحانم کنی 😌»

کاربر: «قانون دوم نیوتن؟»
ربات: «قانون دوم نیوتن: F = ma. یعنی نیروی خالص برابر جرم ضربدر شتابه...»

قانون مهم:
اگر سؤال درسی و شوخی همزمان بود، اولویت با پاسخ درست درسی است.
"""

def telegram_api(method, payload=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    r = requests.post(url, json=payload or {}, timeout=30)
    r.raise_for_status()
    return r.json()

def send_message(chat_id, text, reply_to=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_to:
        payload["reply_parameters"] = {"message_id": reply_to}
    return telegram_api("sendMessage", payload)

def ask_ai(user_id, user_text):
    history = histories.setdefault(user_id, [])
    history.append({"role": "user", "content": user_text})

    # Keep only recent messages.
    history[:] = history[-MAX_HISTORY:]

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": PUBLIC_URL or "https://koyeb.com/",
        "X-Title": "Telegram Personality Study Bot",
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": 0.85,
        "max_tokens": 700,
    }

    response = requests.post(
        AI_URL,
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    data = response.json()

    answer = data["choices"][0]["message"]["content"].strip()

    history.append({"role": "assistant", "content": answer})
    history[:] = history[-MAX_HISTORY:]
    return answer

def set_webhook():
    if not PUBLIC_URL:
        logging.warning("PUBLIC_URL is empty; webhook was not configured.")
        return

    webhook_url = f"{PUBLIC_URL}/telegram/{WEBHOOK_SECRET}"

    try:
        result = telegram_api("setWebhook", {
            "url": webhook_url,
            "secret_token": WEBHOOK_SECRET,
            "allowed_updates": ["message"],
        })
        logging.info("Webhook setup: %s", result)
    except Exception:
        logging.exception("Could not configure Telegram webhook.")

@app.get("/")
def home():
    return jsonify({
        "ok": True,
        "service": "Telegram AI Bot",
        "status": "running"
    })

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.post(f"/telegram/<secret>")
def telegram_webhook(secret):
    if secret != WEBHOOK_SECRET:
        return jsonify({"ok": False}), 403

    update = request.get_json(silent=True) or {}
    message = update.get("message")

    if not message:
        return jsonify({"ok": True})

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    user = message.get("from", {})
    user_id = str(user.get("id", chat_id))

    text = message.get("text", "")
    if not text or not chat_id:
        return jsonify({"ok": True})

    try:
        if text.startswith("/start"):
            send_message(
                chat_id,
                "سلام 😎\n"
                "من ربات حاضر جوابم.\n\n"
                "هم سؤال درسی جواب می‌دم، هم اگر بخوای باهات کل‌کل می‌کنم 😂\n"
                "برای شروع فقط پیام بده."
            )
            return jsonify({"ok": True})

        if text.startswith("/help"):
            send_message(
                chat_id,
                "دستورها:\n"
                "/start شروع\n"
                "/help راهنما\n"
                "/reset پاک کردن حافظه گفت‌وگو\n\n"
                "بقیه‌اش رو با پیام معمولی انجام بده."
            )
            return jsonify({"ok": True})

        if text.startswith("/reset"):
            histories.pop(user_id, None)
            send_message(chat_id, "حافظه این گفت‌وگو پاک شد. از نو شروع کنیم 😎")
            return jsonify({"ok": True})

        answer = ask_ai(user_id, text)

        # Telegram message limit is around 4096 characters.
        if len(answer) > 4000:
            answer = answer[:3990] + "\n..."

        send_message(
            chat_id,
            answer,
            reply_to=message.get("message_id")
        )

    except Exception:
        logging.exception("Message handling failed.")
        try:
            send_message(
                chat_id,
                "یه لحظه مغزم هنگ کرد 😂 دوباره بفرست."
            )
        except Exception:
            logging.exception("Could not send error message.")

    return jsonify({"ok": True})

if __name__ == "__main__":
    # The webhook is configured on startup.
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)
