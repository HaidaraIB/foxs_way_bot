from telegram import (
    Update,
    Chat,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters,
)

from custom_filters import *

from DB import DB
import os

from common import (
    build_admin_keyboard,
    reload_dicts,
    back_button,
    back_to_admin_home_page_handler,
    payment_methods_info,
    request_buttons,
)

from start import start_command

from constants import *

(
    USER_ID_TO_BAN_UNBAN,
    BAN_UNBAN_USER,
) = range(2)


async def ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        text = (
            "إرسل آيدي المستخدم الذي تريد حظره/فك الحظر عنه.\n\n"
            "يمكنك استخدام كيبورد معرفة الآيديات، قم بالضغط على /start وإظهاره إن كان مخفياً."
        )
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_button),
        )
        return USER_ID_TO_BAN_UNBAN


async def user_id_to_ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        user = DB.get_user(user_id=int(update.message.text))
        if not user:
            await update.message.reply_text(
                text="لم يتم العثور على المستخدم، تأكد من الآيدي وأعد إرساله. ❌"
            )
            return
        if user["banned"]:
            ban_button = [
                InlineKeyboardButton(
                    text="فك الحظر 🔓", callback_data=f"unban {user['id']}"
                )
            ]
        else:
            ban_button = [
                InlineKeyboardButton(text="حظر 🔒", callback_data=f"ban {user['id']}")
            ]
        keyboard = [
            ban_button,
            [
                InlineKeyboardButton(
                    text="الرجوع🔙", callback_data="back to user id to ban unban"
                )
            ],
            back_button[0],
        ]
        await update.message.reply_text(
            text="هل تريد.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return BAN_UNBAN_USER


back_to_user_id_to_ban_unban = ban_unban


async def ban_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await DB.set_banned(
            user_id=int(update.callback_query.data.split(" ")[-1]),
            banned=1 if update.callback_query.data.startswith("ban") else 0,
        )

        await update.callback_query.edit_message_text(
            text="تمت العملية بنجاح ✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


async def hide_ids_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if (
            not context.user_data.get("request_keyboard_hidden", None)
            or not context.user_data["request_keyboard_hidden"]
        ):
            context.user_data["request_keyboard_hidden"] = True
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="تم الإخفاء✅",
                reply_markup=ReplyKeyboardRemove(),
            )
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="القائمة الرئيسية🔝",
                reply_markup=build_admin_keyboard(),
            )
        else:
            context.user_data["request_keyboard_hidden"] = False
            
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="تم الإظهار✅",
                reply_markup=ReplyKeyboardMarkup(request_buttons, resize_keyboard=True),
            )
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="القائمة الرئيسية🔝",
                reply_markup=build_admin_keyboard(),
            )

async def find_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.effective_message.users_shared:
            await update.message.reply_text(
                text=f"🆔: <code>{update.effective_message.users_shared.user_ids[0]}</code>",
            )
        else:
            await update.message.reply_text(
                text=f"🆔: <code>{update.effective_message.chat_shared.chat_id}</code>",
            )

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):

        buy_dicts, sell_dicts = reload_dicts()

        for method in payment_methods_info:
            payment_methods_info[method]['sell'] = sell_dicts[method]
            payment_methods_info[method]['buy'] = buy_dicts[method]
        
        if update.callback_query:
            await update.callback_query.answer("تم التحديث ✅")


async def restart(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(os.getenv("OWNER_ID")):
        context.bot_data["restart"] = True
        context.application.stop_running()


async def stop(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(os.getenv("OWNER_ID")):
        context.application.stop_running()

restart_handler = CommandHandler('restart', restart)

stop_handler = CommandHandler('stop', stop)

refresh_handler = CallbackQueryHandler(refresh, "^refresh$")

find_id_handler = MessageHandler(
    filters=filters.StatusUpdate.USER_SHARED | filters.StatusUpdate.CHAT_SHARED,
    callback=find_id,
)

hide_ids_keyboard_handler = CallbackQueryHandler(
    callback=hide_ids_keyboard, pattern="^hide ids keyboard$"
)

ban_unban_user_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            ban_unban,
            "^ban unban$",
        ),
    ],
    states={
        USER_ID_TO_BAN_UNBAN: [
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=user_id_to_ban_unban,
            )
        ],
        BAN_UNBAN_USER: [CallbackQueryHandler(ban_unban_user, "^ban \d+$|^unban \d+$")],
    },
    fallbacks=[
        start_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(
            back_to_user_id_to_ban_unban, "^back to user id to ban unban$"
        ),
    ],
)
