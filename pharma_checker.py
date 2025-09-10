# =======================================================================================
# == FINAL, SCALABLE PHARMA JOB CHECKER SCRIPT V4.2 (Direct API Call Reliability Fix)  ==
# =======================================================================================
import requests
from bs4 import BeautifulSoup
import os
import urllib3

# Suppress only the single InsecureRequestWarning from a single call to verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

KEYWORDS = ['pharmacist', 'pharma', 'pharmacy', 'b.pharm', 'd.pharm', 'drug inspector', 'recruitment', 'vacancy', 'career']

# --- YOUR CONTROL PANEL: CHECKING HOME PAGES ---
SITES_TO_CHECK = [
    { 'name': 'PCI Homepage', 'url': 'https://www.pci.nic.in/', 'base_url': 'https://www.pci.nic.in', 'verify_ssl': True },
    { 'name': 'AIIMS Delhi Homepage', 'url': 'https://www.aiims.edu/', 'base_url': 'https://www.aiims.edu', 'verify_ssl': True },
    { 'name': 'AIIMS Bhubaneswar Homepage', 'url': 'https://aiimsbhubaneswar.nic.in/', 'base_url': 'https://aiimsbhubaneswar.nic.in', 'verify_ssl': True },
    { 'name': 'NIPER Guwahati Homepage', 'url': 'https://niperguwahati.ac.in/', 'base_url': 'https://niperguwahati.ac.in', 'verify_ssl': True },
    { 'name': 'RRB Bhopal Homepage', 'url': 'https://www.rrbbpl.nic.in/', 'base_url': 'https://www.rrbbpl.nic.in', 'verify_ssl': False }
]
# --- END OF CONFIGURATION ---

def send_telegram_message(message):
    """Sends a message using the requests library directly, mimicking curl for maximum reliability."""
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(send_url, data=payload, timeout=10)
        response_json = response.json()
        
        # Check the actual response from Telegram's servers
        if response.status_code == 200 and response_json.get('ok'):
            print("  -> Telegram API confirmed successful delivery.")
        else:
            # This is the new, powerful error logging. It will tell us what Telegram thinks is wrong.
            print(f"  -> ERROR from Telegram API: Status Code {response.status_code} - Response: {response_json}")
            
    except Exception as e:
        print(f"  -> CRITICAL ERROR sending message via requests: {e}")

def check_site(site):
    print(f"\nChecking site: {site['name']} ({site['url']})")
    try:
        response = requests.get(site['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=20, verify=site['verify_ssl'])
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_links = soup.find_all('a')
        
        if not all_links:
            print("  -> Could not find any links on the page.")
            return

        new_notices_found = 0
        for link_tag in all_links:
            link_text = link_tag.get_text().lower()
            
            if any(keyword in link_text for keyword in KEYWORDS):
                if 'href' in link_tag.attrs:
                    link = link_tag['href'].strip()
                    if not link or link.startswith('#') or link.startswith('javascript:'):
                        continue

                    if not link.startswith('http'):
                        link = f"{site['base_url'].strip('/')}/{link.lstrip('/')}"
                    
                    new_notices_found += 1
                    title_text = ' '.join(link_tag.get_text().strip().split())
                    message = (f"Pharma Alert from {site['name']}!\n\n"
                               f"Link Text: {title_text}\n\n"
                               f"URL: {link}")
                    send_telegram_message(message)
        
        if new_notices_found == 0:
            print("  -> No links found matching keywords.")

    except requests.exceptions.RequestException as e:
        print(f"  -> Could not connect or failed to check the website: {e}")
    except Exception as e:
        print(f"  -> An unexpected error occurred: {e}")

def main():
    print("=========================================================")
    print("Starting Pan-India Pharma Job Check V4.2 (Direct API)")
    for site in SITES_TO_CHECK:
        check_site(site)
    print("\n=========================================================")
    print("All sites checked. Script finished.")

if __name__ == "__main__":
    main()
