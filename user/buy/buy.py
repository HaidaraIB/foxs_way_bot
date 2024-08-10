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

from custom_filters import User

from common import (
    build_user_keyboard,
    build_first_method_keyboard,
    build_second_method_keyboard,
    payment_methods_pattern,
    user_first_step,
    payment_methods_info,
    back_button_user,
    back_to_user_home_page_handler,
)

from start import (
    start_command,
)

from constants import *
from DB import DB
import os
import datetime

(
    CHOOSE_SEND_METHOD,
    CHOOSE_TAKE_METHOD,
    AMOUNT_TO_BUY,
    WALLET,
    K_CARD_BUY_WAL_NUM,
    SCREEN_SHOT,
) = range(6)


async def send_money_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    back_buttons: list[list[InlineKeyboardButton]],
    exchange_amount_text: str = "",
    exchange_amount_kur_text: str = "",
):
    send_method = context.user_data["send_buy_method"]
    if send_method == USDT:
        text = (
            f"{exchange_amount_text}"
            f"قم بإرسال المبلغ إلى المحفظة👝:\n\n<code>{context.bot_data[USDT]}</code>\n\n"
            "ثم قم بإرسال لقطة شاشة لإثبات عملية الدفع إلى الروبوت حتى نتمكن من توثيقها.\n\n"
            "<b>ملاحظة هامة: الشبكة المستخدمه هي TRC20</b>\n\n"
            f"{'-' * 20}\n\n"
            f"{exchange_amount_kur_text}"
            f"بڕە پارەکە بنێرە بۆ جزدانەکە👝:\n\n<code>{context.bot_data[USDT]}</code>\n\n"
            "پاشان وێنەی شاشەی بەڵگەی پرۆسەی پارەدان بنێرە بۆ بۆتەکە تا بتوانین بەڵگەی لەسەر بکەین.\n"
            "<b> تێبینی گرنگ: تۆڕی بەکارهێنراو TRC20 ە</b>"
        )

    else:
        text = (
            f"{exchange_amount_text}"
            f"ستقوم بتحويل المبلغ إلى الحساب التالي:\n\n<code>{context.bot_data[send_method]}</code>\n\n"
            "ثم قم بإرسال لقطة شاشة لإثبات عملية الدفع إلى الروبوت حتى نتمكن من توثيقها.\n\n"
            f"{'-' * 20}\n\n"
            f"{exchange_amount_kur_text}"
            f"بڕە پارەکە دەگوازیتەوە بۆ ئەو ئەکاونتەی خوارەوە:\n\n<code>{context.bot_data[send_method]}</code>\n\n"
            "پاشان وێنەی شاشەی بەڵگەی پرۆسەی پارەدان بنێرە بۆ بۆتەکە تا بتوانین بەڵگەی لەسەر بکەین.\n"
        )
    await update.message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(back_buttons),
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):

        res = await user_first_step(update=update)
        if not res:
            return

        await update.callback_query.answer()
        keyboard = build_first_method_keyboard()
        # keyboard = build_payment_methods_keyboard(op="buy")
        keyboard.append(back_button_user[0])
        text = f"""ماذا تريد أن تبيع؟

{'-' * 20}
                
دەتەوێت چی فرۆشیت؟"""
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_SEND_METHOD


async def choose_send_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        if "back to" not in update.callback_query.data:
            method = update.callback_query.data

            if not context.bot_data["activate_buy"]["first_method"][method]:
                await update.callback_query.answer(
                    "هذه الوسيلة متوقفة حالياً❗️",
                    show_alert=True,
                )
                return

            context.user_data["send_buy_method"] = method
        else:
            method = context.user_data["send_buy_method"]

        # keyboard = build_payment_methods_keyboard(op="buy", first=method)
        keyboard = build_second_method_keyboard()

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to choose send method",
                ),
            ]
        )
        keyboard.append(back_button_user[0])
        text = (
            f"ستقوم بدفع:\n{method}\nمقابل:\n\n"
            f"{'-' * 20}\n\n"
            f"پارە دەدەیت:\n{method}\nبەرامبەر:"
        )
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_TAKE_METHOD


