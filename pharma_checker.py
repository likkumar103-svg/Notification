# =========================================================================================
# == FINAL, SCALABLE PHARMA JOB CHECKER SCRIPT V6.2 (Single-Target Mode for PCI)         ==
# =========================================================================================
import requests
from bs4 import BeautifulSoup
import os
import json
import urllib3
from datetime import datetime

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
MEMORY_FILE = 'sent_notices.json'

KEYWORDS = ['pharmacist', 'pharma', 'pharmacy', 'b.pharm', 'd.pharm', 'drug inspector', 'recruitment', 'vacancy', 'career']

# --- YOUR CONTROL PANEL: FOCUSED ON A SINGLE, CORRECT WEBSITE ---
SITES_TO_CHECK = [
    { 
        'name': 'PCI (Circulars)',
        'url': 'https://pci.gov.in/en/blog/?category=Circulars', # The only URL we are checking
        'base_url': 'https://pci.gov.in',
        'find_all_selector': 'div', # This page uses 'div' for its main post containers
        'verify_ssl': True 
    }
]
# --- END OF CONFIGURATION ---

def load_sent_notices():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            try: return set(json.load(f))
            except json.JSONDecodeError: return set()
    return set()

def save_sent_notices(sent_links):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(list(sent_links), f, indent=2)

def send_telegram_message(message):
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = { 'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'disable_web_page_preview': True }
    try:
        response = requests.post(send_url, data=payload, timeout=10).json()
        if response.get('ok'):
            print("  -> Telegram API confirmed successful delivery.")
            return True
        else:
            print(f"  -> ERROR from Telegram API: {response}")
            return False
    except Exception as e:
        print(f"  -> CRITICAL ERROR sending message: {e}")
        return False

def check_site(site, sent_notices):
    print(f"\nChecking site: {site['name']} ({site['url']})")
    new_links_found = []
    try:
        response = requests.get(site['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=20, verify=site['verify_ssl'])
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_items = soup.find_all(site['find_all_selector'])
        
        if not all_items:
            print("  -> No items found with the selector. The website structure might have changed.")
            return new_links_found

        for item in all_items:
            item_text = item.get_text().lower()
            if any(keyword in item_text for keyword in KEYWORDS):
                link_tag = item.find('a')
                if not link_tag: link_tag = item if item.name == 'a' else None
                
                if link_tag and 'href' in link_tag.attrs:
                    link = link_tag['href'].strip()
                    if not link or link.startswith('#') or link.startswith('javascript:'): continue
                    if not link.startswith('http'): link = f"{site['base_url'].strip('/')}/{link.lstrip('/')}"
                    
                    if link not in sent_notices:
                        title_text = ' '.join(item.get_text().strip().split())
                        message = (f"🔔 New Pharma Alert from {site['name']}!\n\n"
                                   f"Title: {title_text}\n\n"
                                   f"URL: {link}")
                        
                        if send_telegram_message(message):
                            print(f"  -> New notice found and sent: {link}")
                            new_links_found.append(link)
        
        if not new_links_found:
            print("  -> No new links found matching keywords.")

    except requests.exceptions.RequestException as e:
        print(f"  -> Site check failed: {e}")
        error_message = (f"⚠️ Site Error: {site['name']}!\n\n"
                         f"Could not connect to the website. The URL might be broken or the site is down.\n\n"
                         f"URL: {site['url']}\n"
                         f"Details: {e}")
        send_telegram_message(error_message)
    
    return new_links_found

def main():
    print("=====================================================")
    print(f"Starting Job Check V6.2 (Single-Target) at {datetime.now().isoformat()}")
    sent_notices = load_sent_notices()
    all_new_links = []
    for site in SITES_TO_CHECK:
        newly_found = check_site(site, sent_notices)
        all_new_links.extend(newly_found)
    
    if all_new_links:
        sent_notices.update(all_new_links)
        save_sent_notices(sent_notices)
        print(f"\nMemory updated. Total notices tracked: {len(sent_notices)}")
    else:
        print("\nNo new notices found across all sites. Memory file is unchanged.")
    print("=====================================================")

if __name__ == "__main__":
    main()
