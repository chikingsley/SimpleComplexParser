import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

import asyncio
import requests
import json
from pyngrok import ngrok
import uvicorn
import signal
from dotenv import load_dotenv

load_dotenv()

async def setup_webhook():
    """Set up webhook for testing"""
    try:
        # Start ngrok tunnel
        port = 8000
        public_url = ngrok.connect(port).public_url
        webhook_url = f"{public_url}/api/telegram"
        
        # Get bot token
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found")
            
        # Get webhook secret
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        
        # Set webhook
        webhook_data = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": True
        }
        
        if webhook_secret:
            webhook_data["secret_token"] = webhook_secret
            
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            json=webhook_data
        )
        
        if response.status_code == 200:
            print(f"✅ Webhook set successfully!")
            print(f"URL: {webhook_url}")
            return True
        else:
            print(f"❌ Failed to set webhook: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up webhook: {str(e)}")
        return False

async def cleanup_webhook():
    """Clean up webhook and ngrok"""
    try:
        # Delete webhook
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        requests.get(f"https://api.telegram.org/bot{bot_token}/deleteWebhook")
        
        # Kill ngrok
        ngrok.kill()
        print("\n✅ Cleanup complete")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")

async def run_server():
    """Run the FastAPI server"""
    config = uvicorn.Config(
        "api.telegram:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
    server = uvicorn.Server(config)
    await server.serve()

async def test_webhook():
    """Test webhook setup"""
    try:
        # Setup webhook
        if not await setup_webhook():
            return
            
        print("\n🚀 Starting local server...")
        
        # Handle shutdown gracefully
        def signal_handler(sig, frame):
            print("\n\n🛑 Shutting down...")
            asyncio.create_task(cleanup_webhook())
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Run server
        await run_server()
        
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        await cleanup_webhook()

if __name__ == "__main__":
    print("🔍 Testing Telegram webhook...")
    print("\n1. Checking local server...")
    asyncio.run(test_webhook()) 