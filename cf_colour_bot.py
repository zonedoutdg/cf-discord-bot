import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# CF roles mapping
CF_ROLES = [
    (0, 1199, "newbie"),
    (1200, 1399, "pupil"),
    (1400, 1599, "specialist"),
    (1600, 1899, "expert"),
    (1900, 2199, "Candidate Master"),
    (2200, 2399, "Master"),
    (2400, 99999, "Grandmaster"),
]

CF_ROLE_NAMES = [r[2] for r in CF_ROLES]

@bot.event
async def on_ready():
    print(f"✅ Bot online as {bot.user}")

def get_cf_role(rating):
    for lo, hi, role in CF_ROLES:
        if lo <= rating <= hi:
            return role
    return CF_ROLES[0][2]

@bot.command()
async def cf(ctx, handle: str):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    r = requests.get(url).json()

    if r["status"] != "OK":
        await ctx.send("❌ Invalid Codeforces handle")
        return

    user = r["result"][0]
    rating = user.get("rating", 0)

    role_name = get_cf_role(rating)
    guild = ctx.guild
    member = ctx.author

    role_to_add = discord.utils.get(guild.roles, name=role_name)
    if not role_to_add:
        await ctx.send("❌ Role not found. Check role names.")
        return

    # Remove old CF roles
    for role in member.roles:
        if role.name in CF_ROLE_NAMES:
            await member.remove_roles(role)

    await member.add_roles(role_to_add)

    await ctx.send(
        f"🎉 **{handle}** linked!\n"
        f"Rating: **{rating}**\n"
        f"Role: **{role_name}**"
    )

bot.run(TOKEN)
