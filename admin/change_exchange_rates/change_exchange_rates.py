from telegram import (
    Update,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from custom_filters import Admin

from admin.admin_calls.admin_calls import refresh

from common import (
    back_button,
    back_to_admin_home_page_handler,
    build_admin_keyboard,
    build_first_method_keyboard,
    build_second_method_keyboard,
    payment_methods_pattern,
    reload_dicts,
    edit_json,
)

from start import (
    start_command,
)

(
    CHOOSE_RATE,
    CHOOSE_FIRST,
    CHOOSE_SECOND,
    NEW_RATE,
) = range(4)

back_buttons = [
    [
        InlineKeyboardButton(
            text="الرجوع🔙",
            callback_data="back to choose rate",
        ),
    ],
    back_button[0],
]


async def change_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        rates_keyboard = [
            [
                InlineKeyboardButton(
                    text="دولار إلى دينار 🇺🇸 ⬅️ 🇮🇶",
                    callback_data="USD_TO_DINAR",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="دينار إلى دولار 🇮🇶 ⬅️ 🇺🇸",
                    callback_data="DINAR_TO_USD",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="نسب بيع💸",
                    callback_data="change_buy_percentages",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="نسب شراء🛒",
                    callback_data="change_sell_percentages",
                ),
            ],
            back_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="ما الذي تريد تعديله؟",
            reply_markup=InlineKeyboardMarkup(rates_keyboard),
        )
        return CHOOSE_RATE


async def change_percentages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("back"):
            buy_or_sell = context.user_data["buy_or_sell"]
        else:
            buy_or_sell = update.callback_query.data.split("_")[1]
            context.user_data["buy_or_sell"] = buy_or_sell
        keyboard = build_first_method_keyboard() + back_buttons
        if buy_or_sell == "buy":
            text = "تغيير نسب بيع، ماذا تريد أن تبيع؟"
        else:
            text = "تغيير نسب شراء، ما الذي تريد شراءه؟"
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_FIRST


async def choose_first(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith('back'):
            context.user_data["first_to_change"] = update.callback_query.data
        keyboard = build_second_method_keyboard()
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to first",
                ),
            ],
        )
        await update.callback_query.edit_message_text(
            text="مقابل؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_SECOND


back_to_first = change_percentages


async def choose_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        context.user_data["chosen_rate"] = update.callback_query.data
        if update.callback_query.data in ["USD_TO_DINAR", "DINAR_TO_USD"]:
            back_to_second = False
            curr = "دينار" if update.callback_query.data == "USD_TO_DINAR" else "دولار"
            text = f"القيمة الحالية هي: {context.bot_data[update.callback_query.data]} {curr}\nأرسل القيمة الجديدة."
        else:
            buy_dicts, sell_dicts = reload_dicts()
            back_to_second = True
            if context.user_data["buy_or_sell"] == 'sell':
                curr = sell_dicts[context.user_data["first_to_change"]][update.callback_query.data]
                text = f"القيمة الحالية هي:\n{curr}\nأرسل القيمة الجديدة."
            else:
                curr = buy_dicts[context.user_data["first_to_change"]][update.callback_query.data]
                text = f"القيمة الحالية هي:\n{curr}\nأرسل القيمة الجديدة."
        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to second" if back_to_second else "back to choose rate",
                ),
            ],
            back_button[0],
        ]
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons)
        )
        return NEW_RATE


back_to_second = choose_first

back_to_choose_rate = change_rates


async def new_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if context.user_data["chosen_rate"] in ["USD_TO_DINAR", "DINAR_TO_USD"]:
            context.bot_data[context.user_data["chosen_rate"]] = float(update.message.text)
        else:
            buy_dicts, sell_dicts = reload_dicts()
            if context.user_data["buy_or_sell"] == 'buy':
                buy_dicts[context.user_data["first_to_change"]][context.user_data["chosen_rate"]] = float(update.message.text)
                edit_json(name='buy', d=buy_dicts)
            else:
                sell_dicts[context.user_data["first_to_change"]][context.user_data["chosen_rate"]] = float(update.message.text)
                edit_json(name='sell', d=sell_dicts)
            await refresh(update, context)
        await update.message.reply_text(
            text="تمت العملية بنجاح✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


change_rates_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            change_rates,
            "change rates",
        ),
    ],
    states={
        CHOOSE_RATE: [
            CallbackQueryHandler(
                choose_rate,
                "^DINAR_TO_USD$|^USD_TO_DINAR$",
            ),
            CallbackQueryHandler(
                change_percentages,
                "^change_buy_percentages$|^change_sell_percentages$",
            )
        ],
        CHOOSE_FIRST: [
            CallbackQueryHandler(
                choose_first,
                payment_methods_pattern,
            )

        ],
        CHOOSE_SECOND: [
            CallbackQueryHandler(
                choose_rate,
                payment_methods_pattern,
            )

        ],
        NEW_RATE: [
            MessageHandler(
                filters=filters.Regex("^-?\d+\.?\d*$"),
                callback=new_rate,
            )
        ],
    },
    fallbacks=[
        start_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(back_to_choose_rate, "^back to choose rate$"),
        CallbackQueryHandler(back_to_second, "^back to second$"),
        CallbackQueryHandler(back_to_first, "^back to first$"),
    ],
)
