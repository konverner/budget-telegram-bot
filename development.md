# Budget Telegram Bot - Development Notes

## Overview

This is a Telegram Bot that provides an interface for budgeting with Google Sheets. The bot allows users to easily record and manage financial transactions through Telegram, with automatic synchronization to Google Sheets.

## Development Setup

### Initial Setup

#### 1. Clone the repository

```bash
git clone https://github.com/konverner/budget-telegram-bot.git
cd budget-telegram-bot
```

#### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install development dependencies

```bash
pip install -e ".[all]"
```

#### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

#### 5. Install pre-commit hooks (optional but recommended):

```bash
pre-commit install
```


## Project Architecture

### Structure

The project is based on a modular architecture with separation of concerns. It follows the template from https://github.com/konverner/telegram-bot.

```
src/
├── app/
│   ├── auth/           # User authentication and authorization
│   ├── budget/         # Core budget management features
│   ├── database/       # Database models and operations
│   ├── language/       # Multi-language support
│   ├── middleware/     # Bot middleware components
│   ├── plugins/        # External service integrations
│   │   └── google_sheets/  # Google Sheets API integration
│   ├── config.py       # Application configuration
│   └── main.py         # Application entry point
tests/                  # Test files
```

Each feature is organized with the following components:

- **Data Models**: SQLAlchemy models representing database entities
- **Services**: Business logic and database operations
- **Config**: YAML files with configurable parameters and strings
- **Handlers**: Telegram message/callback handlers (similar to API routes)
- **Markup**: Functions for generating Telegram UI elements (keyboards, buttons)

### Components

#### Configuration System
- **File**: `src/app/config.py`
- Uses Pydantic Settings for environment variable management
- Supports multiple environments (local, staging, production)
- Automatic validation and type checking

#### Database Layer
- **File**: `src/app/database/core.py`
- SQLAlchemy ORM with automatic table creation
- Support for both SQLite and PostgreSQL
- Session management with proper cleanup

#### Middleware System
- **Anti-flood Protection**: Rate limiting to prevent spam
- **Database Middleware**: Automatic session injection
- **User Middleware**: User creation and authentication
- **State Management**: Conversation state tracking

#### Plugin System
- **Google Sheets Integration**: Automatic data synchronization
- **Extensible Architecture**: Easy to add new external services

## Communication Strategies

### Webhook vs Polling

The bot supports two communication modes with Telegram:

| Feature | Polling | Webhook |
|---------|---------|---------|
| **Initiation** | Client-initiated (our bot) | Server-initiated (Telegram) |
| **Data Flow** | Client pulls data from server | Server pushes data to client |
| **Resource Usage** | Can be inefficient (many empty calls) | Efficient (only when events occur) |
| **Use Case** | Development, simple deployments | Production, high-traffic bots |
| **Public IP** | Not required | HTTPS server required |
| **Setup Complexity** | Simple | More complex |

### Webhook Configuration

To use webhook mode, configure one of the following in `.env`:

#### Option 1: External Webhook URL
```env
WEBHOOK_URL=https://your-domain.com
```

#### Option 2: Self-Hosted with SSL
```env
HOST=your-public-ip
PORT=443  # Must be 443, 80, or 8443
WEBHOOK_SSL_CERT=./webhook_cert.pem
WEBHOOK_SSL_PRIVKEY=./webhook_pkey.pem
```

Generate self-signed SSL certificates:
```bash
openssl genrsa -out webhook_pkey.pem 2048
openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
```

⚠️ **Important**: When prompted for "Common Name", use the same value as your `HOST`.

Set the communication strategy:
```env
COMMUNICATION_STRATEGY=webhook  # or "polling"
```


### Code Quality and Testing

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/

# Run specific test file
pytest tests/test_app.py
```

#### Code Linting and Formatting
```bash
# Check code style
ruff check src/

# Format code
ruff format src/

# Type checking
mypy src/
```

#### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Database Development

#### Migrations
The project uses SQLAlchemy with automatic table creation:
- Tables are created automatically on first run
- Schema changes require manual migration planning
- Use `drop_tables()` and `create_tables()` for development resets

#### Working with Different Databases

To use PostgreSQL, we set configuration in .env

```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=budget_bot
DB_PASSWORD=secure_password
DB_NAME=budget_bot_db
```

If not set, SQLite will be used and a database is saved as `local_database.db`

### Adding New Features

To add a new feature:

#### 1. Create feature directory

   ```
   src/app/new_feature/
   ├── __init__.py
   ├── models.py       # Database models
   ├── services.py     # Business logic
   ├── handlers.py     # Telegram handlers
   ├── markup.py       # UI elements
   └── config.yaml     # Feature configuration
   ```

#### 2. Register handlers


   ```python
   # In src/app/main.py
   from .new_feature.handlers import register_handlers as new_feature_handlers
   
   handlers = [
       language_handlers,
       budget_handlers,
       new_feature_handlers  # Add here
   ]
   ```

#### 3. Add database models

```python
# In new_feature/models.py
from sqlalchemy import Column, Integer, String
from ..auth.models import Base

class NewFeatureModel(Base):
    __tablename__ = "new_feature"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

#### 4. Create tests


```python
# In tests/test_new_feature.py
def test_new_feature():
    assert True
```


