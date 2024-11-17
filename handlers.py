from telegram import Update
from telegram.ext import Application, PicklePersistence, Defaults
from telegram.constants import ParseMode
from start import start_command, admin_command, inits
from common import (
    back_to_user_home_page_handler,
    back_to_admin_home_page_handler,
    error_handler,
)

from admin.admin_settings import *
from admin.broadcast import *
from admin.admin_calls import *
from admin.change_exchange_rates import *
from admin.wallet_settings import *
from admin.activate_methods import *

from dealer.handle_buy import *
from dealer.handle_sell import *

from user.buy import *
from user.sell import *

import sys
import os
from DB import DB


def main():
    DB.creat_tables()
    defaults = Defaults(parse_mode=ParseMode.HTML)
    my_persistence = PicklePersistence(filepath="data/persistence", single_file=False)
    app = (
        Application.builder()
        .token(os.getenv("BOT_TOKEN"))
        .post_init(inits)
        .arbitrary_callback_data(True)
        .persistence(persistence=my_persistence)
        .defaults(defaults)
        .concurrent_updates(True)
        .build()
    )
    # BUY
    app.add_handler(buy_handler)
    app.add_handler(time_order_handler)

    # HANDLE BUY
    app.add_handler(complete_buy_handler)
    app.add_handler(reject_buy_handler)

    # SELL
    app.add_handler(sell_handler)
    app.add_handler(time_sell_order_handler)

    # HANDLE SELL
    app.add_handler(complete_sell_handler)
    app.add_handler(reject_sell_handler)

    app.add_handler(change_rates_handler)
    app.add_handler(wallets_settings_handler)

    # ADMIN SETTINGS
    app.add_handler(admin_settings_handler)
    app.add_handler(show_admins_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)

    app.add_handler(ban_unban_user_handler)

    app.add_handler(broadcast_message_handler)

    app.add_handler(hide_ids_keyboard_handler)
    app.add_handler(activate_methods_handler)
    app.add_handler(find_id_handler)

    app.add_handler(refresh_handler)
    app.add_handler(restart_handler)
    app.add_handler(stop_handler)

    app.add_handler(start_command)
    app.add_handler(admin_command)
    app.add_handler(back_to_user_home_page_handler)
    app.add_handler(back_to_admin_home_page_handler)

    app.add_error_handler(error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

    if app.bot_data["restart"]:
        os.execl(sys.executable, sys.executable, *sys.argv)
