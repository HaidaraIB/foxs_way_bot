from telegram import Update, Chat, ReplyKeyboardMarkup, BotCommand, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ContextTypes, Application, ConversationHandler
from telegram.constants import ParseMode
from DB import DB
from custom_filters import Admin
from common import build_user_keyboard, build_admin_keyboard, request_buttons
from constants import *

async def inits(app: Application):
    app.bot_data["restart"] = False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        await context.bot.set_my_commands(
            commands=[
                BotCommand(
                    command="start",
                    description="home page",
                )
            ]
        )
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

        text = (
            f"السلام عليكم ، يرجى اختيار طلبك من القائمة واتباع الخطوات لإكمال العملية بنجاح.\n\n"
            f"{'-'*50}\n\n"
            "سڵاوتان لێبێت، تکایە داواکارییەکەت لە لیستەکەدا هەڵبژێرە و هەنگاوەکانی تەواوکردنی پرۆسەکە بە سەرکەوتوویی پەیڕەو بکە"
        )

        await update.message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=build_user_keyboard(),
        )
        return ConversationHandler.END


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await context.bot.set_my_commands(
            commands=[
                BotCommand(
                    command="start",
                    description="home page",
                ),
                BotCommand(
                    command="admin",
                    description="admin page",
                ),
            ]
        )
        if (
            not context.user_data.get("request_keyboard_hidden", None)
            or not context.user_data["request_keyboard_hidden"]
        ):
            context.user_data["request_keyboard_hidden"] = False

            await update.message.reply_text(
                text="أهلاً بك...",
                reply_markup=ReplyKeyboardMarkup(request_buttons, resize_keyboard=True),
            )
        else:
            await update.message.reply_text(
                text="أهلاً بك...",
                reply_markup=ReplyKeyboardRemove(),
            )

        await update.message.reply_text(
            text="تعمل الآن كآدمن🕹",
            parse_mode=ParseMode.HTML,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


start_command = CommandHandler(command="start", callback=start)
admin_command = CommandHandler(command="admin", callback=admin)
