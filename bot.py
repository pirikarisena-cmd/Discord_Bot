import os
import json
import random
import urllib.parse
from pathlib import Path

import discord
from discord import app_commands

# ===== 設定 =====
GUILD_ID = 1455898610750197974
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN が設定されていません")

# ===== Discord =====
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
GUILD = discord.Object(id=GUILD_ID)

# ===== 永続データ =====
DATA_DIR = Path("/data")
DATA_DIR.mkdir(exist_ok=True)

FAVORITE_FILE = DATA_DIR / "favorites.json"
RANDOM_FILE = DATA_DIR / "random_songs.json"

def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

favorites = load_json(FAVORITE_FILE, {})
random_songs = load_json(
    RANDOM_FILE,
    [
        "Montagem Miau",
        "Montagem Moe",
        "MEMORIES FUNK",
        "Brazilian Phonk"
    ]
)

# ===== 起動 =====
@client.event
async def on_ready():
    await tree.sync(guild=GUILD)
    print(f"✅ Logged in as {client.user}")

# ===== /spotify =====
@tree.command(name="spotify", description="音楽を横断検索", guild=GUILD)
@app_commands.describe(name="曲名")
async def spotify(interaction: discord.Interaction, name: str):
    q = urllib.parse.quote(name)
    msg = (
        f"🔍 **{name}**\n\n"
        f"Spotify\nhttps://open.spotify.com/search/{q}\n\n"
        f"YouTube Music\nhttps://music.youtube.com/search?q={q}\n\n"
        f"Apple Music\nhttps://music.apple.com/jp/search?term={q}"
    )
    await interaction.response.send_message(msg)

# ===== /randomsong =====
@tree.command(name="randomsong", description="ランダム神曲", guild=GUILD)
async def randomsong(interaction: discord.Interaction):
    song = random.choice(random_songs)
    q = urllib.parse.quote(song)
    msg = (
        f"🎲 **今日の一曲**\n\n"
        f"{song}\n\n"
        f"Spotify\nhttps://open.spotify.com/search/{q}\n\n"
        f"YouTube Music\nhttps://music.youtube.com/search?q={q}\n\n"
        f"Apple Music\nhttps://music.apple.com/jp/search?term={q}"
    )
    await interaction.response.send_message(msg)

# ===== オートコンプリート =====
async def favorite_autocomplete(interaction: discord.Interaction, current: str):
    uid = str(interaction.user.id)
    songs = favorites.get(uid, [])
    return [
        app_commands.Choice(name=s, value=s)
        for s in songs if current.lower() in s.lower()
    ][:25]

# ===== /favorite_add =====
@tree.command(name="favorite_add", description="お気に入り追加", guild=GUILD)
@app_commands.describe(name="曲名")
async def favorite_add(interaction: discord.Interaction, name: str):
    uid = str(interaction.user.id)
    favorites.setdefault(uid, [])
    if name in favorites[uid]:
        await interaction.response.send_message("⚠ 登録済み", ephemeral=True)
        return
    favorites[uid].append(name)
    save_json(FAVORITE_FILE, favorites)
    await interaction.response.send_message(f"⭐ 追加：{name}", ephemeral=True)

# ===== /favorite_remove =====
@tree.command(name="favorite_remove", description="お気に入り削除", guild=GUILD)
@app_commands.describe(name="曲名")
@app_commands.autocomplete(name=favorite_autocomplete)
async def favorite_remove(interaction: discord.Interaction, name: str):
    uid = str(interaction.user.id)
    if uid not in favorites or name not in favorites[uid]:
        await interaction.response.send_message("⚠ 見つかりません", ephemeral=True)
        return
    favorites[uid].remove(name)
    save_json(FAVORITE_FILE, favorites)
    await interaction.response.send_message(f"🗑 削除：{name}", ephemeral=True)

# ===== /favorite_list =====
@tree.command(name="favorite_list", description="お気に入り一覧", guild=GUILD)
async def favorite_list(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    songs = favorites.get(uid, [])
    if not songs:
        await interaction.response.send_message("📭 お気に入りなし", ephemeral=True)
        return

    lines = []
    for s in songs:
        q = urllib.parse.quote(s)
        lines.append(
            f"{s}\n"
            f"Spotify https://open.spotify.com/search/{q}\n"
            f"YouTube https://www.youtube.com/results?search_query={q}\n"
            f"Apple https://music.apple.com/jp/search?term={q}\n"
        )

    await interaction.response.send_message("\n".join(lines), ephemeral=True)

# ===== /sync =====
@tree.command(name="sync", description="コマンド同期", guild=GUILD)
async def sync_cmd(interaction: discord.Interaction):
    await tree.sync(guild=GUILD)
    await interaction.response.send_message("✅ synced", ephemeral=True)

# ===== 起動 =====
client.run(TOKEN)
