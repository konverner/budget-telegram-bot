import logging

from pathlib import Path

from omegaconf import OmegaConf
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Load configuration
CURRENT_DIR = Path(__file__).parent
config = OmegaConf.load(CURRENT_DIR / "config.yaml")
strings = config.strings


# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def create_category_markup(categories, lang):
    """Create markup for category selection"""
    markup = InlineKeyboardMarkup(row_width=2)
    for category in categories:
        markup.add(InlineKeyboardButton(
            category['name'],
            callback_data=f"cat_{category['id']}"
        ))
    markup.add(InlineKeyboardButton(
        strings[lang].cancel,
        callback_data="cancel_transaction"
    ))
    return markup

def create_cancel_button(lang: str) -> InlineKeyboardMarkup:
    """Create a cancel button"""
    cancel_button = InlineKeyboardMarkup(row_width=1)
    cancel_button.add(
        InlineKeyboardButton(strings[lang].cancel, callback_data="cancel_transaction"),
    )
    return cancel_button

def create_subcategory_markup(subcategories, lang):
    """Create markup for subcategory selection"""
    markup = InlineKeyboardMarkup(row_width=2)
    for subcategory in subcategories:
        markup.add(InlineKeyboardButton(
            subcategory['name'], 
            callback_data=f"subcat_{subcategory['id']}"
        ))
    markup.add(InlineKeyboardButton(
        strings[lang].cancel, 
        callback_data="cancel_transaction"
    ))
    return markup

def create_skip_button(lang: str) -> InlineKeyboardMarkup:
    """Create a skip button for the items menu"""
    skip_button = InlineKeyboardMarkup(row_width=1)
    skip_button.add(
        InlineKeyboardButton(strings[lang].skip, callback_data="skip_comment"),
    )
    return skip_button