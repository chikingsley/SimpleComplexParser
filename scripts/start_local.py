import os
import subprocess
import sys
import time
import requests
from dotenv import load_dotenv

def start_localtunnel(port):
    """Start localtunnel and return the URL"""
    process = subprocess.Popen(
        ['lt', '--port', str(port), '--subdomain', 'dealparser'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for localtunnel to start and get URL
    for line in process.stdout:
        if 'your url is:' in line.lower():
            url = line.split('your url is: ')[-1].strip()
            print(f"Localtunnel URL: {url}")
            return url, process
    
    raise Exception("Failed to start localtunnel")

def set_webhook(bot_token, webhook_url, secret_token):
    """Set Telegram webhook"""
    # Ensure URL ends with /api/telegram
    if not webhook_url.endswith('/api/telegram'):
        webhook_url = webhook_url.rstrip('/') + '/api/telegram'
    
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    data = {
        "url": webhook_url,
        "secret_token": secret_token,
        "allowed_updates": ["message", "callback_query"]
    }
    
    print(f"Setting webhook to: {webhook_url}")
    response = requests.post(api_url, json=data)
    return response.json()

def main():
    # Load environment variables
    load_dotenv()
    
    # Get environment variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    webhook_secret = os.getenv("WEBHOOK_SECRET")
    
    if not all([bot_token, webhook_secret]):
        print("Error: Missing required environment variables")
        sys.exit(1)
    
    try:
        # Start localtunnel
        port = 8000  # Match the port in docker-compose.yml
        tunnel_url, tunnel_process = start_localtunnel(port)
        print(f"Tunnel established at: {tunnel_url}")
        
        # Give the tunnel a moment to stabilize
        time.sleep(2)
        
        # Set webhook
        result = set_webhook(bot_token, tunnel_url, webhook_secret)
        print(f"Webhook set result: {result}")
        
        if not result.get('ok'):
            print(f"Failed to set webhook: {result.get('description')}")
            tunnel_process.terminate()
            sys.exit(1)
            
        print("Webhook set successfully! Bot is ready.")
        print("Press Ctrl+C to stop the tunnel")
        
        # Keep script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        tunnel_process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        if 'tunnel_process' in locals():
            tunnel_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main() 