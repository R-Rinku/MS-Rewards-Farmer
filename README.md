# Microsoft Rewards Farmer 🌾

An automated desktop bot for completing Microsoft Rewards tasks, daily sets, and Bing search quotas with human-like interactions.

> **Credits & Acknowledgements:**  
> This project is originally created and maintained by **[Carl Furtado (User0332)](https://github.com/User0332)**.  
> Original repository: **[User0332/rewards-farmer](https://github.com/User0332/rewards-farmer)**  
> Technique explanation and original video guide: **[YouTube Video](https://youtu.be/4qdPcMNaioA)**.  
> Full credit goes to Carl Furtado for the core automation architecture, anti-detection techniques, and Bezier mouse movement modeling.

---

## ⚡ Quick Start (Ready in 2 Minutes)

No complex setup, no local AI models, and no API keys required.

### 1. Prerequisites
- **Python 3.10+**
- **Microsoft Edge** browser installed on your computer

### 2. Clone and Install
Clone this repository and install the lightweight requirements:

```sh
git clone https://github.com/R-Rinku/MS-Rewards-Farmer.git
cd MS-Rewards-Farmer
pip install -r requirements.txt
```

*(Alternatively, if you use Poetry: `poetry install`)*

### 3. One-Time Sign-In & Automatic Validation
The bot automatically detects if your profile is signed in to Microsoft Rewards:

1. **First run (Visible mode):**
   ```sh
   python src/main.py
   ```
2. Edge opens `https://rewards.bing.com/`. The bot automatically detects that the profile is not yet signed in and prompts:
   ```text
   [SIGN-IN REQUIRED] Microsoft Rewards profile is not signed in.
   Please sign in to your Microsoft account in the opened Edge browser window.
   Waiting for sign-in... (will automatically continue once you sign in)
   ```
3. Sign in to your Microsoft account in Edge.
4. As soon as you log in, the bot detects your authenticated session automatically (`[AUTH SUCCESS]`), saves your session cookies securely in `data-dir/`, and begins completing tasks immediately.

**You only ever have to log in once.** For all future runs (including background `--headless` runs), the bot recognizes your saved profile automatically without asking again. If your session ever expires in the future, it safely informs you to re-authenticate instead of failing silently.

### 4. Run the Bot

Run the bot anytime directly from the project root:

```sh
# Normal run (visible browser window)
python src/main.py

# Headless run (silent background mode, no popups)
python src/main.py --headless
```

---

## 🔍 How Search Queries Work (Zero AI Required by Default)

The bot needs realistic queries to type into Bing to fulfill the daily search quota.

By default, the bot uses the **`trends`** backend:
- Fetches **live trending searches** from Google Trends RSS.
- Expands queries using **Bing's OpenSearch Autosuggest API** (real terms Bing natively expects).
- Uses Wikipedia featured topics and words from `nouns.txt` as resilient fallbacks.
- **100% keyless, instant, and requires zero external AI services.**

### Query Backend Options

You can specify the query source with `--source` or the `QUERY_SOURCE` environment variable:

| Source | Requirements | Description |
| :--- | :--- | :--- |
| **`trends`** *(Default)* | **None** (Standard Library) | Live Google Trends, Bing Autosuggest, and Wikipedia topics. Fast, authentic, and zero configuration. |
| **`llm`** *(Optional)* | Ollama CLI + `gemma4:cloud` | Generates queries using a local or cloud Ollama model. |

```sh
# Run with keyless trends (default)
python src/main.py --source trends

# Run with Ollama (if configured)
python src/main.py --source llm
```

---

## ⚙️ Command-Line Options

You can configure runs directly via flags or environment variables:

| Flag | Env Variable | Default | Description |
| :--- | :--- | :--- | :--- |
| `--headless` | `REWARDS_HEADLESS=1` | `False` | Run Edge invisibly in the background. |
| `--source` | `QUERY_SOURCE` | `trends` | Query backend: `trends` (default) or `llm`. |
| `--accounts` | `REWARDS_ACCOUNTS` | `default` | Comma-separated list of profile accounts to cycle through. |

```sh
# View all CLI arguments
python src/main.py --help
```

---

## 👥 Multi-Account Support

You can farm points across multiple Microsoft accounts in a single run. Each account uses an isolated profile under `data-dir/`:

1. Sign in to each account once:
   ```sh
   # On Windows:
   msedge --user-data-dir="%cd%\data-dir\personal" --profile-directory=Default https://rewards.bing.com
   msedge --user-data-dir="%cd%\data-dir\spare" --profile-directory=Default https://rewards.bing.com
   ```
2. Run all accounts sequentially:
   ```sh
   python src/main.py --accounts personal,spare --headless
   ```

If one account encounters an issue, the bot safely logs the error and continues to the remaining accounts.

---

## 🖼️ Visual Search Image

Microsoft Rewards occasionally offers visual search bonus points. If you want to enable this task:

```sh
python src/random_image_for_visual_search.py
```

This helper script downloads a safe sample image (`visual_search.jpg`) into the root directory. If omitted, the visual search task is safely skipped while all other tasks continue normally.

---

## 🐳 Docker Support

If you prefer running in a container without local Edge drivers:

```sh
docker compose build
docker compose run --rm rewards-farmer
```

*(Note: On Windows hosts, direct local execution `python src/main.py` is recommended because Windows DPAPI cookie encryption cannot be read inside Linux containers.)*

---

## 🛠️ Logging & Debugging

The bot logs task status cleanly to the console. You can increase verbosity or redirect to a log file:

```sh
# PowerShell:
$env:REWARDS_FARMER_LOG_LEVEL="DEBUG"; $env:REWARDS_FARMER_LOG_FILE="run.log"; python src/main.py

# Linux / macOS Bash:
REWARDS_FARMER_LOG_LEVEL=DEBUG REWARDS_FARMER_LOG_FILE=run.log python src/main.py
```

---

## ⚠️ Disclaimer

Use at your own risk. Automated scripts may violate Microsoft Rewards Terms of Service. This tool is provided for educational and research purposes.
