# Telegram Bot

A Telegram bot built with Python, FastAPI, and python-telegram-bot.

## Deployment to Render

### Prerequisites

1. Create a Telegram bot and get your bot token from [@BotFather](https://t.me/botfather)
2. Create a [Render account](https://render.com)
3. Fork/clone this repository

### Deployment Steps

1. **Create New Web Service**
   - Go to Render Dashboard
   - Click "New +" and select "Web Service"
   - Connect your repository
   - Choose the branch to deploy

2. **Configure Environment Variables**
   
   Add the following environment variables in Render dashboard:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   WEBHOOK_SECRET=generate_random_secret_here
   WEBHOOK_URL=https://your-app-name.onrender.com
   ENVIRONMENT=production
   ```

3. **Deploy Settings**
   - Name: Choose a name for your service
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.telegram:app --host 0.0.0.0 --port $PORT`
   - Select "Auto-Deploy: Yes"

4. **Verify Deployment**
   - Wait for deployment to complete
   - Visit `https://your-app-name.onrender.com/health`
   - Should return `{"status": "healthy"}`

5. **Set Up Telegram Webhook**
   - The webhook will be automatically set during application startup
   - Verify webhook status by sending a message to your bot
   - Check logs in Render dashboard for any issues

### Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   ENVIRONMENT=development
   ```
5. Run locally:
   ```bash
   uvicorn api.telegram:app --reload
   ```

### Monitoring and Logs

- Monitor your application through Render dashboard
- View logs: Render Dashboard → Your Service → Logs
- Set up alerts for errors and downtime

### Troubleshooting

1. **Webhook Issues**
   - Check WEBHOOK_URL is correct
   - Verify WEBHOOK_SECRET is set
   - Check logs for webhook-related errors

2. **Application Errors**
   - Review Render logs
   - Verify all environment variables are set
   - Check application logs for specific error messages

3. **Bot Not Responding**
   - Verify bot token is correct
   - Check webhook status using Telegram API
   - Ensure application health check passes
