# =========================================================================
# == FINAL, SCALABLE PHARMA JOB CHECKER SCRIPT V5.0 (with Memory)        ==
# =========================================================================
import requests
from bs4 import BeautifulSoup
import os
import json
import urllib3
from datetime import datetime

# Suppress SSL warnings for specific sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
MEMORY_FILE = 'sent_notices.json'

KEYWORDS = ['pharmacist', 'pharma', 'pharmacy', 'b.pharm', 'd.pharm', 'drug inspector', 'recruitment', 'vacancy', 'career']

SITES_TO_CHECK = [
    # ... (Your list of sites remains the same)
    { 'name': 'PCI Homepage', 'url': 'https://www.pci.nic.in/', 'base_url': 'https://www.pci.nic.in', 'verify_ssl': True },
    { 'name': 'AIIMS Delhi Homepage', 'url': 'https://www.aiims.edu/', 'base_url': 'https://www.aiims.edu', 'verify_ssl': True },
    { 'name': 'AIIMS Bhubaneswar Homepage', 'url': 'https://aiimsbhubaneswar.nic.in/', 'base_url': 'https://aiimsbhubaneswar.nic.in', 'verify_ssl': True },
    { 'name': 'NIPER Guwahati Homepage', 'url': 'https://niperguwahati.ac.in/', 'base_url': 'https://niperguwahati.ac.in', 'verify_ssl': True },
    { 'name': 'RRB Bhopal Homepage', 'url': 'https://www.rrbbpl.nic.in/', 'base_url': 'https://www.rrbbpl.nic.in', 'verify_ssl': False }
]
# --- END OF CONFIGURATION ---

def load_sent_notices():
    """Loads the memory of sent notice links from the JSON file."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set() # Return empty set if file is corrupt or empty
    return set()

def save_sent_notices(sent_links):
    """Saves the updated memory of sent links to the JSON file."""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(list(sent_links), f, indent=2)

def send_telegram_message(message):
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = { 'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'disable_web_page_preview': True }
    try:
        response = requests.post(send_url, data=payload, timeout=10)
        response_json = response.json()
        if response.status_code == 200 and response_json.get('ok'):
            print("  -> Telegram API confirmed successful delivery.")
            return True
        else:
            print(f"  -> ERROR from Telegram API: {response_json}")
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
        all_links = soup.find_all('a')
        
        if not all_links:
            print("  -> Could not find any links on the page.")
            return new_links_found

        for link_tag in all_links:
            link_text = link_tag.get_text().lower()
            if any(keyword in link_text for keyword in KEYWORDS):
                if 'href' in link_tag.attrs:
                    link = link_tag['href'].strip()
                    if not link or link.startswith('#') or link.startswith('javascript:'):
                        continue
                    if not link.startswith('http'):
                        link = f"{site['base_url'].strip('/')}/{link.lstrip('/')}"
                    
                    # THE CORE LOGIC: Check if we have sent this link before
                    if link not in sent_notices:
                        title_text = ' '.join(link_tag.get_text().strip().split())
                        message = (f"🔔 New Pharma Alert from {site['name']}!\n\n"
                                   f"Link Text: {title_text}\n\n"
                                   f"URL: {link}")
                        
                        if send_telegram_message(message):
                            print(f"  -> New notice found and sent: {link}")
                            new_links_found.append(link) # Add to list of newly sent links
        
        if not new_links_found:
            print("  -> No new links found matching keywords.")

    except Exception as e:
        print(f"  -> An error occurred while checking the site: {e}")
    
    return new_links_found

def main():
    print("=====================================================")
    print(f"Starting Job Check V5.0 at {datetime.now().isoformat()}")
    
    sent_notices = load_sent_notices()
    initial_count = len(sent_notices)
    
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
