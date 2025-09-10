# pharma_checker.py for GitHub Actions
import requests
from bs4 import BeautifulSoup
import telegram
import time
import os

# --- CONFIGURATION ---
# Get secrets from GitHub Actions environment variables
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

URL_TO_CHECK = 'https://aiimsbhubaneswar.nic.in/Recruitment_Notice.aspx'
KEYWORDS = ['pharmacist', 'pharma', 'pharmacy']
SENT_NOTICES_FILE = 'sent_notices.txt' 
# NOTE: This file won't work perfectly on GitHub Actions without extra steps.
# For now, the script will re-send old notices each time it runs. We can refine this later.
# --- END OF CONFIGURATION ---

# (The rest of the script is the same as before)

def send_telegram_message(message):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        print(f"Notification sent successfully.")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def check_for_updates():
    print(f"Checking for updates on {URL_TO_CHECK}...")
    try:
        response = requests.get(URL_TO_CHECK, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        notices = soup.find_all('tr') 
        new_notices_found = False

        for notice in notices:
            notice_text = notice.get_text().lower()
            if any(keyword in notice_text for keyword in KEYWORDS):
                link_tag = notice.find('a')
                if link_tag and 'href' in link_tag.attrs:
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = f"https://aiimsbhubaneswar.nic.in/{link}"
                    
                    # Simple check to see if we've found a new one
                    new_notices_found = True
                    title_text = ' '.join(notice.get_text().strip().split())
                    message = f"🚨 <b>Pharma Alert (from GitHub)!</b>\n\n<b>Title:</b> {title_text}\n<b>Link:</b> <a href='{link}'>Click Here</a>"
                    send_telegram_message(message)
        
        if not new_notices_found:
            print("No new notices found matching keywords.")
                    
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to the website: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_for_updates()
    print("Check complete.")
