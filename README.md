# Telegram Bot

A Telegram bot built with Python, FastAPI, and python-telegram-bot, leveraging Mistral AI for advanced processing.

## Architecture

The bot now uses:
- Mistral AI for intelligent message processing
- Notion integration for data management
- Docker for consistent deployment
- Flexible dependency management with pip-tools

## Local Deployment with Docker

### Prerequisites

1. Create a Telegram bot and get your bot token from [@BotFather](https://t.me/botfather)
2. Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
3. Install [pip-tools](https://pip.pypa.io/en/stable/installation/): `pip install pip-tools`
4. Install [Node.js](https://nodejs.org/) (for localtunnel)
5. Install localtunnel: `npm install -g localtunnel`

### Environment Setup

1. Create a `.env` file with required tokens:
```
TELEGRAM_BOT_TOKEN=your_bot_token
NOTION_TOKEN=your_notion_token
MISTRAL_API_KEY=your_mistral_api_key
OFFERS_DATABASE_ID=your_offers_db_id
ADVERTISERS_DATABASE_ID=your_advertisers_db_id
ENVIRONMENT=production
```

2. Manage Dependencies
```bash
# Update dependencies
pip-compile requirements.in
pip-sync requirements.txt
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

### Development Workflow

1. **Dependency Management**
```bash
# Add new package
echo "new-package>=1.0.0" >> requirements.in
pip-compile requirements.in
pip-sync requirements.txt
```

2. **Run Without Docker**
```bash
python -m venv venv
source venv/bin/activate
pip-sync requirements.txt
python scripts/start_local.py
```

3. **Docker Development**
```bash
# Start services
docker-compose up

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up --build
```

### Troubleshooting

1. **Dependency Issues**
```bash
# Regenerate exact dependencies
pip-compile requirements.in
pip-sync requirements.txt
```

2. **Webhook Debugging**
```bash
# Check webhook status
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"

# Delete webhook
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
```

3. **Docker Troubleshooting**
```bash
# Check container logs
docker-compose logs

# Restart containers
docker-compose restart

# Rebuild containers
docker-compose up --build
```

## Best Practices

- Always use `pip-tools` for dependency management
- Keep `.env` file secure and out of version control
- Use environment variables for sensitive information
- Regularly update dependencies using `pip-compile`
- Monitor Docker logs for potential issues
- Use localtunnel for easy webhook testing

## Future Improvements

- Implement more robust error handling
- Add comprehensive logging
- Enhance AI-powered message processing
- Implement more advanced Notion integrations
