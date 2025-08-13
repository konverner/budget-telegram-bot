import logging
from datetime import datetime
from pathlib import Path

from omegaconf import OmegaConf

from ..plugins.google_sheets.client import GoogleSheetsClient

# Load configuration
CURRENT_DIR = Path(__file__).parent
config = OmegaConf.load(CURRENT_DIR / "config.yaml")

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class BudgetService:
    """Budget service class for handling Google Sheets operations"""

    def __init__(self):
        """Initialize the budget service with Google Sheets client"""
        self.google_sheets = GoogleSheetsClient(share_emails=config.app.share_emails)
        self.sheet_name = config.app.sheet_name
        self.categories_worksheet = config.app.categories_worksheet
        self.transactions_worksheet = config.app.transactions_worksheet
        self._categories_cache = None

    def _get_or_create_sheet(self):
        """Get or create the budget sheet"""
        try:
            return self.google_sheets.get_sheet(self.sheet_name)
        except Exception:
            logger.info(f"Sheet {self.sheet_name} not found, creating new one")
            return self.google_sheets.create_sheet(self.sheet_name)

    def _ensure_categories_worksheet(self, sheet):
        """Ensure categories worksheet exists with proper headers"""
        try:
            self.google_sheets.create_worksheet(sheet, self.categories_worksheet)
            # Add headers and sample data
            headers = ["Category"]
            sample_categories = [
                "Housing", "Housing.Rent", "Housing.Supplies", "Housing.Electricity",
                "Housing.Internet", "Housing.Cell", "Transportation", "Food",
                "Food.Groceries", "Food.Restaurants", "Health", "Health.Hair",
                "Health.Medical", "Miscellaneous", "Travel", "Travel.Food",
                "Travel.Accommodation", "Travel.Transportation", "Travel.Entertainment",
                "Travel.Miscellaneous", "Salary", "Freelance"
            ]
            self.google_sheets.add_row(sheet, self.categories_worksheet, headers)
            for category in sample_categories:
                self.google_sheets.add_row(sheet, self.categories_worksheet, [category])
            logger.info("Categories worksheet created with sample data")
        except Exception as e:
            logger.info(f"Categories worksheet already exists: {e}")

    def _ensure_transactions_worksheet(self, sheet):
        """Ensure transactions worksheet exists with proper headers"""
        try:
            self.google_sheets.create_worksheet(sheet, self.transactions_worksheet)
            headers = ["Date", "Category", "Amount", "Comment"]
            self.google_sheets.add_row(sheet, self.transactions_worksheet, headers)
            logger.info("Transactions worksheet created")
        except Exception as e:
            logger.info(f"Transactions worksheet already exists: {e}")

    def _parse_categories_from_sheet(self, sheet) -> dict[str, list[dict]]:
        """Parse categories and subcategories from Google Sheet"""
        if self._categories_cache:
            return self._categories_cache

        try:
            worksheet = sheet.worksheet(self.categories_worksheet)
            # Get all values from column A starting from row 2
            all_values = worksheet.get_all_values()
            if not all_values or len(all_values) < 2:
                logger.warning("No categories data found in worksheet")
                return {}

            categories_data = [row[0] for row in all_values[1:] if row and row[0].strip()]

            categories = {}
            category_id = 1

            for category_name in categories_data:
                category_name = category_name.strip()
                if not category_name:
                    continue

                if '.' not in category_name:
                    # Main category
                    categories[category_name] = {
                        'id': category_id,
                        'name': category_name,
                        'subcategories': []
                    }
                    category_id += 1
                else:
                    # Subcategory
                    parts = category_name.split('.', 1)
                    main_category = parts[0].strip()
                    subcategory = parts[1].strip()

                    if main_category in categories:
                        categories[main_category]['subcategories'].append({
                            'id': category_id,
                            'name': subcategory,
                            'full_name': category_name
                        })
                        category_id += 1
            self._categories_cache = categories
            return categories
        except Exception as e:
            logger.error(f"Error parsing categories from sheet: {e}")
            return {}

    def _clear_cache(self):
        """Clear the categories cache"""
        self._categories_cache = None

    def get_categories(self) -> list[dict]:
        """Get main budget categories"""
        if self._categories_cache:
            return [
                {'id': cat_data['id'], 'name': cat_data['name']}
                for cat_data in self._categories_cache.values()
            ]
        sheet = self._get_or_create_sheet()
        self._ensure_categories_worksheet(sheet)

        categories_data = self._parse_categories_from_sheet(sheet)

        # Return only main categories
        return [
            {'id': cat_data['id'], 'name': cat_data['name']} 
            for cat_data in categories_data.values()
        ]

    def get_subcategories(self, category_id: int) -> list[dict]:
        """Get subcategories for a given category"""
        if self._categories_cache:
            for cat_data in self._categories_cache.values():
                if cat_data['id'] == category_id:
                    return cat_data['subcategories']

        sheet = self._get_or_create_sheet()
        categories_data = self._parse_categories_from_sheet(sheet)

        # Find the category by ID
        for cat_data in categories_data.values():
            if cat_data['id'] == category_id:
                return cat_data['subcategories']
        return []

    def get_category_name(self, category_id: int) -> str:
        """Get category name by ID"""
        if self._categories_cache:
            for cat_data in self._categories_cache.values():
                if cat_data['id'] == category_id:
                    return cat_data['name']
        sheet = self._get_or_create_sheet()
        categories_data = self._parse_categories_from_sheet(sheet)
        for cat_data in categories_data.values():
            if cat_data['id'] == category_id:
                return cat_data['name']
        return "Unknown"

    def get_subcategory_name(self, subcategory_id: int) -> str:
        """Get subcategory name by ID"""
        if not subcategory_id:
            return ""
        if self._categories_cache:
            for cat_data in self._categories_cache.values():
                for subcat in cat_data['subcategories']:
                    if subcat['id'] == subcategory_id:
                        return subcat['name']
        sheet = self._get_or_create_sheet()
        categories_data = self._parse_categories_from_sheet(sheet)
        for cat_data in categories_data.values():
            for subcat in cat_data['subcategories']:
                if subcat['id'] == subcategory_id:
                    return subcat['name']
        return ""

    def save_transaction(self, user_id: str, transaction_data: dict) -> None:
        """Save transaction to Google Sheets"""
        sheet = self._get_or_create_sheet()
        self._ensure_transactions_worksheet(sheet)

        # Get category and subcategory names
        category_name = self.get_category_name(transaction_data['category_id'])
        subcategory_name = self.get_subcategory_name(transaction_data.get('subcategory_id'))

        # Build full category name
        if subcategory_name:
            full_category = f"{category_name}.{subcategory_name}"
        else:
            full_category = category_name

        row_data = [
            full_category,
            datetime.now().strftime("%Y/%m/%d"),
            transaction_data['amount'],
            transaction_data.get('comment', '')
        ]

        self.google_sheets.add_row(sheet, self.transactions_worksheet, row_data)
        logger.info("Transaction saved for user {user_id}: {row_data}")

    def refresh_categories_cache(self) -> bool:
        """Force refresh the categories cache from Google Sheets"""
        try:
            self._clear_cache()
            sheet = self._get_or_create_sheet()
            self._ensure_categories_worksheet(sheet)
            # Force reload categories by calling _parse_categories_from_sheet
            categories_data = self._parse_categories_from_sheet(sheet)
            logger.info(f"Categories cache refreshed successfully. Found {len(categories_data)} main categories.")
            return True
        except Exception as e:
            logger.error(f"Error refreshing categories cache: {e}")
            return False


# Create service instance
budget_service = BudgetService()
