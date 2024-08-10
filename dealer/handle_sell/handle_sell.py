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

SELL_PROOF, REJECT_SELL_REASON = range(2)


async def complete_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        await update.callback_query.answer(
            "قم بإرسال صورة لإثبات الدفع، يمكنك إرسال ملاحظات مرفقة مع الصورة إن أردت.",
            show_alert=True,
        )
        context.user_data["sell_order_serial"] = int(
            update.callback_query.data.split(" ")[-1]
        )
        back_button = [
            [
                InlineKeyboardButton(
                    text="الرجوع عن إكمال الطلب🔙",
                    callback_data="back from complete sell",
                ),
            ],
        ]
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(back_button),
        )
        return SELL_PROOF


async def SELL_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        order = DB.get_order(
            serial=context.user_data["sell_order_serial"],
            op="sell",
        )
        caption = (
            "طلب شراء مكتمل ✅\n\n"
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

        await update.message.reply_text(text="طلب مكتمل ✅")

        await DB.update_state(serial=order['serial'], op='sell', state='completed')

        return ConversationHandler.END


async def reject_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        await update.callback_query.answer(
            "قم بإرسال سبب الرفض، يمكنك إرسال صورة مرفقة بتعليق أو تعليق فقط.",
            show_alert=True,
        )
        context.user_data["sell_order_serial"] = int(
            update.callback_query.data.split(" ")[-1]
        )
        back_button = [
            [
                InlineKeyboardButton(
                    text="الرجوع عن رفض الطلب🔙",
                    callback_data="back from reject sell",
                ),
            ],
        ]
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(back_button),
        )
        return REJECT_SELL_REASON


async def reject_SELL_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        order = DB.get_order(
            serial=context.user_data["sell_order_serial"],
            op="sell",
        )
        reject_text = (
            "طلب شراء مرفوض ❌\n\n" f"رقم الطلب: <code>{order['serial']}</code>\n\n"
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

        await DB.update_state(serial=order['serial'], op='sell', state='rejected')

        return ConversationHandler.END


async def back_to_handle_sell_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and update.effective_user.id == int(
        os.getenv("DEALER_ID")
    ):
        serial = context.user_data["sell_order_serial"]
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
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(dealer_keyboard),
        )
        return ConversationHandler.END


complete_sell_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(complete_sell, "^complete sell order \d+$")],
    states={
        SELL_PROOF: [
            MessageHandler(
                filters=filters.PHOTO | filters.CAPTION,
                callback=SELL_proof,
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(back_to_handle_sell_order, "^back from complete sell$")
    ],
)

reject_sell_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(reject_sell, "^reject sell order \d+$")],
    states={
        REJECT_SELL_REASON: [
            MessageHandler(
                filters=filters.PHOTO
                | filters.CAPTION
                | (filters.TEXT & ~filters.COMMAND),
                callback=reject_SELL_reason,
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(back_to_handle_sell_order, "^back from reject sell$")
    ],
)
