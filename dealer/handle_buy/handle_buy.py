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

from DB import DB

import os

BUY_PROOF, REJECT_BUY_REASON = range(2)


async def complete_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        await update.callback_query.answer(
            "قم بإرسال صورة لإثبات الدفع، يمكنك إرسال ملاحظات مرفقة مع الصورة إن أردت.",
            show_alert=True,
        )
        context.user_data["buy_order_serial"] = int(
            update.callback_query.data.split(" ")[-1]
        )
        back_button = [
            [
                InlineKeyboardButton(
                    text="الرجوع عن إكمال الطلب🔙",
                    callback_data="back from complete buy",
                ),
            ],
        ]
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(back_button),
        )
        return BUY_PROOF


async def buy_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        order = DB.get_order(
            serial=context.user_data["buy_order_serial"],
            op="buy",
        )
        caption = (
            "طلب بيع مكتمل ✅\n\n"
            f"رقم الطلب: <code>{order['serial']}</code>\n\n"
            f"ملاحظات: {update.message.caption_html if update.message.caption_html else 'لا يوجد'}"
        )

        await context.bot.send_photo(
            chat_id=order["user_id"],
            photo=update.message.photo[-1],
            caption=caption,
        )

        await context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=order["message_id"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="طلب مكتمل ✅",
                            callback_data="طلب مكتمل ✅",
                        ),
                    ],
                ]
            ),
        )
        await DB.update_state(serial=order['serial'], op='buy', state='completed')

        await update.message.reply_text(text="طلب مكتمل ✅")

        return ConversationHandler.END


async def reject_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        await update.callback_query.answer(
            "قم بإرسال سبب الرفض، يمكنك إرسال صورة مرفقة بتعليق أو تعليق فقط.",
            show_alert=True,
        )
        context.user_data["buy_order_serial"] = int(
            update.callback_query.data.split(" ")[-1]
        )
        back_button = [
            [
                InlineKeyboardButton(
                    text="الرجوع عن رفض الطلب🔙",
                    callback_data="back from reject buy",
                ),
            ],
        ]
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(back_button),
        )
        return REJECT_BUY_REASON


async def reject_buy_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        order = DB.get_order(
            serial=context.user_data["buy_order_serial"],
            op="buy",
        )
        reject_text = (
            "طلب بيع مرفوض ❌\n\n" f"رقم الطلب: <code>{order['serial']}</code>\n\n"
        )
        reason_text = update.message.caption_html if update.message.caption_html else "مرفق في الصورة"

        if update.message.photo:
            caption = reject_text + f"السبب: {reason_text}"
            await context.bot.send_photo(
                chat_id=order["user_id"],
                photo=update.message.photo[-1],
                caption=caption,
            )
        else:
            text = reject_text + f"السبب: {update.message.text_html}"
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=text,
            )

        await context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=order["message_id"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="طلب مرفوض ❌",
                            callback_data="طلب مرفوض ❌",
                        ),
                    ],
                ]
            ),
        )
        await update.message.reply_text(text="طلب مرفوض ❌")

        await DB.update_state(serial=order['serial'], op='buy', state='rejected')

        return ConversationHandler.END


async def back_to_handle_buy_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        serial = context.user_data["buy_order_serial"]
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
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(dealer_keyboard),
        )
        return ConversationHandler.END


complete_buy_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(complete_buy, "^complete buy order \d+$")],
    states={
        BUY_PROOF: [
            MessageHandler(
                filters=filters.PHOTO | filters.CAPTION,
                callback=buy_proof,
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(back_to_handle_buy_order, "^back from complete buy$")
    ],
)

reject_buy_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(reject_buy, "^reject buy order \d+$")],
    states={
        REJECT_BUY_REASON: [
            MessageHandler(
                filters=filters.PHOTO
                | filters.CAPTION
                | (filters.TEXT & ~filters.COMMAND),
                callback=reject_buy_reason,
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(back_to_handle_buy_order, "^back from reject buy$")
    ],
)
