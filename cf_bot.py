import sys
import discord
from discord.ext import commands, tasks
import requests
import json
import os
import time
from datetime import datetime
import os

# ================== CONFIG ==================

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CONTEST_CHANNEL_ID = 1455296598887108853

CF_API_USER = "https://codeforces.com/api/user.info?handles={}"
CF_API_CONTESTS = "https://codeforces.com/api/contest.list"
ATCODER_API = "https://kenkoooo.com/atcoder/resources/contests.json"
CODECHEF_API = "https://www.codechef.com/api/list/contests/all"

USERS_FILE = "cf_users.json"
CF_CONTESTS_FILE = "seen_cf.json"
ATCODER_FILE = "seen_atcoder.json"
CODECHEF_FILE = "seen_codechef.json"

# ================== DISCORD SETUP ==================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================== CF ROLE MAPPING (FIXED) ==================

CF_ROLES = [
    (0, 1199, "newbie"),
    (1200, 1399, "pupil"),
    (1400, 1599, "specialist"),
    (1600, 1899, "expert"),
    (1900, 2199, "candidate master"),
    (2200, 2399, "master"),
    (2400, 99999, "grandmaster"),
]

CF_ROLE_NAMES = [r[2] for r in CF_ROLES]

# ================== STORAGE ==================

def load_json(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

cf_users = load_json(USERS_FILE, {})
seen_cf = set(load_json(CF_CONTESTS_FILE, []))
seen_atcoder = set(load_json(ATCODER_FILE, []))
seen_codechef = set(load_json(CODECHEF_FILE, []))

# ================== HELPERS ==================

def role_from_rating(rating):
    for lo, hi, name in CF_ROLES:
        if lo <= rating <= hi:
            return name
    return "newbie"

def fetch_cf_user(handle):
    try:
        r = requests.get(CF_API_USER.format(handle), timeout=10).json()
        if r["status"] != "OK":
            return None
        return r["result"][0]
    except Exception:
        return None

# ================== EVENTS ==================

@bot.event
async def on_ready():
    print(f"✅ Bot online as {bot.user}")
    refresh_roles.start()
    check_contests.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

# ================== COMMANDS ==================

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def cf(ctx, handle: str):
    user = fetch_cf_user(handle)
    if not user:
        await ctx.send("❌ Invalid Codeforces handle")
        return

    rating = user.get("rating", 0)
    role_name = role_from_rating(rating)

    guild = ctx.guild
    member = ctx.author

    role = None
    for r in guild.roles:
        if r.name.lower() == role_name:
            role = r
            break

    if not role:
        await ctx.send(f"❌ Role `{role_name}` not found.")
        return

    for r in member.roles:
        if r.name.lower() in CF_ROLE_NAMES:
            await member.remove_roles(r)

    await member.add_roles(role)

    cf_users[str(member.id)] = handle
    save_json(USERS_FILE, cf_users)

    await ctx.send(
        f"🎉 **{handle}** linked!\n"
        f"Rating: **{rating}**\n"
        f"Role: **{role_name}**"
    )

# ================== AUTO ROLE REFRESH ==================

@tasks.loop(hours=6)
async def refresh_roles():
    for guild in bot.guilds:
        for uid, handle in cf_users.items():
            member = guild.get_member(int(uid))
            if not member:
                continue

            user = fetch_cf_user(handle)
            if not user:
                continue

            role_name = role_from_rating(user.get("rating", 0))

            for r in member.roles:
                if r.name.lower() in CF_ROLE_NAMES and r.name.lower() != role_name:
                    await member.remove_roles(r)

            for r in guild.roles:
                if r.name.lower() == role_name and r not in member.roles:
                    await member.add_roles(r)

# ================== CONTEST NOTIFIER ==================

@tasks.loop(minutes=5)
async def check_contests():
    channel = bot.get_channel(CONTEST_CHANNEL_ID)
    if not channel:
        return

    # ---- Codeforces ----
    try:
        r = requests.get(CF_API_CONTESTS, timeout=10).json()
        for c in r["result"]:
            if c["phase"] != "BEFORE":
                continue
            if c["id"] in seen_cf:
                continue

            seen_cf.add(c["id"])
            save_json(CF_CONTESTS_FILE, list(seen_cf))

            embed = discord.Embed(
                title="📢 New Codeforces Contest!",
                description=c["name"],
                color=0x2B6BFF
            )
            embed.add_field(name="🕒 Start", value=f"<t:{c['startTimeSeconds']}:F>")
            embed.add_field(name="🔗 Link", value="https://codeforces.com/contests")
            await channel.send(embed=embed)
    except Exception:
        pass

    # ---- AtCoder ----
    try:
        now = int(time.time())
        contests = requests.get(ATCODER_API, timeout=10).json()
        for c in contests:
            if c["start_epoch_second"] < now:
                continue
            if c["id"] in seen_atcoder:
                continue

            seen_atcoder.add(c["id"])
            save_json(ATCODER_FILE, list(seen_atcoder))

            embed = discord.Embed(
                title="📢 New AtCoder Contest!",
                description=c["title"],
                color=0x00AA88
            )
            embed.add_field(
                name="🕒 Start",
                value=f"<t:{c['start_epoch_second']}:F>"
            )
            embed.add_field(
                name="🔗 Link",
                value=f"https://atcoder.jp/contests/{c['id']}"
            )
            await channel.send(embed=embed)
    except Exception:
        pass

    # ---- CodeChef ----
    try:
        data = requests.get(CODECHEF_API, timeout=10).json()
        for c in data.get("future_contests", []):
            cid = c["contest_code"]
            if cid in seen_codechef:
                continue

            seen_codechef.add(cid)
            save_json(CODECHEF_FILE, list(seen_codechef))

            ts = int(
                datetime.fromisoformat(
                    c["contest_start_date_iso"].replace("Z", "+00:00")
                ).timestamp()
            )

            embed = discord.Embed(
                title="📢 New CodeChef Contest!",
                description=c["contest_name"],
                color=0x964B00
            )
            embed.add_field(name="🕒 Start", value=f"<t:{ts}:F>")
            embed.add_field(
                name="🔗 Link",
                value=f"https://www.codechef.com/{cid}"
            )
            await channel.send(embed=embed)
    except Exception:
        pass

# ================== START ==================

bot.run(TOKEN)
