# ShopTrack

ShopTrack is an inventory manager for small shops. The repository includes a Flask web app and a Windows desktop build.

## Features

- Inventory dashboard and item search
- Add, edit, delete, and update stock
- Low stock alerts and suggested reorder quantities
- Supplier information and order history, with receive and cancel actions that update stock
- SQLite storage for local use
- Separate shop accounts with hashed passwords and isolated inventory/order data
- CSRF protection, low stock tracking, and inventory/order CSV export

## Web app

The web preview is hosted at [shoptrack-tg2e.onrender.com](https://shoptrack-tg2e.onrender.com). The first request can take about a minute after the free service wakes up.

Create an account from the app. Each shop gets its own sign-in and separate inventory and order history.

Run locally on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY = "choose-a-long-random-secret"
python app.py
```

Open http://127.0.0.1:5000 and create a shop account.

## Render setup

Set a strong `SECRET_KEY` as a secret environment variable, and set `SESSION_COOKIE_SECURE=true`. `SHOPTRACK_DATABASE` selects the SQLite file path. Account records use that database; each shop's inventory and orders are stored in a separate database file alongside it.

The current free Render web service uses an ephemeral filesystem. Account and shop data can be lost on spin-down, restart, or redeploy. The app offers separate inventory and order CSV exports, but they do not back up accounts. There is no email verification or password recovery yet. Before inviting shops to rely on it for business records, connect durable database/storage and create a backup/restore plan. Treat the free hosted app as a pilot.

## Windows desktop app

Download the `ShopTrack.exe` asset from the GitHub release page. The desktop build stores its working database under `%LOCALAPPDATA%\ShopTrack\shoptrack.db`.


