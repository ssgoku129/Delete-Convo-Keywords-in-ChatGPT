import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json

# ── CONFIG ─────────────────────────────────────────────────────────────────────
KEYWORD           = "test"       # <-- Change this to the keyword you want to delete
DRY_RUN           = False        # Set to True to preview matches without deleting
CHROMEDRIVER_PATH = "chromedriver.exe"  # Path to your chromedriver executable
# ──────────────────────────────────────────────────────────────────────────────

opts = webdriver.ChromeOptions()
opts.add_argument("--start-maximized")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option("useAutomationExtension", False)
opts.add_argument("--disable-blink-features=AutomationControlled")

service = Service(CHROMEDRIVER_PATH)
driver  = webdriver.Chrome(service=service, options=opts)
wait    = WebDriverWait(driver, 15)


def get_search_results():
    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Search chats')]")))
    search_btn.click()
    time.sleep(1.5)

    search_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder,'Search')]")))
    search_input.click()
    time.sleep(0.3)
    search_input.send_keys(KEYWORD)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//a[contains(@href,'/c/')]")))
        time.sleep(0.5)
    except Exception:
        search_input.send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        return []

    modal = driver.find_element(By.XPATH, "//div[@role='dialog']")
    links = modal.find_elements(By.XPATH, ".//a[contains(@href,'/c/')]")

    urls = []
    seen = set()
    for r in links:
        href = r.get_attribute("href")
        if href and "/c/" in href and href not in seen:
            seen.add(href)
            urls.append(href.split("?")[0])

    search_input.send_keys(Keys.ESCAPE)
    time.sleep(0.8)
    return urls


def get_token_from_session():
    """Get bearer token from the /api/auth/session endpoint."""
    driver.get("https://chatgpt.com/api/auth/session")
    time.sleep(2)
    try:
        body = driver.find_element(By.TAG_NAME, "body").text
        data = json.loads(body)
        return data.get("accessToken")
    except Exception as e:
        print("Session parse error: {}".format(e))
        return None


def delete_chat_via_api(chat_id, token):
    """
    ChatGPT uses PATCH with is_visible=false to 'delete' (hide) a conversation.
    Endpoint: /backend-api/conversation/<id>
    """
    result = driver.execute_script("""
        var chat_id = arguments[0];
        var token = arguments[1];
        var xhr = new XMLHttpRequest();
        xhr.open('PATCH', 'https://chatgpt.com/backend-api/conversation/' + chat_id, false);
        xhr.setRequestHeader('Authorization', 'Bearer ' + token);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({is_visible: false}));
        return {status: xhr.status, response: xhr.responseText};
    """, chat_id, token)
    return result


# ── main ──────────────────────────────────────────────────────────────────────
driver.get("https://chatgpt.com")
input("Log in manually, wait until your chat list fully loads, then press ENTER...")

print("Getting access token from session...")
token = get_token_from_session()
if not token:
    print("ERROR: Could not get access token.")
    driver.quit()
    raise SystemExit(1)

print("Got token: {}...".format(token[:20]))

# Go back to main page for searching
driver.get("https://chatgpt.com")
time.sleep(2)

all_deleted = 0
all_skipped = 0
round_num   = 0

while True:
    round_num += 1
    print("\n=== Round {} ===".format(round_num))

    chat_urls = get_search_results()
    if not chat_urls:
        print("No more chats found. Done!")
        break

    print("Found {} chat(s):".format(len(chat_urls)))
    for u in chat_urls:
        print("  " + u)

    if DRY_RUN:
        print("DRY-RUN — not deleting.")
        break

    round_deleted = 0
    for i, url in enumerate(chat_urls, 1):
        chat_id = url.rstrip("/").split("/c/")[-1]
        print("[{}/{}] Deleting {}...".format(i, len(chat_urls), chat_id))
        try:
            result = delete_chat_via_api(chat_id, token)
            status   = result.get("status")   if result else None
            response = result.get("response", "") if result else ""
            print("  status={} body={}".format(status, response[:80]))
            if status in (200, 204):
                print("[{}/{}] Deleted.".format(i, len(chat_urls)))
                round_deleted += 1
                all_deleted   += 1
            else:
                print("[{}/{}] Unexpected status: {}".format(i, len(chat_urls), status))
                all_skipped += 1
        except Exception as e:
            print("[{}/{}] Skipped - {}".format(i, len(chat_urls), e))
            traceback.print_exc()
            all_skipped += 1
        time.sleep(0.3)

    if round_deleted == 0:
        print("Nothing deleted this round — stopping.")
        break

print("\nAll done. Deleted: {}  Skipped: {}".format(all_deleted, all_skipped))
driver.quit()
