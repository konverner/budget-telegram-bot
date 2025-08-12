import logging

import telebot
from dotenv import find_dotenv, load_dotenv
from telebot.states.sync.middleware import StateMiddleware

from .auth.data import init_roles_table, init_superuser
from .budget.handlers import register_handlers as budget_handlers
from .config import settings
from .database.core import SessionLocal, create_tables, drop_tables
from .language.handler import register_handlers as language_handlers
from .middleware.antiflood import AntifloodMiddleware
from .middleware.database import DatabaseMiddleware
from .middleware.user import UserCallbackMiddleware, UserMessageMiddleware

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Load and get environment variables
load_dotenv(find_dotenv(usecwd=True))


def start_bot():
    """Start the Telegram bot with configuration, middlewares, and handlers."""

    if not settings.BOT_TOKEN:
        logging.critical("BOT_TOKEN is not set in environment variables")
        raise ValueError("BOT_TOKEN environment variable is required")

    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.PROJECT_VERSION} with {settings.COMMUNICATION_STRATEGY} strategy")

    try:
        bot = telebot.TeleBot(settings.BOT_TOKEN, use_class_middlewares=True)
        _setup_middlewares(bot)

        _register_core_handlers(bot)

        bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

        bot_info = bot.get_me()
        logger.info(
            f"Bot {bot_info.username} (ID: {bot_info.id}) initialized successfully"
        )

        if settings.COMMUNICATION_STRATEGY == "polling":
            _start_polling_loop(bot)
        elif settings.COMMUNICATION_STRATEGY == "webhook":
            _set_webhook(bot)
        else:
            logging.critical(f"Unsupported communication strategy: {settings.COMMUNICATION_STRATEGY}")
            raise ValueError(f"Unsupported communication strategy: {settings.COMMUNICATION_STRATEGY}")

    except Exception as e:
        logging.critical(f"Failed to start bot: {str(e)}")
        raise


def _setup_middlewares(bot):
    """Configure bot middlewares."""
    if settings.ANTIFLOOD_ENABLED:
        logger.info(
            f"Enabling antiflood (window: {settings.ANTIFLOOD_RATE_LIMIT}s)"
        )
        bot.setup_middleware(
            AntifloodMiddleware(bot, settings.ANTIFLOOD_RATE_LIMIT)
        )

    bot.setup_middleware(StateMiddleware(bot))
    bot.setup_middleware(DatabaseMiddleware(bot))
    bot.setup_middleware(UserMessageMiddleware(bot))
    bot.setup_middleware(UserCallbackMiddleware(bot))


def _register_core_handlers(bot):
    """Register all bot handlers."""
    handlers = [
        language_handlers,
        budget_handlers
    ]
    for handler in handlers:
        handler(bot)


def _start_polling_loop(bot):
    """Start the main bot polling loop with error handling."""
    logger.info("Starting bot polling...")
    bot.polling(none_stop=True, interval=0, timeout=60, long_polling_timeout=60)


def _set_webhook(bot):
    """
    Set the webhook

    If webhook URL is set in environment variables, use it.
    Otherwise, use the HOST public ip and SSL certificate for the webhook.
    """
    if not settings.WEBHOOK_URL:
        logger.info(f"Setting bot webhook with host {settings.HOST} and port {settings.PORT}...")
        bot.run_webhooks(
            listen=settings.HOST,
            port=settings.PORT,
            certificate=settings.WEBHOOK_SSL_CERT,
            certificate_key=settings.WEBHOOK_SSL_PRIVKEY
        )
    else:
        logger.info(f"Setting bot webhook {settings.WEBHOOK_URL}...")
        bot.run_webhooks(webhook_url=settings.WEBHOOK_URL)


def init_db():
    """Initialize the database for applications."""
    # Create tables
    create_tables()

    # Create a new database session directly using SessionLocal
    db_session = SessionLocal()

    init_roles_table(db_session)

    # Add admin to user table
    if settings.SUPERUSER_USER_ID:
        init_superuser(db_session, settings.SUPERUSER_USER_ID, settings.SUPERUSER_USERNAME)
        logger.info(f"Superuser {settings.SUPERUSER_USERNAME} added successfully.")

    db_session.close()

    logger.info("Database initialized")


if __name__ == "__main__":
    drop_tables()
    init_db()
    start_bot()
