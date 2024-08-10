from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Chat,
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)


from custom_filters.Admin import Admin

from common import (
    build_admin_keyboard,
    build_payment_methods_keyboard,
    payment_methods_pattern,
    back_to_admin_home_page_handler,
    back_button,
    K_CARD,
)

from start import start_command


(CHOOSE_METHOD_TO_UPDATE, NEW_CODE, NEW_CARD_NUM) = range(3)


async def wallets_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        methods = build_payment_methods_keyboard()
        methods.append(back_button[0])
        await update.callback_query.edit_message_text(
            text="اختر وسيلة الدفع💳.",
            reply_markup=InlineKeyboardMarkup(methods),
        )
        return CHOOSE_METHOD_TO_UPDATE


async def choose_method_to_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            context.user_data["wallet_settings_method"] = update.callback_query.data

            if update.callback_query.data.startswith("USDT"):
                wallet_or_number = "عنوان محفظة"
            elif update.callback_query.data == "Cash - الدفع نقدي 💰":
                wallet_or_number = "عنوان"
            else:
                wallet_or_number = "رقم حساب"

            context.user_data["wallet_or_number"] = wallet_or_number

        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙", callback_data="back to wallets settings"
                )
            ],
            back_button[0],
        ]
        wallet_or_number = context.user_data["wallet_or_number"]
        method = context.user_data["wallet_settings_method"]

        text = (
            f"أرسل {wallet_or_number} {method} الجديد\n\n"
            "القيمة الحالية:\n<code>{}</code>".format(
                context.bot_data[method]["account"]
                if method == K_CARD
                else context.bot_data[method]
            )
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return NEW_CODE


back_to_wallets_settings = wallets_settings


async def new_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):

        method = context.user_data["wallet_settings_method"]

        if method == K_CARD:
            context.bot_data[context.user_data["wallet_settings_method"]][
                "account"
            ] = update.message.text
            back_buttons = [
                [
                    InlineKeyboardButton(
                        text="الرجوع🔙", callback_data="back to new code"
                    )
                ],
                back_button[0],
            ]
            await update.message.reply_text(
                text=f"أرسل رقم البطاقة الجديد:\nالرقم الحالي هو: {context.bot_data[K_CARD]['card']}",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return NEW_CARD_NUM

        context.bot_data[context.user_data["wallet_settings_method"]] = (
            update.message.text
        )
        wallet_or_number = context.user_data["wallet_or_number"]

        text = f"تم تغيير {wallet_or_number} <b>{method}</b> ينجاح✅"

        await update.message.reply_text(
            text=text,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


back_to_new_code = choose_method_to_update


async def new_card_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        context.bot_data[K_CARD]["card"] = update.message.text
        text = f"تم تغيير رقم بطاقة <b>Qi Card - كي كارد الرافدين 💳</b> ينجاح✅"
        await update.message.reply_text(
            text=text,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


wallets_settings_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(wallets_settings, "^wallets settings$")],
    states={
        CHOOSE_METHOD_TO_UPDATE: [
            CallbackQueryHandler(choose_method_to_update, payment_methods_pattern)
        ],
        NEW_CODE: [
            MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=new_code)
        ],
        NEW_CARD_NUM: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND, callback=new_card_num
            )
        ],
    },
    fallbacks=[
        start_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(back_to_wallets_settings, "^back to wallets settings$"),
        CallbackQueryHandler(back_to_new_code, "^back to new code$"),
    ],
)