back_to_choose_send_method = buy


async def choose_take_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        if "back to" not in update.callback_query.data:
            method = update.callback_query.data
            if not context.bot_data["activate_buy"]["second_method"][method]:
                await update.callback_query.answer(
                    "هذه الوسيلة متوقفة حالياً❗️",
                    show_alert=True,
                )
                return
            context.user_data["take_buy_method"] = method

        ar_curr = payment_methods_info[context.user_data["send_buy_method"]]["ar_curr"]
        kur_curr = payment_methods_info[context.user_data["send_buy_method"]][
            "kur_curr"
        ]

        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to choose take method",
                ),
            ],
            back_button_user[0],
        ]

        text = (
            f"أرسل المبلغ الذي تريد بيعه بال{ar_curr}\n\n"
            f"{'-' * 20}\n\n"
            f"ئەو بڕە پارەیەی دەتەوێت بیفرۆشیت بە {kur_curr} بنێرە"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return AMOUNT_TO_BUY


back_to_choose_take_method = choose_send_method


async def amount_to_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):

        if update.callback_query:
            await update.callback_query.answer()
            amount: float = context.user_data["amount_to_buy"]
        else:
            amount = float(update.message.text)
            context.user_data["amount_to_buy"] = amount

        send_method = context.user_data["send_buy_method"]
        take_method = context.user_data["take_buy_method"]

        if (
            payment_methods_info[send_method]["curr"] == "dinar"
            and not (5000001 > amount > 1499)
        ) or (
            payment_methods_info[send_method]["curr"] == "usd"
            and not (5001 > amount > 9)
        ):
            if payment_methods_info[send_method]["curr"] == "usd":
                text = (
                    "يرجى إدخال قيمة بين 10$  و 5000$ !\n\n"
                    f"{'-' * 20}\n\n"
                    "تکایە بەهایەک لە نێوان 10 بۆ 5000 دۆلار دابنێ!"
                )
            else:
                text = (
                    "الرجاء إدخال قيمة تتراوح بين 15000 دينار عراقي و5,000,000 دينار عراقي\n\n"
                    f"{'-' * 20}\n\n"
                    "تکایە بەهایەک لە نێوان 15,000 دیناری عێراقی بۆ 5,000,000 دیناری عێراقی دابنێ"
                )

            await update.message.reply_text(text=text)
            return

        buy_dict: dict = payment_methods_info[send_method]["buy"]
        comm: float = buy_dict[take_method] / 100 * amount

        new_amount: float = amount + comm

        ar_curr = payment_methods_info[take_method]["ar_curr"]
        kur_curr = payment_methods_info[take_method]["kur_curr"]

        if (
            payment_methods_info[send_method]["curr"]
            != payment_methods_info[take_method]["curr"]
        ):
            if payment_methods_info[send_method]["curr"] == "usd":
                new_amount *= context.bot_data["USD_TO_DINAR"]
            else:
                new_amount *= context.bot_data["DINAR_TO_USD"]

        context.user_data["exchange_amount"] = new_amount

        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to amount to buy",
                ),
            ],
            back_button_user[0],
        ]

        if send_method == "Cash - الدفع نقدي 💰":
            text = (
                f"ستتلقى المبلغ التالي: <code>{new_amount:,.4f}</code> {ar_curr}\n\n"
                f"عنوان مكتب <b>{send_method}</b>:\n<code>{context.bot_data[send_method]}</code>\n\n"
                f"{'-' * 20}\n\n"
                f"ئەم بڕە پارەیە وەردەگریت: <code>{new_amount:,.4f}</code> {ar_curr}\n\n"
                f"ناونیشانی ئۆفیسی <b>کاش - پارەدان بە کاش 💰</b>:\n<code>هەولێر - عەینکاوە - شەقامی ئەل مۆنتەزا\n009647511230235</code>"
            )

            await update.message.reply_text(
                text=text,
                reply_markup=build_user_keyboard(),
            )
            return ConversationHandler.END

        elif take_method == "Cash - الدفع نقدي 💰":
            await send_money_step(
                update=update,
                context=context,
                back_buttons=back_buttons,
                exchange_amount_text=(
                    "مكان الاستلام : أربيل - عينكاوة - شارع المنتزه + واتساب 009647511230235\n\n"
                    f"ستتلقى المبلغ التالي: <code>{new_amount:,.4f}</code> {ar_curr}\n\n"
                ),
                exchange_amount_kur_text=(
                    "مكان الاستلام : أربيل - عينكاوة - شارع المنتزه + واتساب 009647511230235\n\n"
                    f"ئەم بڕە پارەیە وەردەگریت: <code>{new_amount:,.4f}</code> {kur_curr}\n\n"
                ),
            )
            return SCREEN_SHOT

        if take_method in [
            USDT,
        ]:
            wallet_or_number = "أرسل عنوان محفظتك التي ستصل عليها الأموال"
            wallet_or_number_kur = "ناونیشانی جزدانەکەت بنێرە کە پارەکە دەگاتە ئەوێ"
        else:
            wallet_or_number = "أرسل رقم حسابك الذي ستصل عليه الأموال"
            wallet_or_number_kur = "ژمارەی ئەکاونتەکەت بنێرە کە لەسەری پارەکە وەردەگریت"

        text = (
            f"ستتلقى المبلغ التالي: <code>{new_amount:,.4f}</code> {ar_curr}\n\n"
            f"{wallet_or_number}.\n\n"
            f"{'-' * 20}\n\n"
            f"ئەم بڕە پارەیە وەردەگریت: <code>{new_amount:,.4f}</code> {ar_curr}\n\n"
            f"{wallet_or_number_kur}."
        )

        if not update.callback_query:
            await update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )

        return WALLET


