# Budget Telegram Bot

This is a Telegram Bot that provides a convenient interface for budgeting with Google Sheets.

While Google Sheets are commonly used for budgeting purposes ([reference](https://www.reddit.com/r/personalfinance/comments/c4mzfe/i_made_a_google_sheet_to_replace_quicken/)), entering transactions can be uncomfortable, especially on mobile devices. This bot solves that problem by allowing you to easily record transactions via Telegram messages.

## Features

- 📊 **Google Sheets Integration**: Automatically sync your budget data with Google Sheets
- 💰 **Transaction Management**: Add, view, and categorize expenses and income
- 🔒 **Secure Authentication**: Uses Google Cloud Service Account for secure API access
- 🚀 **Multiple Deployment Options**: Run directly or using Docker
- 📱 **Mobile-Friendly**: Designed for easy use on mobile devices via Telegram
- 🛡️ **Anti-spam Protection**: Built-in rate limiting to prevent abuse
- 🗄️ **Flexible Database**: Supports both SQLite (default) and PostgreSQL

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- A Telegram account
- Google Cloud Platform account
- Google Sheets account

### Step 1: Clone the Repository

```bash
git clone https://github.com/konverner/budget-telegram-bot.git
cd budget-telegram-bot
```

### Step 2: Set up Google Sheets and Google Cloud

#### 2.1. Create Google Sheets

1. Create a new Google Sheet and name it "budget"
2. Create two worksheets within the sheet:
   - "transactions" - for recording income and expenses
   - "categories" - for organizing transaction categories
3. **Important**: Share the sheet with your service account email (you'll get this in step 2.4)

Example sheet structure:
- **transactions worksheet**: Date | Amount | Category | Description
- **categories worksheet**: Category | Type (income/expense)

#### 2.2. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Follow the guide: https://developers.google.com/workspace/guides/create-project

#### 2.3. Create a Service Account

1. In Google Cloud Console, go to **IAM & Admin > Service Accounts**
2. Click **"Create Service Account"**
3. Enter a name (e.g., "telegram-bot") and description
4. Click **"Create and Continue"**
5. Skip the optional steps and click **"Done"**

#### 2.4. Enable Required APIs

Enable the following APIs for your project:
1. **Google Sheets API**: https://console.cloud.google.com/apis/api/sheets.googleapis.com
2. **Google Drive API**: https://console.cloud.google.com/apis/api/drive.googleapis.com

Or follow this guide: https://developers.google.com/workspace/guides/enable-apis

#### 2.5. Create Service Account Credentials

1. Go to **IAM & Admin > Service Accounts**
2. Click on your service account
3. Go to the **"Keys"** tab
4. Click **"Add Key" > "Create new key"**
5. Select **"JSON"** and click **"Create"**
6. Save the downloaded JSON file securely
7. **Important**: Share your Google Sheet with the `client_email` from this JSON file

### Step 3: Set up Telegram Bot

#### 3.1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Save the bot token you receive

#### 3.2. Get Your User ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Save your user ID (you'll need this as SUPERUSER_USER_ID)

### Step 4: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and fill in the required values:

   **Required Telegram Settings:**
   ```env
   BOT_TOKEN=your_bot_token_from_botfather
   SUPERUSER_USERNAME=your_telegram_username
   SUPERUSER_USER_ID=your_user_id_from_userinfobot
   ```

   **Required Google Cloud Settings:**
   Extract these values from your downloaded JSON credentials file:
   ```env
   PROJECT_ID=your-project-id
   CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com
   CLIENT_ID=123456789012345678901
   PRIVATE_KEY_ID=your-private-key-id
   PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
   [Copy the entire private key from the JSON file, including line breaks]
   -----END PRIVATE KEY-----"
   CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...
   ```

   **Optional Settings:**
   - Database configuration (defaults to SQLite)
   - Webhook configuration (defaults to polling)
   - Anti-flood protection settings

### Step 5: Install Dependencies

Choose one of the following methods:

#### Option A: Direct Installation
```bash
pip install .
```

#### Option B: Development Installation
```bash
pip install -e ".[all]"
```

## Running the Bot

You can run the project directly on your machine or in Docker.

### Option 1: Run Directly

1. Make sure all dependencies are installed:
   ```bash
   pip install .
   ```

2. Run the bot:
   ```bash
   python -m src.app.main
   ```

### Option 2: Run with Docker

1. Build the Docker image:
   ```bash
   docker build -t budget-telegram-bot .
   ```

2. Run the Docker container:
   ```bash
   docker run --env-file .env budget-telegram-bot
   ```

### Communication Modes

The bot supports two communication modes:

#### Polling Mode (Default)
- No additional setup required
- Bot actively polls Telegram for updates
- Works behind NAT/firewall
- Set `COMMUNICATION_STRATEGY=polling` in `.env`

#### Webhook Mode
- Requires a public HTTPS endpoint
- More efficient for high-traffic bots
- Set `COMMUNICATION_STRATEGY=webhook` in `.env`

For webhook mode, you can either:
1. **Use a webhook URL** (e.g., from ngrok, Railway, Heroku):
   ```env
   WEBHOOK_URL=https://your-domain.com
   ```

2. **Use self-signed SSL certificates**:
   ```bash
   # Generate certificates
   openssl genrsa -out webhook_pkey.pem 2048
   openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
   ```
   
   Then configure:
   ```env
   HOST=your-public-ip
   PORT=443
   WEBHOOK_SSL_CERT=./webhook_cert.pem
   WEBHOOK_SSL_PRIVKEY=./webhook_pkey.pem
   ```

## Database Configuration

### SQLite (Default)
The bot uses SQLite by default, creating a `local_database.db` file automatically. No additional configuration needed.

### PostgreSQL (Production)
For production environments, configure PostgreSQL:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=budget_bot
DB_PASSWORD=your_secure_password
DB_NAME=budget_bot_db
```

The bot will automatically create the necessary tables on first run.

## Usage

1. Start a conversation with your bot on Telegram
2. Use commands to interact with your budget:
   - Add transactions
   - View spending summaries
   - Manage categories
   - Get budget reports

The bot will automatically sync all data with your Google Sheets.

## Troubleshooting

### Common Issues

#### Bot Not Responding
1. Check that `BOT_TOKEN` is correctly set in `.env`
2. Verify the bot token format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
3. Ensure the bot is not running elsewhere
4. Check the logs for error messages

#### Google Sheets Access Denied
1. Verify all Google Cloud credentials are correctly set
2. Ensure the Google Sheets and Drive APIs are enabled
3. Check that you've shared your Google Sheet with the service account email
4. Verify the service account has the necessary permissions

#### Database Connection Issues
1. If using PostgreSQL, check connection parameters
2. Verify the database exists and is accessible
3. For SQLite, ensure write permissions in the directory

#### Permission Denied Errors
1. Check that `SUPERUSER_USER_ID` matches your Telegram user ID
2. Message [@userinfobot](https://t.me/userinfobot) to confirm your user ID

### Getting Help

If you encounter issues:
1. Check the logs for detailed error messages
2. Verify all environment variables are correctly set
3. Ensure all prerequisites are installed
4. Check the [Issues page](https://github.com/konverner/budget-telegram-bot/issues) for similar problems

### Debug Mode

To enable debug logging, set the environment to development:
```env
ENVIRONMENT=local
```

This will provide more detailed logs to help diagnose issues.

