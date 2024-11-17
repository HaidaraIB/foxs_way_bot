from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
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
from start import start_command
from constants import *
from DB import DB
import os
import datetime

(
    CHOOSE_TAKE_SELL_METHOD,
    CHOOSE_SEND_SELL_METHOD,
    AMOUNT_TO_SELL,
    SELL_WALLET,
    SELL_SCREEN_SHOT,
) = range(5)


async def send_money_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    back_buttons: list[list[InlineKeyboardButton]],
    exchange_amount_text: str = "",
    exchange_amount_kur_text: str = "",
):
    send_method = context.user_data["send_sell_method"]
    if send_method == USDT:
        text = (
            f"{exchange_amount_text}"
            f"قم بإرسال المبلغ إلى المحفظة👝:\n\n<code>{context.bot_data[USDT]}</code>\n\n"
            "ثم أرسل لقطة شاشة لعملية الدفع إلى البوت لنقوم بتوثيقها.\n\n"
            "<b>ملاحظة هامة: الشبكة المستخدمه هي TRC20</b>\n\n"
            f"{'-' * 20}\n\n"
            f"{exchange_amount_kur_text}"
            f"بڕە پارەکە بنێرە بۆ جزدانەکە👝:\n\n<code>{context.bot_data[USDT]}</code>\n\n"
            "پاشان وێنەی شاشەی بەڵگەی پارەدانەکەت بنێرە بۆ بۆتەکە تا بتوانین ڕەسەنایەتییەکەی بسەلمێنین.\n\n"
            "<b> تێبینی گرنگ: تۆڕی بەکارهێنراو TRC20 ە</b>\n\n"
        )
    elif send_method == K_CARD:
        text = (
            f"{exchange_amount_text}"
            f"قم بتحويل المبلغ إلى الحساب التالي:\n\n"
            f"رقم الحساب: <code>{context.bot_data[K_CARD]['account']}</code>\n\n"
            f"رقم البطاقة: <code>{context.bot_data[K_CARD]['card']}</code>\n\n"
            "ثم أرسل لقطة شاشة لعملية الدفع إلى البوت لنقوم بتوثيقها.\n\n"
            "<b>ملاحظة هامة: الشبكة المستخدمه هي TRC20</b>\n\n"
            f"{'-' * 20}\n\n"
            f"{exchange_amount_kur_text}"
            f"بڕە پارەکە دەگوازیتەوە بۆ ئەو ئەکاونتەی خوارەوە:\n\n<code>{context.bot_data[K_CARD]['account']}</code>\n\n"
            f"ژمارەی هەژمار: <code>{context.bot_data[K_CARD]['account']}</code>\n\n"
            f"ژمارەی کارتەکە: <code>{context.bot_data[K_CARD]['card']}</code>\n\n"
            "پاشان وێنەی شاشەی بەڵگەی پارەدانەکەت بنێرە بۆ بۆتەکە تا بتوانین ڕەسەنایەتییەکەی بسەلمێنین.\n\n"
            "<b> تێبینی گرنگ: تۆڕی بەکارهێنراو TRC20 ە</b>\n\n"
        )
    else:
        text = (
            f"{exchange_amount_text}"
            f"قم بتحويل المبلغ إلى الحساب التالي:\n\n<code>{context.bot_data[send_method]}</code>\n\n"
            "ثم أرسل لقطة شاشة لعملية الدفع إلى البوت لنقوم بتوثيقها.\n\n"
            f"{'-' * 20}\n\n"
            f"{exchange_amount_kur_text}"
            f"بڕە پارەکە دەگوازیتەوە بۆ ئەو ئەکاونتەی خوارەوە:\n\n<code>{context.bot_data[send_method]}</code>\n\n"
            "پاشان وێنەی شاشەی بەڵگەی پارەدانەکەت بنێرە بۆ بۆتەکە تا بتوانین ڕەسەنایەتییەکەی بسەلمێنین."
        )
    await update.message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(back_buttons),
    )