back_to_amount_to_buy = choose_take_method


async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        wal = update.message.text
        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to wallet",
                ),
            ],
            back_button_user[0],
        ]
        if context.user_data["take_buy_method"] == K_CARD:
            context.user_data["buy_wallet"] = {"account": wal}
            await update.message.reply_text(
                text="أرسل رقم البطاقة:",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return K_CARD_BUY_WAL_NUM
        else:
            context.user_data["buy_wallet"] = wal

        await send_money_step(
            update=update,
            context=context,
            back_buttons=back_buttons,
        )

        return SCREEN_SHOT


async def k_card_buy_wal_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        context.user_data["buy_wallet"]["wallet"] = update.message.text
        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to k_card_buy_wal_num",
                ),
            ],
            back_button_user[0],
        ]
        await send_money_step(
            update=update,
            context=context,
            back_buttons=back_buttons,
        )
        return SCREEN_SHOT


async def back_to_k_card_buy_wal_num(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to wallet",
                ),
            ],
            back_button_user[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل رقم البطاقة:", reply_markup=InlineKeyboardMarkup(back_buttons)
        )
        return K_CARD_BUY_WAL_NUM


back_to_wallet = amount_to_buy


async def screen_shot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):

        photo = update.message.photo[-1]

        send_method = context.user_data["send_buy_method"]
        take_method = context.user_data["take_buy_method"]

        buy_dict: dict = payment_methods_info[send_method]["buy"]

        serial = await DB.add_buy_order(
            user_id=update.effective_user.id,
            buy_what=send_method,
            exchange_of=take_method,
            amount_to_buy=context.user_data["amount_to_buy"],
            exchange_amount=context.user_data["exchange_amount"],
            percentage=buy_dict[take_method],
            wallet=(
                context.user_data["buy_wallet"]
                if isinstance(context.user_data["buy_wallet"], str)
                else "{},{}".format(
                    context.user_data["buy_wallet"]["account"],
                    context.user_data["buy_wallet"]["wallet"],
                )
            ),
            amount_to_buy_curr=payment_methods_info[send_method]["curr"],
            exchange_curr=payment_methods_info[take_method]["curr"],
        )

        order = DB.get_order(serial=serial, op="buy")

        send_curr = payment_methods_info[send_method]["ar_curr"]
        take_curr = payment_methods_info[take_method]["ar_curr"]

        if take_method in [
            USDT,
        ]:
            wallet_or_number = "عنوان المحفظة"
        else:
            wallet_or_number = "رقم الحساب"

        text = (
            "طلب بيع:\n\n"
            f"رقم الطلب: <code>{serial}</code>\n"
            f"آيدي المستخدم: <code>{update.effective_user.id}</code>\n\n"
            f"بتاريخ:\n<b>{order['order_date']}</b>\n\n"
            f"بيع:\n<b>{send_method}</b>\n"
            f"مقابل:\n<b>{take_method}</b>\n\n"
            f"القيمة المدفوعة: <code>{context.user_data['amount_to_buy']}</code> {send_curr}\n"
            f"القيمة المطلوبة: <code>{context.user_data['exchange_amount']}</code> {take_curr}\n\n"
        )
        if take_method == K_CARD:
            text += (
                f"رقم الحساب: <code>{context.user_data['buy_wallet']['account']}</code>\n\n"
                f"رقم البطاقة: <code>{context.user_data['buy_wallet']['wallet']}</code>"
            )
        elif take_method != "Cash - الدفع نقدي 💰":
            text += (
                f"{wallet_or_number}: <code>{context.user_data['buy_wallet']}</code>"
            )

        dealer_keyboard = [
            [
                InlineKeyboardButton(
                    text="إكمال الطلب ✅",
                    callback_data=f"complete buy order {serial}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="رفض الطلب ❌",
                    callback_data=f"reject buy order {serial}",
                ),
            ],
        ]

        msg = await context.bot.send_photo(
            chat_id=int(os.getenv("DEALER_ID")),
            photo=photo,
            caption=text,
            reply_markup=(
                InlineKeyboardMarkup(dealer_keyboard)
                if take_method != "Cash - الدفع نقدي 💰"
                else None
            ),
        )

        await DB.add_message_id(
            serial=serial,
            message_id=msg.id,
            op="buy",
        )
        if take_method == "Cash - الدفع نقدي 💰":
            user_text = (
                "تم استلام طلبك✅\n\n"
                f"رقم الطلب: <code>{serial}</code>\n"
                f"قم بمراجعة المكتب في العنوان:\n<code>{context.bot_data[take_method]}</code>\n"
                "في مدة تتراوح ما بين 1 إلى 24 ساعة.\n\n"
                "<b>ملاحظة: في حال الرغبة بإلغاء التحويل بعد الدفع سيتم إرجاع الاموال في مدة تتراوح بين 1 ساعة إلى 72 ساعة مع خصم اجرة التحويل من المبلغ المدفوع.</b>\n\n"
                f"{'-' * 20}\n\n"
                "داواکاریەکەت وەرگیراوە✅\n\n"
                f"ژمارەی داواکاری: <code>{serial}</code>\n"
                f"سەردانی ئۆفیس بکەن لە:\n<code>هەولێر - عەینکاوە - شەقامی ئەل مۆنتەزا\n009647511230235</code>\n"
                "لە ماوەی نێوان ١ بۆ ٢٤ کاتژمێردا.\n\n"
                "<b>تێبینی: ئەگەر بتەوێت دوای پارەدان گواستنەوەکە هەڵبوەشێنیتەوە، ئەوا پارەکە لە ماوەی 1 کاتژمێر تا 72 کاتژمێر دەگەڕێتەوە، لەگەڵ بڕینی کرێی گواستنەوەکە لەو بڕە پارەیەی کە دراوە.</b>\n\n"
            )
        else:
            user_text = (
                "تم إرسال طلبك للتنفيذ✅\n\n"
                f"رقم الطلب: <code>{serial}</code>\n"
                f"سيتم تنفيذ الطلب في مدة تتراوح ما بين 1 إلى 24 ساعة.\n\n"
                "<b>ملاحظة 1: يرجى عدم استخدام زر طلب المساعدة أدناه قبل مرور 24 ساعة دون اكتمال الطلب.</b>\n\n"
                "<b>ملاحظة 2: في حال الرغبة بإلغاء التحويل بعد الدفع سيتم إرجاع الاموال في مدة تتراوح بين 1 ساعة إلى 72 ساعة مع خصم اجرة التحويل من المبلغ المدفوع.</b>\n\n"
                f"{'-' * 20}\n\n"
                "داواکاریەکەت نێردراوە بۆ پرۆسێسکردن ✅\n\n"
                f"ژمارەی داواکاری ئێستا: <code>{serial}</code>\n"
                f"داواکارییەکە لە ماوەی ١ بۆ ٢٤ کاتژمێردا جێبەجێ دەکرێت.\n\n"
                "<b>تێبینی یەکەم: تکایە پێش تێپەڕبوونی ٢٤ کاتژمێر بەبێ ئەوەی داواکارییەکە تەواو بێت، دوگمەی داوای یارمەتی لە خوارەوە بەکارمەهێنە.</b>\n\n"
                "<b>تێبینی دووەم: ئەگەر بتەوێت دوای پارەدان گواستنەوەکە هەڵبوەشێنیتەوە، لە ماوەی 1 بۆ 72 کاتژمێردا پارەکەت بۆ دەگەڕێتەوە، لەگەڵ بڕینی کرێی گواستنەوەکە لەو بڕە پارەیەی کە دراوە.</b>\n\n"
            )

        help_button = [
            [
                InlineKeyboardButton(
                    text="طلب مساعدة ❓",
                    url=os.getenv("OWNER_USERNAME"),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="كم مضى على الطلب🕑",
                    callback_data=f"time order {serial}",
                ),
            ],
        ]

        await update.message.reply_text(
            text=user_text,
            reply_markup=(
                InlineKeyboardMarkup(help_button)
                if take_method != "Cash - الدفع نقدي 💰"
                else None
            ),
        )

        await update.message.reply_text(
            text="القائمة الرئيسية🔝",
            reply_markup=build_user_keyboard(),
        )
        return ConversationHandler.END


