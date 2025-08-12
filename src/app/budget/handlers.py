import logging
from pathlib import Path

from omegaconf import OmegaConf
from telebot import TeleBot, types
from telebot.states import State, StatesGroup
from telebot.states.sync.context import StateContext

from .markup import create_cancel_button, create_category_markup, create_skip_button, create_subcategory_markup
from .service import budget_service

# Set logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load configuration
CURRENT_DIR = Path(__file__).parent
config = OmegaConf.load(CURRENT_DIR / "config.yaml")
strings = config.strings


class TransactionState(StatesGroup):
    """Transaction entry states"""

    category = State()
    subcategory = State()
    amount = State()
    comment = State()


def register_handlers(bot: TeleBot):
    """Register resource handlers"""
    logger.info("Registering resource handlers")

    @bot.message_handler(commands=['add_transaction'])
    def start_transaction(message: types.Message, data: dict):
        user = data["user"]
        state = StateContext(message, bot)
        state.set(TransactionState.category)

        try:
            categories = budget_service.get_categories()
            if not categories:
                bot.send_message(
                    message.chat.id,
                    strings[user.lang].no_categories,
                )
                return

            markup = create_category_markup(categories, user.lang)
            bot.send_message(
                message.chat.id,
                strings[user.lang].select_category,
                reply_markup=markup,
            )
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            bot.send_message(
                message.chat.id,
                strings[user.lang].transaction_error
            )

    @bot.callback_query_handler(state=TransactionState.category, func=lambda call: call.data.startswith("cat_"))
    def get_category(call: types.CallbackQuery, data: dict):
        user = data["user"]
        state = StateContext(call, bot)
        category_id = int(call.data.split("_")[1])

        state.add_data(category_id=category_id)

        try:
            subcategories = budget_service.get_subcategories(category_id)
            if subcategories:
                state.set(TransactionState.subcategory)
                markup = create_subcategory_markup(subcategories, user.lang)
                bot.edit_message_text(
                    strings[user.lang].select_subcategory,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                )
            else:
                state.set(TransactionState.amount)
                state.add_data(subcategory_id=None)
                bot.edit_message_text(
                    strings[user.lang].enter_amount,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=create_cancel_button(user.lang),
                )
        except Exception as e:
            logger.error(f"Error getting subcategories for category {category_id}: {e}")
            bot.edit_message_text(
                strings[user.lang].transaction_error,
                call.message.chat.id,
                call.message.message_id
            )

    @bot.callback_query_handler(state=TransactionState.subcategory, func=lambda call: call.data.startswith("subcat_"))
    def get_subcategory(call: types.CallbackQuery, data: dict):
        user = data["user"]
        state = StateContext(call, bot)
        subcategory_id = int(call.data.split("_")[1])

        state.add_data(subcategory_id=subcategory_id)
        state.set(TransactionState.amount)

        bot.edit_message_text(
            strings[user.lang].enter_amount,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=create_cancel_button(user.lang),
        )

    @bot.message_handler(state=TransactionState.amount)
    def get_amount(message: types.Message, data: dict):
        user = data["user"]
        state = StateContext(message, bot)

        try:
            amount = float(message.text.replace(",", "."))
            state.add_data(amount=amount)
            state.set(TransactionState.comment)

            bot.send_message(
                message.chat.id,
                strings[user.lang].enter_comment,
                reply_markup=create_skip_button(user.lang),
            )
        except ValueError:
            bot.send_message(
                message.chat.id,
                strings[user.lang].invalid_amount,
                reply_markup=create_cancel_button(user.lang),
            )

    @bot.message_handler(state=TransactionState.comment)
    def get_comment(message: types.Message, data: dict):
        user = data["user"]
        state = StateContext(message, bot)
        comment = message.text if message.text else ""

        # Get all collected data
        with state.data() as transaction_data:
            transaction_data['comment'] = comment

            # Save transaction using the budget service
            try:
                budget_service.save_transaction(str(user.id), transaction_data)
                bot.send_message(
                    message.chat.id,
                    strings[user.lang].transaction_saved,
                )
                logger.info(f"Transaction saved successfully for user {user.id}")
            except Exception as e:
                logger.error(f"Error saving transaction for user {user.id}: {e}")
                bot.send_message(
                    message.chat.id,
                    strings[user.lang].transaction_error,
                )
        state.delete()

    # Handle skip comment
    @bot.callback_query_handler(func=lambda call: call.data == "skip_comment")
    def skip_comment(call: types.CallbackQuery, data: dict):
        user = data["user"]
        state = StateContext(call, bot)
        comment = ""

        # Get all collected data
        with state.data() as transaction_data:
            transaction_data['comment'] = comment

            # Save transaction using the budget service
            try:
                budget_service.save_transaction(str(user.id), transaction_data)
                category_name = budget_service.get_category_name(transaction_data['category_id'])
                subcategory_name = budget_service.get_subcategory_name(transaction_data.get('subcategory_id', None))
                bot.send_message(
                    call.message.chat.id,
                    strings[user.lang].transaction_saved.format(
                        category=category_name,
                        subcategory=subcategory_name if subcategory_name else "",
                        amount=transaction_data['amount'],
                        comment=transaction_data['comment'],
                    ),
                )
                logger.info(f"Transaction saved successfully for user {user.id}")
            except Exception as e:
                logger.error(f"Error saving transaction for user {user.id}: {e}")
                bot.send_message(
                    call.message.chat.id,
                    strings[user.lang].transaction_error,
                )

        state.delete()

    @bot.message_handler(commands=['update_categories'])
    def update_categories_cache(message: types.Message):
        user = message.from_user
        try:
            # Show loading message
            sent_message = bot.send_message(
                message.chat.id,
                strings[user.lang].updating_categories,
            )

            # Refresh the cache
            success = budget_service.refresh_categories_cache()

            if success:
                bot.edit_message_text(
                    strings[user.lang].categories_updated,
                    message.chat.id,
                    sent_message.message_id,
                )
            else:
                bot.edit_message_text(
                    strings[user.lang].categories_update_error,
                    message.chat.id,
                    sent_message.message_id,
                )
        except Exception as e:
            logger.error(f"Error updating categories cache: {e}")
            bot.edit_message_text(
                strings[user.lang].categories_update_error,
                message.chat.id,
                message.message_id
            )

    @bot.callback_query_handler(func=lambda call: call.data == "cancel_transaction")
    def cancel_transaction(call: types.CallbackQuery, data: dict):
        user = data["user"]
        state = StateContext(call, bot)
        state.delete()

        bot.edit_message_text(
            strings[user.lang].transaction_cancelled,
            call.message.chat.id,
            call.message.message_id
        )
