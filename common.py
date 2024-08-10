from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Chat,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
    KeyboardButton,
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)

from telegram.error import TimedOut, NetworkError

import os
import traceback
import json

from custom_filters import *


from constants import *

from DB import DB

import json


def edit_json(name:str, d: dict):
    with open(f"jsons/{name}.json", mode="w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)


def reload_dicts():
    with open("jsons/buy.json", mode="r", encoding="utf-8") as f:
        buy_dicts = json.load(f)
    with open("jsons/sell.json", mode="r", encoding="utf-8") as f:
        sell_dicts = json.load(f)
    return buy_dicts, sell_dicts


buy_dicts, sell_dicts = reload_dicts()

payment_methods_info = {
    ZAIN_CASH: {
        "curr": "dinar",
        "sell": sell_dicts[ZAIN_CASH],
        "buy": buy_dicts[ZAIN_CASH],
        "ar_curr": "دينار عراقي 🇮🇶",
        "kur_curr": "دیناری عێراقی 🇮🇶",
    },
    FIB: {
        "curr": "dinar",
        "sell": sell_dicts[FIB],
        "buy": buy_dicts[FIB],
        "ar_curr": "دينار عراقي 🇮🇶",
        "kur_curr": "دیناری عێراقی 🇮🇶",
    },
    FASTPAY: {
        "curr": "dinar",
        "sell": sell_dicts[FASTPAY],
        "buy": buy_dicts[FASTPAY],
        "ar_curr": "دينار عراقي 🇮🇶",
        "kur_curr": "دیناری عێراقی 🇮🇶",
    },
    USDT: {
        "curr": "usd",
        "sell": sell_dicts[USDT],
        "buy": buy_dicts[USDT],
        "ar_curr": "دولار أميركي 🇺🇸",
        "kur_curr": "دۆلاری ئەمریکی 🇺🇸",
    },
    PERFECT_MONEY: {
        "curr": "usd",
        "sell": sell_dicts[PERFECT_MONEY],
        "buy": buy_dicts[PERFECT_MONEY],
        "ar_curr": "دولار أميركي 🇺🇸",
        "kur_curr": "دۆلاری ئەمریکی 🇺🇸",
    },
    PAYEER: {
        "curr": "usd",
        "sell": sell_dicts[PAYEER],
        "buy": buy_dicts[PAYEER],
        "ar_curr": "دولار أميركي 🇺🇸",
        "kur_curr": "دۆلاری ئەمریکی 🇺🇸",
    },
    WEB_MONEY: {
        "curr": "usd",
        "sell": sell_dicts[WEB_MONEY],
        "buy": buy_dicts[WEB_MONEY],
        "ar_curr": "دولار أميركي 🇺🇸",
        "kur_curr": "دۆلاری ئەمریکی 🇺🇸",
    },
    CASH: {
        "curr": "dinar",
        "sell": sell_dicts[CASH],
        "buy": buy_dicts[CASH],
        "ar_curr": "دينار عراقي 🇮🇶",
        "kur_curr": "دیناری عێراقی 🇮🇶",
    },
    K_CARD: {
        "curr": "dinar",
        "sell": sell_dicts[K_CARD],
        "buy": buy_dicts[K_CARD],
        "ar_curr": "دينار عراقي 🇮🇶",
        "kur_curr": "دیناری عێراقی 🇮🇶",
    },
}


payment_methods_list = [
    USDT,
    PERFECT_MONEY,
    PAYEER,
    WEB_MONEY,
    ZAIN_CASH,
    FIB,
    FASTPAY,
    CASH,
    K_CARD
]

first_method_list = [
    USDT,
    PERFECT_MONEY,
    PAYEER,
    WEB_MONEY,
]

second_method_list = [
    ZAIN_CASH,
    FIB,
    FASTPAY,
    CASH,
    K_CARD
]


def payment_methods_pattern(callback_data: str):
    return callback_data in payment_methods_list


request_buttons = [
    [
        KeyboardButton(
            text="معرفة id مستخدم🆔",
            request_users=KeyboardButtonRequestUsers(request_id=0, user_is_bot=False),
        ),
        KeyboardButton(
            text="معرفة id قناة📢",
            request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=True),
        ),
    ],
    [
        KeyboardButton(
            text="معرفة id مجموعة👥",
            request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=False),
        ),
        KeyboardButton(
            text="معرفة id بوت🤖",
            request_users=KeyboardButtonRequestUsers(request_id=3, user_is_bot=True),
        ),
    ],
]


