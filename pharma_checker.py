# =========================================================================
# == FINAL, SCALABLE PHARMA JOB CHECKER SCRIPT V4.0 (Homepage Scraping)  ==
# =========================================================================
import requests
from bs4 import BeautifulSoup
import telegram
import time
import os
import urllib3

# Suppress only the single InsecureRequestWarning from a single call to verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

KEYWORDS = ['pharmacist', 'pharma', 'pharmacy', 'b.pharm', 'd.pharm', 'drug inspector', 'recruitment', 'vacancy', 'career']

# --- YOUR CONTROL PANEL: UPDATED TO CHECK HOME PAGES ---
# 'find_all_selector' is now 'a' to find ALL links on the page.
SITES_TO_CHECK = [
    {
        'name': 'PCI Homepage',
        'url': 'https://www.pci.nic.in/', # CHECKING HOMEPAGE
        'base_url': 'https://www.pci.nic.in',
        'find_all_selector': 'a', # Finds all links
        'verify_ssl': True
    },
    {
        'name': 'AIIMS Delhi Homepage',
        'url': 'https://www.aiims.edu/', # CHECKING HOMEPAGE
        'base_url': 'https://www.aiims.edu',
        'find_all_selector': 'a', # Finds all links
        'verify_ssl': True
    },
    {
        'name': 'AIIMS Bhubaneswar Homepage',
        'url': 'https://aiimsbhubaneswar.nic.in/', # CHECKING HOMEPAGE
        'base_url': 'https://aiimsbhubaneswar.nic.in',
        'find_all_selector': 'a', # Finds all links
        'verify_ssl': True
    },
    {
        'name': 'NIPER Guwahati Homepage',
        'url': 'https://niperguwahati.ac.in/', # CHECKING HOMEPAGE
        'base_url': 'https://niperguwahati.ac.in',
        'find_all_selector': 'a', # Finds all links
        'verify_ssl': True
    },
    {
        'name': 'RRB Bhopal Homepage',
        'url': 'https://www.rrbbpl.nic.in/', # CHECKING HOMEPAGE
        'base_url': 'https://www.rrbbpl.nic.in',
        'find_all_selector': 'a', # Finds all links
        'verify_ssl': False # Special SSL fix for this site
    }
]
# --- END OF CONFIGURATION ---

def send_telegram_message(message):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML', disable_web_page_preview=True)
        print("  -> Notification sent successfully.")
    except Exception as e:
        print(f"  -> Error sending Telegram message: {e}")

def check_site(site):
    print(f"\nChecking site: {site['name']} ({site['url']})")
    try:
        response = requests.get(site['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=20, verify=site['verify_ssl'])
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This will now get every single link on the homepage
        all_links = soup.find_all(site['find_all_selector'])
        
        if not all_links:
            print("  -> Could not find any links on the page.")
            return

        new_notices_found = 0
        for link_tag in all_links:
            link_text = link_tag.get_text().lower()
            
            if any(keyword in link_text for keyword in KEYWORDS):
                if 'href' in link_tag.attrs:
                    link = link_tag['href'].strip()
                    
                    # Ignore empty links or simple anchor links
                    if not link or link.startswith('#') or link.startswith('javascript:'):
                        continue

                    if not link.startswith('http'):
                        link = f"{site['base_url'].strip('/')}/{link.lstrip('/')}"
                    
                    new_notices_found += 1
                    title_text = ' '.join(link_tag.get_text().strip().split())
                    message = (f"🚨 <b>Pharma Alert from {site['name']}!</b>\n\n"
                               f"<b>Link Text:</b> {title_text}\n"
                               f"<b>URL:</b> <a href='{link}'>Click Here to Check</a>")
                    send_telegram_message(message)
        
        if new_notices_found == 0:
            print("  -> No links found matching keywords.")

    except requests.exceptions.RequestException as e:
        print(f"  -> Could not connect or failed to check the website: {e}")
    except Exception as e:
        print(f"  -> An unexpected error occurred: {e}")

def main():
    print("=====================================================")
    print("Starting Pan-India Pharma Job Check V4.0 (Homepage)")
    for site in SITES_TO_CHECK:
        check_site(site)
    print("\n=====================================================")
    print("All sites checked. Script finished.")

if __name__ == "__main__":
    main()