async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:

        res = await user_first_step(update=update)
        if not res:
            return

        await update.callback_query.answer()

        # keyboard = build_payment_methods_keyboard(op="sell")
        keyboard = build_first_method_keyboard()

        keyboard.append(back_button_user[0])

        text = f"ما الذي تريد شراءه؟\n\n" f"{'-' * 20}\n\n" "ئەتەوێت چی بکڕی؟"

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_TAKE_SELL_METHOD


async def choose_take_sell_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        if "back to" not in update.callback_query.data:
            method = update.callback_query.data
            if not context.bot_data["activate_sell"]["first_method"][method]:
                await update.callback_query.answer(
                    "هذه الوسيلة متوقفة حالياً❗️",
                    show_alert=True,
                )
                return
            context.user_data["take_sell_method"] = method
        else:
            method = context.user_data["take_sell_method"]

        # keyboard = build_payment_methods_keyboard(op="sell", first=method)
        keyboard = build_second_method_keyboard()

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to choose take sell method",
                ),
            ]
        )
        keyboard.append(back_button_user[0])
        text = (
            f"ستقوم بشراء:\n{method}\nمقابل:\n\n"
            f"{'-' * 20}\n\n"
            f"دەیکڕیت:\n{method}\nبەرامبەر:"
        )
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_SEND_SELL_METHOD


back_to_choose_take_sell_method = sell


async def choose_send_sell_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        if "back to" not in update.callback_query.data:
            method = update.callback_query.data
            if not context.bot_data["activate_sell"]["second_method"][method]:
                await update.callback_query.answer(
                    "هذه الوسيلة متوقفة حالياً❗️",
                    show_alert=True,
                )
                return
            context.user_data["send_sell_method"] = method

        ar_curr = payment_methods_info[context.user_data["take_sell_method"]]["ar_curr"]
        kur_curr = payment_methods_info[context.user_data["take_sell_method"]][
            "kur_curr"
        ]

        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to choose send sell method",
                ),
            ],
            back_button_user[0],
        ]
        text = (
            f"أرسل المبلغ الذي تريد شراءه بال{ar_curr}\n\n"
            f"{'-' * 20}\n\n"
            f"ئەو بڕە بنووسە کە دەتەوێت بیکریت{kur_curr} بنێرە"
        )
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return AMOUNT_TO_SELL


back_to_choose_send_sell_method = choose_take_sell_method


