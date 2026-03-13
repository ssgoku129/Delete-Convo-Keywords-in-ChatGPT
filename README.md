A Python script that automatically finds and deletes every ChatGPT conversation containing a specific keyword. It works by driving a real Chrome browser session (via Selenium) using your own logged-in account, then calling ChatGPT's internal API to delete each matched conversation.

---

## Why would you want to do this?

### Privacy and Data Security

ChatGPT stores your conversation history on OpenAI's servers. If you have ever typed sensitive information into a conversation, such as a company name, a project codename, a person's name, a password, a client's details, or proprietary code, that information sits in OpenAI's systems and may be used to train future models (depending on your account settings).

If you realise you've had dozens or hundreds of conversations mentioning something sensitive, deleting them one by one manually is not realistic. This script lets you wipe them all out in a single automated run.

### Common scenarios where this matters

- **Work / NDA situations:** You used ChatGPT to help with work tasks and mentioned a client name, internal project name, or proprietary details that shouldn't be in a third-party system.
- **Personal information:** You asked for advice and used real names, addresses, or other personally identifiable information (PII).
- **Password or credential exposure:** You pasted config files or code that contained secrets, API keys, or credentials.
- **Business confidentiality:** Strategy, financials, unreleased product names, or other commercially sensitive topics were discussed.
- **General hygiene:** You simply want a clean slate and don't want years of conversations on OpenAI's servers.

---

## Important caveat about ChatGPT's search

This script is only as good as ChatGPT's own search function, because that is what it uses to find conversations. **ChatGPT's built-in search is known to be unreliable and incomplete.** If you search for a keyword manually on the ChatGPT website, you will notice it does not return every conversation that contains that word. This is a limitation of OpenAI's search indexing, not of this script. The script faithfully deletes every result that ChatGPT's search returns, but if ChatGPT's search misses conversations, those will not be deleted. There is nothing this script (or any script using the same search endpoint) can do about that.

---

## Requirements

- **Python 3.8 or newer**
- **Google Chrome** installed on your machine
- **ChromeDriver** matching your Chrome version (see below)
- The `selenium` Python package

---

## Installation

### 1. Install Python

Download and install Python 3.8+ from https://www.python.org/downloads/

During installation on Windows, check the box that says **"Add Python to PATH"**.

Verify it works by opening a terminal / command prompt and running:

```
python --version
```

### 2. Install Selenium

Open a terminal / command prompt and run:

```
pip install selenium
```

### 3. Download ChromeDriver

ChromeDriver is a separate executable that lets Python control your Chrome browser. It must match your installed version of Chrome.

**Step 1 - Check your Chrome version:**
- Open Chrome
- Click the three-dot menu (top right) > Help > About Google Chrome
- Note the version number (e.g. `124.0.6367.82`)

**Step 2 - Download the matching ChromeDriver:**
- Go to https://googlechromelabs.github.io/chrome-for-testing/
- Find the entry that matches your Chrome version
- Download the `chromedriver` zip for your operating system (`win64` for 64-bit Windows, `mac-x64` or `mac-arm64` for Mac, `linux64` for Linux)

**Step 3 - Place the file:**
- Extract the zip
- On **Windows**: place `chromedriver.exe` in the same folder as the script
- On **Mac/Linux**: place `chromedriver` (no extension) in the same folder as the script, then make it executable:
  ```
  chmod +x chromedriver
  ```

> **Mac/Linux users:** Also update the `CHROMEDRIVER_PATH` line in the script. See the configuration section below.

---

## Configuration

Open `delete_convo_keyword.py` in any text editor and look for the CONFIG section near the top:

```python
KEYWORD           = "test"              # <-- Change this
DRY_RUN           = False               # <-- Set to True to preview only
CHROMEDRIVER_PATH = "chromedriver.exe"  # <-- Change if on Mac/Linux
```

### KEYWORD

Change `"test"` to whatever word or phrase you want to search for and delete. For example:

```python
KEYWORD = "Acme Corp"
```

The script will delete every conversation that ChatGPT's search returns for that keyword.

### DRY_RUN

Set this to `True` if you want to do a test run. The script will find and print matching conversations but will **not** delete anything. Useful for checking what would be deleted before you commit.

```python
DRY_RUN = True
```

### CHROMEDRIVER_PATH

- **Windows:** leave it as `"chromedriver.exe"` if the file is in the same folder as the script.
- **Mac/Linux:** change it to `"./chromedriver"` (or the full path if it is somewhere else).

```python
CHROMEDRIVER_PATH = "./chromedriver"
```

---

## Usage

1. Open a terminal / command prompt in the folder containing the script.

2. Run the script:

   **Windows:**
   ```
   python delete_convo_keyword.py
   ```

   **Mac/Linux:**
   ```
   python3 delete_convo_keyword.py
   ```

3. A Chrome browser window will open and navigate to ChatGPT.

4. **Log in to your ChatGPT account manually** in that browser window.

   **Heads up:** Because of the way ChromeDriver launches Chrome (with bot-detection disabled), ChatGPT's login flow can be a bit temperamental. You may find yourself needing to go through the login steps up to 3 times before it fully accepts your session and lands you on the main chat page. This is normal, just keep going until you're in. Once you can see your full conversation list in the sidebar, you're good.

5. Switch back to the terminal and press **ENTER**.

6. The script will:
   - Grab your session token automatically
   - Search for the keyword using ChatGPT's search
   - Delete each matching conversation via the API
   - Repeat until no more results are found

7. When it finishes, it will print a summary:
   ```
   All done. Deleted: 42  Skipped: 0
   ```

---

## How it works

1. Opens Chrome with automation-detection flags disabled so ChatGPT loads normally.
2. Waits for you to log in manually (avoiding the need to store credentials anywhere).
3. Fetches your session bearer token from ChatGPT's `/api/auth/session` endpoint.
4. Uses ChatGPT's search UI to find conversations matching the keyword.
5. Calls the internal `PATCH /backend-api/conversation/<id>` endpoint with `{"is_visible": false}` for each result. This is the same action ChatGPT uses when you delete a conversation manually.
6. Loops and searches again until no more results appear.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `chromedriver` error on startup | Make sure your ChromeDriver version matches your Chrome version exactly. |
| Login keeps failing or looping | This can happen due to how ChromeDriver launches Chrome. Keep trying until it accepts your credentials and loads the chat list, it usually goes through within 3 attempts. |
| Script can't find the search button | ChatGPT may have updated its UI. Try running it again or open an issue. |
| Token error | Make sure you are fully logged in and your chat list has loaded before pressing ENTER. |
| Some conversations not found | This is a ChatGPT search limitation, not a bug in the script. See the caveat section above. |
| Mac: "cannot be opened because the developer cannot be verified" | Run `xattr -d com.apple.quarantine chromedriver` in the terminal. |

---

## License

MIT - do whatever you like with it.
