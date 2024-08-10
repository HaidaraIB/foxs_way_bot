from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)
filterwarnings(
    action="ignore", message=r".*the `days` parameter.*", category=PTBUserWarning
)
filterwarnings(
    action="ignore", message=r".*invalid escape sequence.*", category=SyntaxWarning
)

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

from dotenv import load_dotenv
load_dotenv()

from handlers import main
import os


if __name__ == "__main__":
    # if int(os.getenv("OWNER_ID")) != 755501092:
    #     logging.getLogger("httpx").setLevel(logging.WARNING)
    main()
