import discord
from discord.ext import commands, tasks
import requests
import json
import os

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1455296598887108853  # <-- replace with your #cf-contests channel ID
DATA_FILE = "seen_contests.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

CF_API = "https://codeforces.com/api/contest.list"

# ---------- utility ----------
def load_seen():
    if not os.path.exists(DATA_FILE):
        return set()
    with open(DATA_FILE, "r") as f:
        return set(json.load(f))

def save_seen(seen):
    with open(DATA_FILE, "w") as f:
        json.dump(list(seen), f)

seen_contests = load_seen()

# ---------- bot events ----------
@bot.event
async def on_ready():
    print(f"✅ Contest notifier online as {bot.user}")
    check_contests.start()

# ---------- background task ----------
@tasks.loop(minutes=5)
async def check_contests():
    global seen_contests

    try:
        r = requests.get(CF_API, timeout=10).json()
        if r["status"] != "OK":
            return
    except Exception:
        return

    contests = r["result"]
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    for contest in contests:
        # We only want UPCOMING contests
        if contest["phase"] != "BEFORE":
            continue

        contest_id = contest["id"]
        if contest_id in seen_contests:
            continue

        seen_contests.add(contest_id)
        save_seen(seen_contests)

        name = contest["name"]
        start_time = contest["startTimeSeconds"]
        duration = contest["durationSeconds"] // 3600

        embed = discord.Embed(
            title="📢 New Codeforces Contest Announced!",
            description=f"**{name}**",
            color=0x2B6BFF
        )

        embed.add_field(
            name="🕒 Start Time (UTC)",
            value=f"<t:{start_time}:F>",
            inline=False
        )

        embed.add_field(
            name="⏱ Duration",
            value=f"{duration} hours",
            inline=True
        )

        embed.add_field(
            name="🔗 Link",
            value="https://codeforces.com/contests",
            inline=False
        )

        await channel.send(embed=embed)

# ---------- start ----------
bot.run(TOKEN)
