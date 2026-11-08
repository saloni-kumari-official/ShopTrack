# ShopTrack

ShopTrack is an inventory manager for small shops. The repository includes a Flask web app and a Windows desktop build.

## Features

- Inventory dashboard and item search
- Add, edit, delete, and update stock
- Low stock alerts and suggested reorder quantities
- Supplier information and order history
- SQLite storage for local use
- Password protection and CSRF protection for the web app when deployed

## Web app

The web preview is hosted at [shoptrack-tg2e.onrender.com](https://shoptrack-tg2e.onrender.com). The first request can take about a minute after the free service wakes up.

Demo login password: `ShopTrackDemo`. This is shared public access; anyone with the password can change the temporary demo inventory. Do not enter real business records.

Run locally on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:APP_PASSWORD = "choose-a-local-password"
$env:SECRET_KEY = "choose-a-long-random-secret"
python app.py
```

Open http://127.0.0.1:5000. Local development allows access without `APP_PASSWORD`; set it to enable the login page.

## Render setup

Set `APP_PASSWORD` and `SECRET_KEY` as secret environment variables, and set `SESSION_COOKIE_SECURE=true`. `SHOPTRACK_DATABASE` selects the SQLite file path.

The current free Render web service uses an ephemeral filesystem. SQLite changes are lost on spin-down, restart, or redeploy. Use a paid persistent disk mounted at `/var/data` and set `SHOPTRACK_DATABASE=/var/data/shoptrack.db`, or migrate to managed Postgres, before storing real business records.

## Windows desktop app

Download the `ShopTrack.exe` asset from the GitHub release page. The desktop build stores its working database under `%LOCALAPPDATA%\ShopTrack\shoptrack.db`.

