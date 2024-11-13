# scripts/setup_webhook.py
import os
import sys
import httpx
import json
from dotenv import load_dotenv
from pyngrok import ngrok
import argparse
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

def setup_webhook(environment='local'):
    """Set up Telegram webhook for local testing or production"""
    try:
        # Get environment variables
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        
        if not all([bot_token, webhook_secret]):
            print("❌ Missing required environment variables:")
            print(f"BOT_TOKEN: {'✓' if bot_token else '✗'}")
            print(f"WEBHOOK_SECRET: {'✓' if webhook_secret else '✗'}")
            return False

        # Determine webhook URL based on environment
        if environment == 'local':
            # Start ngrok tunnel for local testing
            try:
                public_url = ngrok.connect(8000).public_url
                webhook_url = f"{public_url}/api/telegram"
                print(f"🚀 Started ngrok tunnel: {public_url}")
            except Exception as e:
                print(f"❌ Failed to start ngrok: {str(e)}")
                return False
        else:
            # Get Vercel URL for production
            vercel_url = os.getenv("VERCEL_URL")
            if not vercel_url:
                print("❌ VERCEL_URL not found in environment")
                return False
            webhook_url = f"https://{vercel_url}/api/telegram"

        print(f"\n🔄 Setting webhook URL: {webhook_url}")

        # First, delete any existing webhook
        delete_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        response = httpx.post(delete_url)
        response.raise_for_status()
        print("✅ Deleted existing webhook")

        # Set the new webhook
        set_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        webhook_data = {
            "url": webhook_url,
            "secret_token": webhook_secret,
            "allowed_updates": ["message", "callback_query"]
        }
        
        response = httpx.post(set_url, json=webhook_data)
        response.raise_for_status()
        print("✅ Set new webhook")

        # Verify webhook info
        info_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = httpx.get(info_url)
        response.raise_for_status()
        
        webhook_info = response.json()
        if webhook_info.get("ok"):
            info = webhook_info.get("result", {})
            print("\n📊 Webhook Status:")
            print(f"URL: {info.get('url')}")
            print(f"Custom certificate: {info.get('has_custom_certificate', False)}")
            print(f"Pending updates: {info.get('pending_update_count', 0)}")
            print(f"Max connections: {info.get('max_connections', 'N/A')}")
            print(f"Last error: {info.get('last_error_message', 'None')}")
            print("\n✨ Webhook setup successful!")
            return True
        else:
            print(f"\n❌ Failed to verify webhook: {webhook_info}")
            return False

    except Exception as e:
        print(f"\n❌ Error setting up webhook: {str(e)}")
        return False

def cleanup_webhook():
    """Clean up webhook and ngrok"""
    try:
        # Delete webhook
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if bot_token:
            delete_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
            response = httpx.post(delete_url)
            response.raise_for_status()
            print("✅ Webhook deleted")
        
        # Kill ngrok if running
        ngrok.kill()
        print("✅ Ngrok tunnel closed")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Setup Telegram webhook')
    parser.add_argument('--env', choices=['local', 'production'], 
                       default='local', help='Environment to setup webhook for')
    args = parser.parse_args()

    try:
        print(f"🔧 Setting up webhook for {args.env} environment...")
        if setup_webhook(args.env):
            if args.env == 'local':
                print("\n📝 Press Ctrl+C to stop the webhook and cleanup")
                try:
                    import time
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping webhook...")
                    cleanup_webhook()
                    print("✅ Cleanup complete")
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted...")
        cleanup_webhook()
        print("✅ Cleanup complete")
        sys.exit(1)