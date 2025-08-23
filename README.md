## Budget Telegram Bot

This is a Telegram Bot used as a interface for budgeting with Google Sheets.

The Google Sheets are often used for budgeting purposes ([1](https://www.reddit.com/r/personalfinance/comments/c4mzfe/i_made_a_google_sheet_to_replace_quicken/)) but the problem is to enter transactions is not always comfortable, espacially via mobile on the go. This bot allows you to enter transactions via Telegram messanger.

## Launch

### Google Sheets

By-default the bot is looking for a sheet named "budget" with two worksheets "transactions" and "categories". You can see example here:

To allow communication between google sheets you need to set a service account on Goolge Cloud:

#### 1. Create a Google Cloud project

To access Google products via API, you must have a developer project on Google Workspace

https://developers.google.com/workspace/guides/create-project

#### 2. Create a service account

You cannot use your personal account for API use, you need to create a service account specifically for the bot:

<img width="666" height="569" alt="Screenshot From 2025-08-15 22-00-49" src="https://github.com/user-attachments/assets/2900879e-5128-4037-8fc4-78b2a95b2191" />
  
#### 3. Enable APIs for the service account

For the created service account, we need to enable Google Sheet and Google Drive APIs: https://developers.google.com/workspace/guides/enable-apis

#### 4. Create credentials

For authorization and authofication of service account, you must create credentials and save them as a JSON file.

<img width="762" height="649" alt="Screenshot From 2025-08-15 22-01-37" src="https://github.com/user-attachments/assets/9192f484-4121-4411-a142-ccadee6ef533" />


### Telegram Bot

#### Create bot account

You need to create a bot account and obtain a token via BotFather: https://core.telegram.org/bots/tutorial#obtain-your-bot-token

#### Setup

1. Clone this repository.
2. Enter values in `.env.example` and rename it to `.env`.

#### Run 

You can run the project directly on your machine or in Docker.

##### Option 1: Run Directly

1. Install the dependencies with `pip install .`.
2. Run the bot with `python -m src.app.main`.

##### Option 2: Run in Docker

To run this application in a Docker container, follow these steps:

1. Build the Docker image with `docker build -t budget-telegram-bot .`.
2. Run the Docker container with `docker run budget-telegram-bot`.
1. Build the Docker image with `docker build -t budget-telegram-bot .`.
2. Run the Docker container with `docker run budget-telegram-bot`.

