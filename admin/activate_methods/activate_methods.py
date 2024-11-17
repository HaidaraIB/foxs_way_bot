from telegram import (
    Chat,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

from constants import *
from custom_filters import Admin
from common import (
    back_button,
    first_method_list,
    second_method_list,
    payment_methods_list,
    back_to_admin_home_page_handler,
)
from start import start_command

(
    BUY_SELL,
    STEP,
    METHOD_TO_TURN_ON_OR_OFF,
) = range(3)


def activate_methods_pattern(callback_data: dict):
    return (
        isinstance(callback_data, dict)
        and callback_data.get("method", False)
        and callback_data["method"] in payment_methods_list
    )


on_off_dict = {
    True: "✅",
    False: "❌",
}

steps_keyboard = [
    [
        InlineKeyboardButton(text="الخيار الأول1️⃣", callback_data="first_method"),
        InlineKeyboardButton(text="الخيار الثاني2️⃣", callback_data="second_method"),
    ],
    [InlineKeyboardButton(text="الرجوع🔙", callback_data="back to buy_sell")],
    back_button[0],
]


def build_activate_methods_keyboard(step: str, op: str, activate_dict: dict):
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{i} {on_off_dict[activate_dict[i]]}",
                callback_data={
                    "op": op,
                    "step": step,
                    "method": i,
                },
            )
        ]
        for i in (first_method_list if step == 'first_method' else second_method_list)
    ]
    keyboard.append(
        [InlineKeyboardButton(text="الرجوع🔙", callback_data="back to step")]
    )
    keyboard.append(back_button[0])
    return keyboard


async def turn_methods_on_or_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = [
            [
                InlineKeyboardButton(text="بيع💸", callback_data="activate_buy"),
                InlineKeyboardButton(text="شراء🛒", callback_data="activate_sell"),
            ],
            back_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="اختر العملية", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return BUY_SELL


async def buy_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        context.user_data["buy_sell"] = update.callback_query.data
        await update.callback_query.edit_message_text(
            text="اختر الخيار", reply_markup=InlineKeyboardMarkup(steps_keyboard)
        )
        return STEP


back_to_buy_sell = turn_methods_on_or_off


async def step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not context.bot_data.get(
            context.user_data["buy_sell"], False
        ) or not context.bot_data[context.user_data["buy_sell"]].get(
            update.callback_query.data, False
        ):
            context.bot_data[context.user_data["buy_sell"]] = {
                update.callback_query.data: {
                    USDT: True,
                    PERFECT_MONEY: True,
                    PAYEER: True,
                    WEB_MONEY: True,
                    FIB: True,
                    FASTPAY: True,
                    ZAIN_CASH: True,
                    CASH: True,
                    K_CARD: True,
                }
            }
        context.user_data["step"] = update.callback_query.data
        await update.callback_query.edit_message_text(
            text="اختر الوسيلة:",
            reply_markup=InlineKeyboardMarkup(
                build_activate_methods_keyboard(
                    step=update.callback_query.data,
                    op=context.user_data["buy_sell"],
                    activate_dict=context.bot_data[context.user_data["buy_sell"]][
                        update.callback_query.data
                    ],
                )
            ),
        )
        return METHOD_TO_TURN_ON_OR_OFF


async def back_to_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):

        await update.callback_query.edit_message_text(
            text="اختر الخيار", reply_markup=InlineKeyboardMarkup(steps_keyboard)
        )
        return STEP


async def method_to_turn_on_or_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        data = update.callback_query.data
        if context.bot_data[context.user_data["buy_sell"]][context.user_data["step"]][
            data["method"]
        ]:
            context.bot_data[context.user_data["buy_sell"]][context.user_data["step"]][
                data["method"]
            ] = False
            await update.callback_query.answer(
                text="تم إيقاف الوسيلة✅",
                show_alert=True,
            )
        else:
            context.bot_data[context.user_data["buy_sell"]][context.user_data["step"]][
                data["method"]
            ] = True
            await update.callback_query.answer(
                text="تم تشغيل الوسيلة✅",
                show_alert=True,
            )
        await update.callback_query.edit_message_text(
            text="اختر الوسيلة، للإنهاء عد إلى القائمة الرئيسية.",
            reply_markup=InlineKeyboardMarkup(
                build_activate_methods_keyboard(
                    step=context.user_data["step"],
                    op=context.user_data["buy_sell"],
                    activate_dict=context.bot_data[context.user_data["buy_sell"]][
                        context.user_data["step"]
                    ],
                )
            ),
        )


activate_methods_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            turn_methods_on_or_off,
            "^activate methods$",
        ),
    ],
    states={
        BUY_SELL: [
            CallbackQueryHandler(
                buy_sell,
                "^activate_buy$|^activate_sell$",
            )
        ],
        STEP: [
            CallbackQueryHandler(
                step,
                "^first_method$|^second_method$",
            )
        ],
        METHOD_TO_TURN_ON_OR_OFF: [
            CallbackQueryHandler(
                method_to_turn_on_or_off,
                activate_methods_pattern,
            )
        ],
    },
    fallbacks=[
        back_to_admin_home_page_handler,
        start_command,
        CallbackQueryHandler(
            back_to_step,
            "^back to step$",
        ),
        CallbackQueryHandler(
            back_to_buy_sell,
            "^back to buy_sell$",
        ),
    ],
)
