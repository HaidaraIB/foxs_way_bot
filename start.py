from telegram import (
    Update,
    Chat,
    Bot,
    ReplyKeyboardMarkup,
    BotCommand,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    Application,
    ConversationHandler,
)

from telegram.constants import (
    ParseMode,
)

from DB import DB

from common import (
    build_user_keyboard,
    build_admin_keyboard,
    payment_methods_list,
    request_buttons,
)
from constants import *


async def inits(app: Application):
    bot: Bot = app.bot
    await bot.set_my_commands(
        commands=[BotCommand(command="start", description="home page")]
    )

    if not app.bot_data.get("USD_TO_DINAR", None):
        app.bot_data["USD_TO_DINAR"] = 1309

    if not app.bot_data.get("DINAR_TO_USD", None):
        app.bot_data["DINAR_TO_USD"] = 0.00076

    for p in payment_methods_list:
        if not app.bot_data.get(p, None):

            if p == CASH:
                app.bot_data[p] = "اربيل - عينكاوة - شارع المنتزه\n009647511230235"
                continue
            elif p == K_CARD:
                app.bot_data[p] = {
                    "account": 7131355377,
                    "card": 5556960147527602,
                }
                continue

            app.bot_data[p] = 123456

    if not app.bot_data.get("activate_buy", False):
        app.bot_data["activate_buy"] = {
            "first_method": {
                USDT: True,
                PERFECT_MONEY: True,
                PAYEER: True,
                WEB_MONEY: True,
                FIB: True,
                FASTPAY: True,
                ZAIN_CASH: True,
                CASH: True,
                K_CARD:True,
            },
            "second_method": {
                USDT: True,
                PERFECT_MONEY: True,
                PAYEER: True,
                WEB_MONEY: True,
                FIB: True,
                FASTPAY: True,
                ZAIN_CASH: True,
                CASH: True,
                K_CARD:True,
            },
        }
        app.bot_data["activate_sell"] = {
            "first_method": {
                USDT: True,
                PERFECT_MONEY: True,
                PAYEER: True,
                WEB_MONEY: True,
                FIB: True,
                FASTPAY: True,
                ZAIN_CASH: True,
                CASH: True,
                K_CARD:True,
            },
            "second_method": {
                USDT: True,
                PERFECT_MONEY: True,
                PAYEER: True,
                WEB_MONEY: True,
                FIB: True,
                FASTPAY: True,
                ZAIN_CASH: True,
                CASH: True,
                K_CARD:True,
            },
        }

    app.bot_data["restart"] = False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        admin = DB.check_admin(user_id=update.effective_user.id)
        if admin:
            if (
                not context.user_data.get("request_keyboard_hidden", None)
                or not context.user_data["request_keyboard_hidden"]
            ):
                context.user_data["request_keyboard_hidden"] = False

                await update.message.reply_text(
                    text="أهلاً بك...",
                    reply_markup=ReplyKeyboardMarkup(
                        request_buttons, resize_keyboard=True
                    ),
                )
            else:
                await update.message.reply_text(
                    text="أهلاً بك...",
                    reply_markup=ReplyKeyboardRemove(),
                )

            text = "تعمل الآن كآدمن🕹"
            keyboard = build_admin_keyboard()

        else:
            old_user = DB.get_user(user_id=update.effective_user.id)
            if not old_user:
                new_user = update.effective_user
                await DB.add_new_user(
                    user_id=new_user.id,
                    username=new_user.username,
                    name=new_user.full_name,
                )
            elif old_user["banned"]:
                await update.message.reply_text(text="تم حظرك من استخدام هذا البوت. ❗️")
                return

            text = f"""السلام عليكم ، يرجى اختيار طلبك من القائمة واتباع الخطوات لإكمال العملية بنجاح.

{'-'*50}

سڵاوتان لێبێت، تکایە داواکارییەکەت لە لیستەکەدا هەڵبژێرە و هەنگاوەکانی تەواوکردنی پرۆسەکە بە سەرکەوتوویی پەیڕەو بکە"""
            keyboard = build_user_keyboard()

        await update.message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
        return ConversationHandler.END


start_command = CommandHandler(command="start", callback=start)