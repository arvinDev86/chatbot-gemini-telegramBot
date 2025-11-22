import logging
import google.generativeai as genai
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ---------------- تنظیمات اولیه ----------------

# توکن ربات تلگرام خود را اینجا قرار دهید
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# کلید API جمینی خود را اینجا قرار دهید
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# تنظیمات لاگینگ (برای دیدن خطاها در کنسول)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# اتصال به گوگل جمینی
genai.configure(api_key=GEMINI_API_KEY)
# مدل مورد نظر (gemini-pro برای متن عالی است)
model = genai.GenerativeModel('gemini-2.5-flash')

# ---------------- توابع ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    # پیام خوش‌آمدگویی هم با فرمت مارک‌داون
    text = f"سلام *{user_name}*! 👋\n من آماده صحبت کردن با شما هستم."
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def chat_with_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # نمایش وضعیت تایپینگ
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        response = model.generate_content(user_text)
        bot_reply = response.text
        
        # تلاش برای ارسال با فرمت Markdown (برای نمایش زیبای کدها)
        try:
            await update.message.reply_text(bot_reply, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            # اگر فرمت مارک‌داون جمینی با تلگرام سازگار نبود، متن ساده بفرست تا ارور ندهد
            await update.message.reply_text(bot_reply)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("خطایی رخ داد. لطفاً دوباره تلاش کنید.")

# ---------------- اجرا ----------------

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat_with_gemini)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    print("ربات با قابلیت نمایش کد (Monospace) روشن شد...")
    application.run_polling()