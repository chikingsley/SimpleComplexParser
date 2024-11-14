# Telegram Bot

A Telegram bot built with Python, FastAPI, and python-telegram-bot.

## Local Deployment with Docker

### Prerequisites

1. Create a Telegram bot and get your bot token from [@BotFather](https://t.me/botfather)
2. Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
3. Install [Node.js](https://nodejs.org/) (for localtunnel)
4. Install localtunnel: `npm install -g localtunnel`

### Environment Setup

Create a `.env` file:
```
TELEGRAM_BOT_TOKEN=your_bot_token
NOTION_TOKEN=your_notion_token
OFFERS_DATABASE_ID=your_offers_db_id
ADVERTISERS_DATABASE_ID=your_advertisers_db_id
WEBHOOK_SECRET=your_webhook_secret
```

### Deployment Steps

1. **Build and Start Docker Container**
```bash
docker-compose up --build
```

2. **Start Localtunnel in Another Terminal**
```bash
python scripts/start_local.py
```

3. **Verify Deployment**
- Check the localtunnel URL in the console
- Send a message to your bot
- Check Docker logs for incoming requests

### Development

1. **Run Without Docker**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the bot
python scripts/start_local.py
```

2. **Run with Docker**
```bash
# Start services
docker-compose up

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up --build
```

### Troubleshooting

1. **Webhook Issues**
```bash
# Check webhook status
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"

# Delete webhook
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
```

2. **Container Issues**
```bash
# Check container logs
docker-compose logs

# Restart containers
docker-compose restart

# Rebuild containers
docker-compose up --build
```

3. **Localtunnel Issues**
```bash
# Kill existing localtunnel
pkill -f "lt --port"

# Restart localtunnel
python scripts/start_local.py
```


