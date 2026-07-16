# 🤖 Downloader Bot

A multi-platform media downloader Telegram bot built with **aiogram 3.x**.  
Supports downloading videos, audio, and playlists from **YouTube**, **SoundCloud**, **Instagram**, **Spotify**, and more.

---

## ✨ Features

- **Multi-platform support** – YouTube, SoundCloud, Instagram, Spotify, and others via `yt-dlp`, `instaloader`, `scdl`, `spotipy`.
- **Telegram Bot integration** – Built with `aiogram 3.17` using webhook mode.
- **Asynchronous & fast** – Powered by `asyncio` and `aiohttp`.
- **Admin controls** – Configurable admin IDs for bot management.
- **Easy deployment** – Ready for cloud hosting with webhook support.

---

## 📦 Dependencies

Key dependencies include:

| Package | Version | Purpose |
|---------|---------|---------|
| `aiogram` | 3.17.0 | Telegram Bot API framework |
| `aiohttp` | 3.11.11 | Async HTTP server for webhooks |
| `yt-dlp` | 2025.01.26 | YouTube/media downloading |
| `youtube-dl` | 2021.12.17 | Legacy YouTube downloader |
| `pytube` | 15.0.0 | YouTube downloading alternative |
| `instaloader` | 4.14.1 | Instagram content downloader |
| `scdl` | 2.12.3 | SoundCloud downloader |
| `soundcloud-v2` | 1.6.0 | SoundCloud API client |
| `spotipy` | 2.25.0 | Spotify API client |
| `redis` | 5.2.1 | Caching / state management |
| `python-dotenv` | 1.0.1 | Environment variable management |

Full list available in [`requirements.txt`](https://github.com/OkaykOrhmn/Downloader/blob/main/requirements.txt).

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/OkaykOrhmn/Downloader.git
cd Downloader
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_telegram_bot_token
```

You can obtain a token from [@BotFather](https://t.me/BotFather) on Telegram.

---

## ⚙️ Configuration

Edit `bot/config.py` to adjust bot settings:

```python
class BotConfig:
    def __init__(self, admin_ids, welcome_message, webhook_url, webhook_port):
        self.admin_ids = admin_ids          # List of admin Telegram user IDs
        self.welcome_message = welcome_message
        self.webhook_url = webhook_url      # Public URL for webhook (e.g., https://your-domain.com/webhook)
        self.webhook_port = webhook_port    # Port for the webhook server (e.g., 8443, 443, 80)
```

Example configuration in `main.py`:

```python
config = BotConfig(
    admin_ids=[1568352369, 23847983],
    welcome_message="Welcome to our Bot!",
    webhook_url="https://your-domain.com/webhook",
    webhook_port=8443,
)
```

---

## ▶️ Usage

Run the bot with:

```bash
python main.py
```

The bot will start an aiohttp web server and set the webhook for your Telegram bot.

> **Note:** For production, ensure your `webhook_url` points to a publicly accessible endpoint (e.g., using ngrok or a cloud server).

---

## 📁 Project Structure

```
Downloader/
├── bot/
│   ├── handlers/           # Message and callback handlers
│   ├── __init__.py
│   └── config.py           # Bot configuration
├── bot_instance.py         # Bot instance initialization
├── main.py                 # Entry point – webhook server setup
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python runtime version (for platforms like Heroku)
└── .env                    # Environment variables (not tracked)
```

---

## 🛠️ Tech Stack

- **Python 3.x** – Core language
- **aiogram 3.x** – Telegram Bot framework
- **aiohttp** – Async web server for webhooks
- **asyncio** – Asynchronous I/O
- **Various downloader libraries** – `yt-dlp`, `instaloader`, `scdl`, `spotipy`, etc.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to open an [issue](https://github.com/OkaykOrhmn/Downloader/issues) or submit a pull request.

---

## 👤 Author

**Kianoosh Rhmn** – [@OkaykOrhmn](https://github.com/OkaykOrhmn)

---

## ⭐ Support

If you find this project useful, please give it a star ⭐ on GitHub!
