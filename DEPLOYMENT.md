# Deployment Guide

This guide explains how to host your Codeforces Discord Bot online so it stays online 24/7 and automatically updates when you merge Pull Requests.

## Prerequisites

- Your GitHub repository: [https://github.com/zonedoutdg/cf-discord-bot](https://github.com/zonedoutdg/cf-discord-bot)
- Your Discord Bot Token (from your `.env` file)

## Option 1: Railway (Recommended)

Railway is very easy to use and detects the configuration automatically.

1.  **Sign Up**: Go to [Railway.app](https://railway.app) and sign up/login with GitHub.
2.  **New Project**: Click **New Project** -> **Deploy from GitHub repo**.
3.  **Select Repo**: Choose `cf-discord-bot` from the list.
4.  **Add Variables**:
    - Click on the new project card.
    - Go to the **Variables** tab.
    - Click **New Variable**.
    - Key: `DISCORD_TOKEN`
    - Value: `(Paste your token from your local .env file)`
    - *Only you can see this value.*
5.  **Done**: Railway will automatically build and start your bot. You will see "Build Complete" and the bot will come online.

## Option 2: Render

Render has a free tier for web services, but for a bot (Background Worker), you might need a paid plan or use their "Background Worker" service type.

1.  **Sign Up**: Go to [Render.com](https://render.com).
2.  **New Web Service**: Click **New +** -> **Background Worker**.
3.  **Connect GitHub**: Connect your account and select `cf-discord-bot`.
4.  **Settings**:
    - **Runtime**: Python 3
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `python3 cf_bot.py`
5.  **Environment**:
    - Scroll down to "Environment Variables".
    - Add `DISCORD_TOKEN` with your token value.
6.  **Deploy**: Click **Create Web Service**.

## Continuous Deployment

Once set up, whenever you or anyone else opens a Pull Request to your repository:
1.  You review the code on GitHub.
2.  You click "Merge Pull Request".
3.  Railway/Render will detect the change to the `main` branch.
4.  It will automatically redeploy the new version of the bot within a minute.