async def amount_to_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:

        if update.callback_query:
            await update.callback_query.answer()
            amount = context.user_data["amount_to_sell"]
        else:
            amount = float(update.message.text)
            context.user_data["amount_to_sell"] = amount

        send_method = context.user_data["send_sell_method"]
        take_method = context.user_data["take_sell_method"]

        if (
            payment_methods_info[take_method]["curr"] == "dinar"
            and not (5000001 > amount > 1499)
        ) or (
            payment_methods_info[take_method]["curr"] == "usd"
            and not (5001 > amount > 9)
        ):
            if payment_methods_info[take_method]["curr"] == "usd":
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

        sell_dict: dict = payment_methods_info[take_method]["sell"]
        comm = sell_dict[send_method] / 100 * amount

        if take_method == USDT:
            if 46 > amount > 9:
                new_amount = amount + 2
            elif 101 > amount > 45:
                new_amount = amount + 3
            else:
                new_amount = amount + comm + 1
        else:
            new_amount = amount + comm

        ar_curr = payment_methods_info[send_method]["ar_curr"]
        kur_curr = payment_methods_info[send_method]["kur_curr"]

        if (
            payment_methods_info[take_method]["curr"]
            != payment_methods_info[send_method]["curr"]
        ):
            if payment_methods_info[take_method]["curr"] == "usd":
                new_amount *= context.bot_data["USD_TO_DINAR"]
            else:
                new_amount *= context.bot_data["DINAR_TO_USD"]

        context.user_data["exchange_sell_amount"] = new_amount

        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to amount to sell",
                ),
            ],
            back_button_user[0],
        ]

        if take_method == "Cash - الدفع نقدي 💰":
            text = (
                f"ستدفع المبلغ التالي: <code>{new_amount:.4f}</code> {ar_curr}\n\n"
                f"عنوان مكتب <b>{take_method}</b>:\n<code>{context.bot_data[take_method]}</code>\n\n"
                f"{'-' * 20}\n\n"
                f"ئەم بڕە پارەیە دەدەیت: <code>{new_amount:.4f}</code> {ar_curr}\n\n"
                f"ناونیشانی ئۆفیسی <b>کاش - پارەدان بە کاش 💰</b>:\n<code>هەولێر - عەینکاوە - شەقامی ئەل مۆنتەزا\n009647511230235</code>"
            )

            await update.message.reply_text(
                text=text,
                reply_markup=build_user_keyboard(),
            )
            return ConversationHandler.END

        elif send_method == "Cash - الدفع نقدي 💰":
            await send_money_step(
                update=update,
                context=context,
                back_buttons=back_buttons,
                exchange_amount_text=f"ستدفع هذا المبلغ: <code>{new_amount:,.4f}</code> {ar_curr}\n\n",
                exchange_amount_kur_text=f"ئەم بڕە پارەیە دەدەیت: <code>{new_amount:,.4f}</code> {kur_curr}\n\n",
            )
            return SELL_SCREEN_SHOT

        if take_method in [
            USDT,
        ]:
            wallet_or_number = "أرسل عنوان محفظتك التي ستصل عليها الأموال"
            wallet_or_number_kur = "ناونیشانی جزدانەکەت بنێرە کە پارەکە دەگاتە ئەوێ"
        else:
            wallet_or_number = "أرسل رقم حسابك الذي ستصل عليه الأموال"
            wallet_or_number_kur = "ژمارەی ئەکاونتەکەت بنێرە کە لەسەری پارەکە وەردەگریت"

        text = (
            f"ستقوم بدفع المبلغ التالي: <code>{new_amount:,.4f}</code> {ar_curr}\n\n"
            f"{wallet_or_number}.\n\n"
            f"{'-' * 20}\n\n"
            f"ئەم بڕە پارەیە دەدەیت: <code>{new_amount:,.4f}</code> {kur_curr}\n\n"
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

        return SELL_WALLET


back_to_amount_to_sell = choose_send_sell_method


async def sell_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        context.user_data["sell_wallet"] = update.message.text
        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙",
                    callback_data="back to sell wallet",
                ),
            ],
            back_button_user[0],
        ]

        await send_money_step(
            update=update,
            context=context,
            back_buttons=back_buttons,
        )

        return SELL_SCREEN_SHOT


back_to_sell_wallet = amount_to_sell


