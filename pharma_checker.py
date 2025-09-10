# =================================================================
# == FINAL, SCALABLE PHARMA JOB CHECKER SCRIPT V2.0              ==
# =================================================================
import requests
from bs4 import BeautifulSoup
import telegram
import time
import os

# --- CONFIGURATION ---
# Your secrets are loaded securely from GitHub Actions environment variables
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# Keywords to look for in any notice
KEYWORDS = ['pharmacist', 'pharma', 'pharmacy', 'b.pharm', 'd.pharm', 'drug inspector']

# --- YOUR CONTROL PANEL: ADD/REMOVE WEBSITES HERE ---
# 'name': A friendly name for notifications.
# 'url': The full URL of the recruitment/notices page.
# 'base_url': The main domain, used to build full links if necessary.
# 'find_all_selector': The HTML tag that usually contains each notice item (e.g., 'tr' for table rows, 'li' for list items).
SITES_TO_CHECK = [
    {
        'name': 'PCI (Announcements)',
        'url': 'https://www.pci.nic.in/Announcements.html',
        'base_url': 'https://www.pci.nic.in',
        'find_all_selector': 'li'
    },
    {
        'name': 'AIIMS Delhi (Recruitment)',
        'url': 'https://www.aiims.edu/en/notices/recruitment/aiims-recruitment.html',
        'base_url': 'https://www.aiims.edu',
        'find_all_selector': 'tr'
    },
    {
        'name': 'AIIMS Bhubaneswar',
        'url': 'https://aiimsbhubaneswar.nic.in/advertisement/',
        'base_url': 'https://aiimsbhubaneswar.nic.in',
        'find_all_selector': 'tr'
    },
    {
        'name': 'NIPER Guwahati',
        'url': 'https://niperguwahati.ac.in/recruitment.php',
        'base_url': 'https://niperguwahati.ac.in',
        'find_all_selector': 'tr'
    },
    {
        'name': 'RRB Bhopal (Paramedical)',
        'url': 'https://www.rrbbpl.nic.in/paramedical-cat.htm',
        'base_url': 'https://www.rrbbpl.nic.in',
        'find_all_selector': 'tr'
    }
]
# --- END OF CONFIGURATION ---

def send_telegram_message(message):
    """Sends a formatted message to your Telegram bot."""
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML', disable_web_page_preview=True)
        print("  -> Notification sent successfully.")
    except Exception as e:
        print(f"  -> Error sending Telegram message: {e}")

def check_site(site):
    """Checks a single website for keywords and sends notifications."""
    print(f"\nChecking site: {site['name']} ({site['url']})")
    try:
        response = requests.get(site['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        notices = soup.find_all(site['find_all_selector'])
        
        if not notices:
            print("  -> No items found with the selector. The website structure might have changed.")
            return

        new_notices_found = 0
        for notice in notices:
            notice_text = notice.get_text().lower()
            if any(keyword in notice_text for keyword in KEYWORDS):
                link_tag = notice.find('a')
                if link_tag and 'href' in link_tag.attrs:
                    link = link_tag['href'].strip()
                    
                    if not link.startswith('http'):
                        link = f"{site['base_url'].strip('/')}/{link.lstrip('/')}"
                    
                    # Note: This version will notify for all found items on every run.
                    # Preventing duplicates requires a more complex setup to store sent links.
                    new_notices_found += 1
                    title_text = ' '.join(notice.get_text().strip().split())
                    message = (f"🚨 <b>Pharma Alert from {site['name']}!</b>\n\n"
                               f"<b>Title:</b> {title_text}\n"
                               f"<b>Link:</b> <a href='{link}'>Click Here to View</a>")
                    send_telegram_message(message)
        
        if new_notices_found == 0:
            print("  -> No notices found matching keywords.")

    except requests.exceptions.RequestException as e:
        print(f"  -> Could not connect to the website: {e}")
    except Exception as e:
        print(f"  -> An error occurred while checking the site: {e}")

def main():
    """Main function to loop through all sites defined in the configuration."""
    print("=========================================")
    print("Starting Pan-India Pharma Job Check...")
    for site in SITES_TO_CHECK:
        check_site(site)
    print("\n=========================================")
    print("All sites checked. Script finished.")

if __name__ == "__main__":
    main()
