import logging
import os
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import BadRequest, NetworkError, TimedOut

# فعال‌سازی لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن ربات شما
TOKEN = "6542041216:AAFcxbb3DApZ8CAIRQ2Tm7B-NbzFmt--CVQ"

# --- بخشی که باید تنظیم کنید ---
# آیدی عددی مدیر اصلی که می‌تواند تنظیمات را مدیریت کند
# آیدی خودتان را از ربات @userinfobot بگیرید و اینجا قرار دهید
ADMIN_USER_ID = 6196578711 # <--- آیدی عددی خود را اینجا قرار دهید
# --- پایان بخشی که باید تنظیم کنید ---

# نام فایل‌های پیکربندی
CONFIG_FILE = 'config.json'
MEDIA_MAP_FILE = 'media_map.json'

# بارگذاری تنظیمات از فایل
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # اگر فایل وجود نداشت، یک تنظیمات پیش‌فرض می‌سازیم
    default_config = {
        "required_channels": [
            {"id": "@aeah1am", "name": "کانال اول"},
            {"id": "@VelvetWhisper_AY", "name": "کانال دوم"}
        ],
        "payment_contact_id": "@uhftgrt",
        "source_channel_id": -1003251983791
    }
    save_config(default_config)
    return default_config

# ذخیره تنظیمات در فایل
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# بارگذاری نقشه رسانه‌ها از فایل
def load_media_map():
    if os.path.exists(MEDIA_MAP_FILE):
        with open(MEDIA_MAP_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    default_map = {
        "1": [33, 34, 35, 36, 37, 38, 39, 40, 41, 42],
        "2": [43, 44, 45, 46, 47, 48, 49],
        "3": [50, 51, 52, 53, 54, 55],
        "4": [56],
	"5": [58],
	"6": [59], 
	"7": [61, 62, 63],
    }
    save_media_map(default_map)
    return default_map

# ذخیره نقشه رسانه‌ها در فایل
def save_media_map(media_map):
    with open(MEDIA_MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(media_map, f, ensure_ascii=False, indent=4)

# بارگذاری اولیه تنظیمات و رسانه‌ها
CONFIG = load_config()
MEDIA_MAP = load_media_map()

# --- شروع بخش جدید: دستورات مدیریتی برای کانال‌ها ---
async def add_channel_command(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("این دستور فقط برای مدیر مجاز است.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("مثال: /addchannel @newchannel نام_کانال_جدید")
        return
    
    channel_id = context.args[0]
    channel_name = " ".join(context.args[1:])
    
    # جلوگیری از تکرار
    if any(ch['id'] == channel_id for ch in CONFIG['required_channels']):
        await update.message.reply_text("این کانال از قبل در لیست وجود دارد.")
        return

    CONFIG['required_channels'].append({"id": channel_id, "name": channel_name})
    save_config(CONFIG)
    await update.message.reply_text(f"✅ کانال '{channel_name}' با موفقیت اضافه شد.")
    logger.info(f"Admin added channel: {channel_id} ({channel_name})")

async def list_channels_command(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("این دستور فقط برای مدیر مجاز است.")
        return
    
    if not CONFIG['required_channels']:
        await update.message.reply_text("هیچ کانال اجباری تعریف نشده است.")
        return
    
    response_text = "📋 لیست کانال‌های اجباری:\n\n"
    for ch in CONFIG['required_channels']:
        response_text += f"• **{ch['name']}** (`{ch['id']}`)\n"
    
    await update.message.reply_text(response_text, parse_mode='Markdown')

async def remove_channel_command(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("این دستور فقط برای مدیر مجاز است.")
        return
    if not context.args:
        await update.message.reply_text("مثال: /removechannel @newchannel")
        return
    
    channel_id_to_remove = context.args[0]
    original_length = len(CONFIG['required_channels'])
    CONFIG['required_channels'] = [ch for ch in CONFIG['required_channels'] if ch['id'] != channel_id_to_remove]
    
    if len(CONFIG['required_channels']) < original_length:
        save_config(CONFIG)
        await update.message.reply_text(f"✅ کانال '{channel_id_to_remove}' با موفقیت حذف شد.")
        logger.info(f"Admin removed channel: {channel_id_to_remove}")
    else:
        await update.message.reply_text(f"کانال '{channel_id_to_remove}' در لیست یافت نشد.")
# --- پایان بخش جدید ---


# --- شروع بخش جدید: دستورات مدیریتی برای رسانه ---
async def add_media_command(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("این دستور فقط برای مدیر مجاز است.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("مثال: /addmedia مجموعه_جدید 25 26 27")
        return
    keyword = context.args[0]
    try:
        message_ids = list(map(int, context.args[1:]))
        MEDIA_MAP[keyword] = message_ids
        save_media_map(MEDIA_MAP)
        await update.message.reply_text(f"✅ کلمه کلیدی '{keyword}' با {len(message_ids)} آیدی با موفقیت آپدیت شد.")
        logger.info(f"Admin updated keyword '{keyword}' with IDs: {message_ids}")
    except ValueError:
        await update.message.reply_text("خطا: تمام آیدی‌ها باید عدد باشند. مثال: /addmedia مجموعه_جدید 25 26 27")

async def list_media_command(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("این دستور فقط برای مدیر مجاز است.")
        return
    if not MEDIA_MAP:
        await update.message.reply_text("هیچ رسانه‌ای تعریف نشده است.")
        return
    response_text = "📋 لیست رسانه‌های فعلی:\n\n"
    for keyword, ids in MEDIA_MAP.items():
        response_text += f"• `{keyword}`: {len(ids)} آیدی\n"
    await update.message.reply_text(response_text, parse_mode='Markdown')

async def delete_media_command(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("این دستور فقط برای مدیر مجاز است.")
        return
    if not context.args:
        await update.message.reply_text("مثال: /deletemedia مجموعه")
        return
    keyword = context.args[0]
    if keyword in MEDIA_MAP:
        del MEDIA_MAP[keyword]
        save_media_map(MEDIA_MAP)
        await update.message.reply_text(f"✅ کلمه کلیدی '{keyword}' با موفقیت حذف شد.")
        logger.info(f"Admin deleted keyword '{keyword}'.")
    else:
        await update.message.reply_text(f"کلمه کلیدی '{keyword}' یافت نشد.")
# --- پایان بخش جدید ---


# این تابع عضویت کاربر را در کانال‌های اجباری بررسی می‌کند
async def check_membership(context: CallbackContext, user_id: int) -> (bool, list):
    unchecked_channels = []
    is_member_of_checkable_channels = True
    # استفاده از لیست کانال‌ها از فایل کانفیگ
    for channel in CONFIG['required_channels']:
        channel_id = channel['id']
        channel_name = channel['name']
        channel_link = f"https://t.me/{channel_id.lstrip('@')}"
        try:
            logger.info(f"در حال بررسی عضویت کاربر {user_id} در {channel_name} ({channel_id})...")
            await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            logger.info(f"✅ کاربر {user_id} در {channel_name} عضو است.")
        except BadRequest as e:
            logger.warning(f"⚠️ نمی‌توان عضویت را در {channel_name} بررسی کرد. دلیل: {e.message}. (ربات احتمالاً مدیر نیست)")
            unchecked_channels.append((channel_name, channel_link))
        except (NetworkError, TimedOut) as e:
            logger.error(f"🔌 خطای شبکه در حین بررسی {channel_name}: {e}")
            is_member_of_checkable_channels = False
            return (False, [])
        except Exception as e:
            logger.error(f"⚠️ خطای پیش‌بینی نشده در بررسی {channel_name}: {e}")
            is_member_of_checkable_channels = False
            return (False, [])
    return (is_member_of_checkable_channels, unchecked_channels)


# این تابع پیام‌ها را پس از 60 ثانیه حذف کرده و یک پیام متنی جدید ارسال می‌کند
async def schedule_self_destruct(context: CallbackContext, chat_id: int, message_ids: list[int]):
    await asyncio.sleep(60)
    try:
        for message_id in message_ids:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await context.bot.send_message(chat_id=chat_id, text="⏳ این محتوا پس از یک دقیقه خودکارسازی شد.")
        logger.info(f"Messages {message_ids} in chat {chat_id} were self-destructed.")
    except Exception as e:
        logger.warning(f"Could not self-destruct messages {message_ids} in chat {chat_id}: {e}")


# این تابع رسانه(ها) را ارسال کرده و سپس پیام تبلیغاتی VIP را می‌فرستد
async def send_media_by_keyword(update: Update, context: CallbackContext, keyword: str):
    message_ids = MEDIA_MAP.get(keyword)
    if not message_ids:
        await update.message.reply_text("رسانه‌ای برای این لینک پیدا نشد.")
        return
    logger.info(f"در حال کپی کردن {len(message_ids)} پیام از کانال ذخیره‌سازی برای کلمه کلیدی '{keyword}'")
    sent_message_ids = []
    try:
        for msg_id in message_ids:
            try:
                copied_message = await context.bot.copy_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=CONFIG['source_channel_id'],
                    message_id=msg_id
                )
                sent_message_ids.append(copied_message.message_id)
                logger.info(f"پیام با آیدی {msg_id} با موفقیت کپی شد. آیدی جدید: {copied_message.message_id}")
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Could not copy message {msg_id}: {e}")
        if sent_message_ids:
            asyncio.create_task(schedule_self_destruct(context, update.effective_chat.id, sent_message_ids))
            logger.info(f"زمان‌بندی خودکارسازی برای {len(sent_message_ids)} پیام فعال شد")
            await asyncio.sleep(2)
            await update.message.reply_text(
                "🔥 برای دسترسی به هزاران محتوای بیشتر و بدون محدودیت، عضو کانال VIP ما شوید!\n\n"
                "💰 هزینه اشتراک: یک بار برای همیشه\n\n"
                "👤 برای عضویت و اطلاعات بیشتر، به آیدی زیر پیام دهید:\n"
                f"**{CONFIG['payment_contact_id']}**",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("هیچ فایلی برای ارسال پیدا نشد.")
    except Exception as e:
        logger.error(f"Error sending media for keyword '{keyword}': {e}")
        await update.message.reply_text("متاسفانه در ارسال محتوا مشکلی پیش آمد.")


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    try:
        is_member, unchecked = await check_membership(context, user_id)
        if not is_member:
            await update.message.reply_text(
                "⚠️ برای استفاده از ربات، باید عضو کانال زیر باشید:\n\n"
                f"[{CONFIG['required_channels'][0]['name']}](https://t.me/{CONFIG['required_channels'][0]['id'].lstrip('@')})\n\n"
                "پس از عضویت، لطفاً دوباره تلاش کنید.",
                disable_web_page_preview=True,
                parse_mode='Markdown'
            )
            return
        if unchecked:
            keyboard = [[InlineKeyboardButton(f"➡️ عضویت در {name}", url=link)] for name, link in unchecked]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "✅ دسترسی شما تایید شد.\n\n"
                "⚠️ توجه: برای اطمینان از دریافت محتوای کامل، لطفاً روی دکمه(های) زیر کلیک کرده و در کانال(های) مربوطه عضو شوید.",
                reply_markup=reply_markup
            )
            await asyncio.sleep(1)
        if context.args:
            keyword = context.args[0]
            await send_media_by_keyword(update, context, keyword)
        else:
            await update.message.reply_text(
                "سلام! 👋\n\n"
                "این ربات فقط از طریق لینک‌های اختصاصی کار می‌کند.\n"
                "لطفاً از لینک معتبری برای مشاهده محتوا استفاده کنید.\n\n"
                "توجه: محتوا پس از یک دقیقه خودکار پاک سازی می‌شود."
            )
    except (NetworkError, TimedOut):
        await update.message.reply_text("خطا در اتصال به سرور تلگرام. لطفاً چند لحظه دیگر دوباره تلاش کنید.")
        return
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await update.message.reply_text("خطایی رخ داد. لطفاً بعداً تلاش کنید.")
        return


def main() -> None:
    if ADMIN_USER_ID == 123456789:
        print("⚠️ لطفاً ابتدا ADMIN_USER_ID را در کد خود با آیدی عددی خودتان جایگزین کنید.")
        return
    print("ربات با قابلیت مدیریت کامل از راه دور راه‌اندازی شد.")
    application = Application.builder().token(TOKEN).connect_timeout(20.0).read_timeout(90.0).write_timeout(90.0).pool_timeout(10.0).build()
    # اضافه کردن تمام هندلرهای مدیریتی
    application.add_handler(CommandHandler("addchannel", add_channel_command))
    application.add_handler(CommandHandler("listchannels", list_channels_command))
    application.add_handler(CommandHandler("removechannel", remove_channel_command))
    application.add_handler(CommandHandler("addmedia", add_media_command))
    application.add_handler(CommandHandler("listmedia", list_media_command))
    application.add_handler(CommandHandler("deletemedia", delete_media_command))
    # هندلرهای اصلی
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start))
    application.run_polling()
    logger.info("ربات با قابلیت مدیریت کامل از راه دور با موفقیت شروع به کار کرد!")

async def error_handler(update: object, context: CallbackContext) -> None:
    logger.error('Exception while handling an update: %s', context.error)
    try:
        if isinstance(context.error, NetworkError): await update.message.reply_text("خطای شبکه! لطفاً بعداً تلاش کنید.")
        elif isinstance(context.error, TimedOut): await update.message.reply_text("زمان اتصال به سرور تمام شد! لطفاً بعداً تلاش کنید.")
        else: await update.message.reply_text("خطایی رخ داد. لطفاً بعداً تلاش کنید.")
    except Exception: pass

if __name__ == '__main__':
    main()