async def sell_screen_shot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:

        photo = update.message.photo[-1]

        send_method = context.user_data["send_sell_method"]
        take_method = context.user_data["take_sell_method"]

        sell_dict: dict = payment_methods_info[take_method]["sell"]

        serial = await DB.add_sell_order(
            user_id=update.effective_user.id,
            sell_what=take_method,
            exchange_of=send_method,
            amount_to_sell=context.user_data["amount_to_sell"],
            exchange_amount=context.user_data["exchange_sell_amount"],
            percentage=sell_dict[send_method],
            wallet=context.user_data.get("sell_wallet", ""),
            amount_to_sell_curr=payment_methods_info[take_method]["curr"],
            exchange_curr=payment_methods_info[send_method]["curr"],
        )

        order = DB.get_order(serial=serial, op="sell")

        take_curr = payment_methods_info[take_method]["ar_curr"]
        send_curr = payment_methods_info[send_method]["ar_curr"]

        if send_method in [
            USDT,
        ]:
            wallet_or_number = "عنوان المحفظة"
        else:
            wallet_or_number = "رقم الحساب"

        text = (
            "طلب شراء:\n\n"
            f"رقم الطلب: <code>{serial}</code>\n"
            f"آيدي المستخدم: <code>{update.effective_user.id}</code>\n\n"
            f"بتاريخ:\n<b>{order['order_date']}</b>\n\n"
            f"شراء:\n<b>{take_method}</b>\n"
            f"مقابل:\n<b>{send_method}</b>\n\n"
            f"القيمة المطلوبة: <code>{context.user_data['amount_to_sell']}</code> {take_curr}\n"
            f"القيمة المدفوعة: <code>{context.user_data['exchange_sell_amount']}</code> {send_curr}\n\n"
        )

        text += (
            f"{wallet_or_number}: <code>{context.user_data['sell_wallet']}</code>"
            if take_method != "Cash - الدفع نقدي 💰"
            else ""
        )

        dealer_keyboard = [
            [
                InlineKeyboardButton(
                    text="إكمال الطلب ✅",
                    callback_data=f"complete sell order {serial}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="رفض الطلب ❌",
                    callback_data=f"reject sell order {serial}",
                ),
            ],
        ]

        msg = await context.bot.send_photo(
            chat_id=int(os.getenv("DEALER_ID")),
            photo=photo,
            caption=text,
            reply_markup=(
                InlineKeyboardMarkup(dealer_keyboard)
                if send_method != "Cash - الدفع نقدي 💰"
                else None
            ),
        )

        await DB.add_message_id(
            serial=serial,
            message_id=msg.id,
            op="sell",
        )
        if send_method == "Cash - الدفع نقدي 💰":
            user_text = (
                "تم استلام طلبك✅\n\n"
                f"رقم الطلب: <code>{serial}</code>\n"
                f"قم بمراجعة المكتب في العنوان:\n<code>{context.bot_data[send_method]}</code>\n"
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
                    callback_data=f"time sell order {serial}",
                ),
            ],
        ]

        await update.message.reply_text(
            text=user_text,
            reply_markup=(
                InlineKeyboardMarkup(help_button)
                if send_method != "Cash - الدفع نقدي 💰"
                else None
            ),
        )

        await update.message.reply_text(
            text="القائمة الرئيسية🔝",
            reply_markup=build_user_keyboard(),
        )
        return ConversationHandler.END


async def time_sell_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        await update.callback_query.answer()
        serial = int(update.callback_query.data.split(" ")[-1])
        order = DB.get_order(serial=serial, op="sell")

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


time_sell_order_handler = CallbackQueryHandler(time_sell_order, "^time sell order \d+$")

sell_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(sell, "^sell$"),
    ],
    states={
        CHOOSE_TAKE_SELL_METHOD: [
            CallbackQueryHandler(choose_take_sell_method, payment_methods_pattern),
        ],
        CHOOSE_SEND_SELL_METHOD: [
            CallbackQueryHandler(choose_send_sell_method, payment_methods_pattern)
        ],
        AMOUNT_TO_SELL: [
            MessageHandler(
                filters=filters.Regex("^\d+\.?\d*$"), callback=amount_to_sell
            )
        ],
        SELL_WALLET: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND, callback=sell_wallet
            )
        ],
        SELL_SCREEN_SHOT: [
            MessageHandler(filters=filters.PHOTO, callback=sell_screen_shot)
        ],
    },
    fallbacks=[
        start_command,
        back_to_user_home_page_handler,
        CallbackQueryHandler(
            back_to_choose_take_sell_method, "^back to choose take sell method$"
        ),
        CallbackQueryHandler(
            back_to_choose_send_sell_method, "^back to choose send sell method$"
        ),
        CallbackQueryHandler(back_to_amount_to_sell, "^back to amount to sell$"),
        CallbackQueryHandler(back_to_sell_wallet, "^back to sell wallet$"),
    ],
    name="sell_handler",
    persistent=True,
)
