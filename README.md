
# Telegram Notification Bot

Makes a request to the ENDPOINT of an API service.
Retrieves the status of that work from JSON from information about a particular homework.
When the work status changes, it sends a message to Telegram.
When an error occurs, it sends a Telegram message.
Logs work
Includes Procfile for Heroku

## Technology:
 - Python
 - Telegram
 - API
 - Logger
 - Pytest
 - Heroku

### .env example

```
PRACTICUM_TOKEN = # PRACTICUM REST API Token
TELEGRAM_TOKEN = # TELEGRAM Messanger Token
TELEGRAM_CHAT_ID= # Telegram chat ID [int]
```

## Installation

Clone the repository:
```
git clone https://github.com/web2cap/hw02_community.git
```

Create and activate virtual environment:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Install dependencies from requirements.txt file:

```
pip install -r requirements.txt
```

create .env file and fill by example:
```
touch .env
```

Run project:

```
python3 homework.py
```

### Author:

Pavel Koshelev
