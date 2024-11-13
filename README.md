# Deal Parser Bot

A Telegram bot that handles both formatted and unformatted deal submissions with Notion integration.

## Features

- Handles two types of deal formats:
  - Formatted: `TIER1-Partner-GEO-Language-Source-Model-CPA-CRG-CPL-Funnels-CR-Deduction`
  - Unformatted: Natural language deal descriptions
- Notion integration for deal storage
- Interactive deal editing and validation
- Webhook support for production deployment

## Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd deal-parser-bot
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the project root:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
NOTION_TOKEN=your_notion_token
OFFERS_DATABASE_ID=your_offers_database_id
ADVERTISERS_DATABASE_ID=your_advertisers_database_id
WEBHOOK_SECRET=your_webhook_secret
```

5. **Run local webhook server**
```bash
# Install ngrok if not already installed
pip install pyngrok

# Start webhook server
python scripts/test_webhook.py
python scripts/tunnel.py
```

The bot will be available through the ngrok URL displayed in the console.

## Production Deployment (Vercel)

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Configure Vercel environment variables**
```bash
vercel env add TELEGRAM_BOT_TOKEN
vercel env add NOTION_TOKEN
vercel env add OFFERS_DATABASE_ID
vercel env add ADVERTISERS_DATABASE_ID
vercel env add WEBHOOK_SECRET
```

3. **Deploy to Vercel**
```bash
vercel
```

The webhook will be automatically configured during deployment.

## Project Structure

```
project_root/
├── api/
│   └── telegram.py      # Webhook handler
├── bot/
│   ├── router.py        # Message router
│   ├── client.py        # Deal parsing client
│   └── message.py       # Message handling
├── scripts/
│   ├── setup_webhook.py # Webhook configuration
│   └── test_webhook.py  # Local testing
├── main.py             # Main bot application
├── main_simple.py      # Simple deal flow
└── main_complex.py     # Complex deal flow
```

## Testing

1. **Local Testing**
```bash
# Start local webhook server
python scripts/test_webhook.py

# In another terminal, send test messages to your bot
```

2. **Production Testing**
After deployment, send messages to your bot on Telegram.

## Webhook Management

- **Set up local webhook:**
```bash
python scripts/setup_webhook.py --env local
```

- **Set up production webhook:**
```bash
python scripts/setup_webhook.py --env production
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| TELEGRAM_BOT_TOKEN | Your Telegram bot token from BotFather |
| NOTION_TOKEN | Notion integration token |
| OFFERS_DATABASE_ID | Notion database ID for offers |
| ADVERTISERS_DATABASE_ID | Notion database ID for advertisers |
| WEBHOOK_SECRET | Secret token for webhook verification |

## Troubleshooting

1. **Webhook Issues**
   - Check webhook status: `https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo`
   - Verify webhook URL is accessible
   - Check webhook secret matches

2. **Notion Integration**
   - Verify database permissions
   - Check integration token access
   - Validate database structure

3. **Local Development**
   - Ensure ngrok is running
   - Verify environment variables
   - Check FastAPI server logs

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 