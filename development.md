# Budget Telegram Bot

## Overview

This is a Telegram Bot used as a interface for budgeting with Google Sheets.


## Structure

The project is based on this template https://github.com/konverner/telegram-bot. 

The project is composed of features. Each feature is defined with:

- Data models: They represent entities in the database.

- Service: It performs business logic with the database.

- Config: It is a YAML file that keeps changeable values like strings and parameters of the feature.

- Handlers: They listen to Telegram actions, similar to routes in classic API architecture.

- Markup: It defines functions for generating UI elements.

### Core Features

### Details

### Webhook vs Polling

We can run a bot via API polling or via Webhook. See the difference:

| Feature |	Polling |	Webhook |
| - | - | - |
| Initiation |	Client-initiated (we) |	Server-initiated (telegram) |
| Data Flow |	Client pulls data from server |	Server pushes data to client |
| Resource Usage |	Can be inefficient (many empty calls)	| Efficient (only sends data when an event occurs) |
| Use Case |	Need for quick response; large data processing | Quick response; small data processing |
| Public IP | No public IP is needed | HTTPS server is needed |

### Webhook

To set webhook, you need to provide in `.env` one of the following:

- `WEBHOOK_URL` : https address
- `HOST`: Public IP of host machine; `PORT`: 443, 80 or 8443; `WEBHOOK_SSL_CERT`, `WEBHOOK_SSL_PRIVKEY`.

One can generate self-signed SSL certificate:

```
openssl genrsa -out webhook_pkey.pem 2048
openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
```
When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply with the same value in you put in `HOST`

Set environment variable `COMMUNICATION_STRATEGY` in `.env` to values `polling` or `webhook`.