def build_user_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="بيع💸",
                callback_data="buy",
            ),
        ],
        [
            InlineKeyboardButton(
                text="شراء🛒",
                callback_data="sell",
            ),
        ],
        [
            InlineKeyboardButton(
                text="مساعدة❓",
                url=os.getenv("OWNER_USERNAME"),
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إعدادات الآدمن 🎛",
                callback_data="admin settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="حظر/فك حظر 🔓🔒",
                callback_data="ban unban",
            )
        ],
        [InlineKeyboardButton(text="تغيير أسعار صرف 💱", callback_data="change rates")],
        [
            InlineKeyboardButton(
                text="تفعيل/إلغاء تفعيل وسائل دفع🔂", callback_data="activate methods"
            )
        ],
        [
            InlineKeyboardButton(
                text="تغيير عناوين دفع ✏️", callback_data="wallets settings"
            )
        ],
        [
            InlineKeyboardButton(
                text="إخفاء/إظهار كيبورد معرفة الآيديات 🪄",
                callback_data="hide ids keyboard",
            )
        ],
        [
            InlineKeyboardButton(
                text="رسالة جماعية 👥",
                callback_data="broadcast",
            )
        ],
        [
            InlineKeyboardButton(
                text="تحديث 🔄",
                callback_data="refresh",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_first_method_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text=i, callback_data=i),
        ]
        for i in first_method_list
    ]
    return keyboard


def build_second_method_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text=i, callback_data=i),
        ]
        for i in second_method_list
    ]
    return keyboard


def build_payment_methods_keyboard(op: str = "", first: str = ""):
    if first:
        keyboard = [
            [InlineKeyboardButton(text=i, callback_data=i)]
            for i in payment_methods_info[first][op]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton(text=i, callback_data=i)]
            for i in payment_methods_list
        ]
    return keyboard


async def back_to_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):

        text = "القائمة الرئيسية🔝"
        keyboard = build_user_keyboard()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        return ConversationHandler.END


async def back_to_admin_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="القائمة الرئيسية🔝", reply_markup=build_admin_keyboard()
        )
        return ConversationHandler.END


back_to_user_home_page_handler = CallbackQueryHandler(
    back_to_home_page, "^back to user home page$"
)
back_to_admin_home_page_handler = CallbackQueryHandler(
    back_to_admin_home_page, "^back to admin home page$"
)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, (TimedOut, NetworkError)):
        print("Timed Out")
        return
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    try:
        error = f"""update = {json.dumps(update_str, indent=2, ensure_ascii=False)} 
        
user_data = {str(context.user_data)}
chat_data = {str(context.chat_data)}

{''.join(traceback.format_exception(None, context.error, context.error.__traceback__))}

{'-'*100}


    """

        with open("errors.txt", "a", encoding="utf-8") as f:
            f.write(error)
    except TypeError:
        error = f"""update = TypeError
        
user_data = {str(context.user_data)}
chat_data = {str(context.chat_data)}

{''.join(traceback.format_exception(None, context.error, context.error.__traceback__))}

{'-'*100}


    """

        with open("errors.txt", "a", encoding="utf-8") as f:
            f.write(error)

        await context.bot.send_message(chat_id=755501092, text=error)


back_button = [
    [
        InlineKeyboardButton(
            text="العودة إلى القائمة الرئيسية🔙",
            callback_data="back to admin home page",
        )
    ],
]

back_button_user = [
    [
        InlineKeyboardButton(
            text="العودة إلى القائمة الرئيسية🔙",
            callback_data="back to user home page",
        )
    ],
]


async def user_first_step(update: Update):
    user = DB.get_user(user_id=update.effective_user.id)

    if not user:
        new_user = update.effective_user
        await DB.add_new_user(
            user_id=new_user.id,
            username=new_user.username,
            name=new_user.full_name,
        )
    elif user["banned"]:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text="تم حظرك من استخدام هذا البوت. ❗️"
            )
        else:
            await update.message.reply_text(text="تم حظرك من استخدام هذا البوت. ❗️")
        return False
    return True