async def time_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        await update.callback_query.answer()
        serial = int(update.callback_query.data.split(" ")[-1])
        order = DB.get_order(serial=serial, op="buy")

        order_date = datetime.datetime.fromisoformat(order["order_date"])
        now = datetime.datetime.now()

        diff = now - order_date
        seconds = diff.total_seconds()

        hours = seconds // 3600
        left_minutes = (seconds % 3600) // 60
        left_seconds = seconds - (hours * 3600) - (left_minutes * 60)

        hours_text = f"{hours} ساعة " if hours else ""
        minutes_text = f"{int(left_minutes)} دقيقة " if left_minutes else ""
        seconds_text = f"{int(left_seconds)} ثانية " if left_seconds else ""

        await update.callback_query.answer(
            hours_text + minutes_text + seconds_text,
            show_alert=True,
        )


time_order_handler = CallbackQueryHandler(time_order, "^time order \d+$")

buy_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(buy, "^buy$"),
    ],
    states={
        CHOOSE_SEND_METHOD: [
            CallbackQueryHandler(choose_send_method, payment_methods_pattern),
        ],
        CHOOSE_TAKE_METHOD: [
            CallbackQueryHandler(choose_take_method, payment_methods_pattern)
        ],
        AMOUNT_TO_BUY: [
            MessageHandler(filters=filters.Regex("^\d+\.?\d*$"), callback=amount_to_buy)
        ],
        WALLET: [
            MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=wallet)
        ],
        K_CARD_BUY_WAL_NUM: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND, callback=k_card_buy_wal_num
            )
        ],
        SCREEN_SHOT: [MessageHandler(filters=filters.PHOTO, callback=screen_shot)],
    },
    fallbacks=[
        start_command,
        back_to_user_home_page_handler,
        CallbackQueryHandler(
            back_to_choose_send_method, "^back to choose send method$"
        ),
        CallbackQueryHandler(
            back_to_choose_take_method, "^back to choose take method$"
        ),
        CallbackQueryHandler(
            back_to_k_card_buy_wal_num, "^back to k_card_buy_wal_num$"
        ),
        CallbackQueryHandler(back_to_amount_to_buy, "^back to amount to buy$"),
        CallbackQueryHandler(back_to_wallet, "^back to wallet$"),
    ],
    name="buy_handler",
    persistent=True,
)
