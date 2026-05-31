# AxiomX

AxiomX is a Python Telegram assistant bot with an optional `aiohttp` web server for uptime checks and media streaming.

## Deployment support

This repository is prepared for:

- VPS/manual Python hosting
- Railway deployment
- Heroku deployment

The same start command is used everywhere:

```bash
python -m AxiomX
```

`Procfile` exposes that command for Heroku-compatible platforms, while Railway can detect the Python app and can also use `railway.json`.

## Required environment variables

Copy `sample.env` to `.env` for local/VPS development, or add the same keys in your Railway/Heroku dashboard.

Minimum required values:

| Variable | Required | Notes |
| --- | --- | --- |
| `TOKEN` | Yes | Telegram bot token from BotFather. |
| `API_ID` | Yes | Telegram API ID from my.telegram.org. |
| `API_HASH` | Yes | Telegram API hash from my.telegram.org. |
| `DB_URL` | Yes | MongoDB connection string. |
| `DB_URL2` | No | Defaults to `DB_URL` if omitted. |
| `USER_STRING` | Optional | Required only for userbot/voice features. |
| `LOGS_CHANNEL` / `LOG_GROUP_ID` | Optional | Chat/channel for logs. |
| `IS_WEB_SUP` | Optional | Keep `True` for web server support on Railway/Heroku. |
| `WEB_URL` | Optional | Set to your deployed app URL only if you want self-ping keep-alive. |

> Never commit real tokens, MongoDB passwords, user sessions, or API keys. `sample.env` contains placeholders only.

## Railway deployment

1. Push this repository to GitHub.
2. Open Railway and create **New Project → Deploy from GitHub repo**.
3. Select this repository.
4. Add all required variables from `sample.env` in **Variables**.
5. Railway should build it as a Python/Nixpacks app. `railway.json` sets the start command to `python -m AxiomX`.
6. After deploy, open the generated domain. The `/` route should show the AxiomX landing page.
7. If you want keep-alive pings, set `WEB_URL` to the Railway public URL.

## Heroku deployment

1. Create a Heroku app.
2. Add buildpacks:
   - `heroku/python`
   - `heroku-community/apt` if native packages such as `ffmpeg` are needed.
3. Set config vars from `sample.env` in **Settings → Config Vars**.
4. Deploy from GitHub or with the Heroku CLI:

```bash
heroku git:remote -a your-heroku-app-name
git push heroku main
```

5. Scale the web dyno:

```bash
heroku ps:scale web=1
```

Heroku reads `Procfile` and starts `python -m AxiomX`.

## VPS deployment

```bash
git clone https://github.com/maanavbaby/AxiomX.git
cd AxiomX
python3 -m venv venv
. venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp sample.env .env
# edit .env with real values
python -m AxiomX
```

For long-running VPS hosting, use `systemd`, `tmux`, or `pm2` to keep the process alive.
