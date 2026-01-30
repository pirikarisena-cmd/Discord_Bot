import os
import json
import random
import urllib.parse
import discord
from discord import app_commands

# =====================
# 設定
# =====================
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1455898610750197974  # ←自分のサーバーID

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN が設定されていません")

# =====================
# データ保存先（Railway Volume対応）
# =====================
DATA_DIR = "/app/data" if os.path.exists("/app") else "./data"
os.makedirs(DATA_DIR, exist_ok=True)

FAVORITES_FILE = f"{DATA_DIR}/favorites.json"
RANDOM_FILE = f"{DATA_DIR}/random_songs.json"

# =====================
# JSONユーティリティ
# =====================
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def spotify_search(q: str) -> str:
    return f"https://open.spotify.com/search/{urllib.parse.quote(q)}"

# =====================
# Discord Client
# =====================
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
GUILD = discord.Object(id=GUILD_ID)

# =====================
# 起動時（即ギルド同期）
# =====================
@client.event
async def on_ready():
    await tree.sync(guild=GUILD)
    print(f"✅ Logged in as {client.user}")

# =====================
# /spotify
# =====================
@tree.command(
    name="spotify",
    description="曲名からSpotify検索リンクを生成",
    guild=GUILD
)
@app_commands.describe(name="曲名")
async def spotify(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(spotify_search(name))

# =====================
# /randomsong（JSON神曲）
# =====================
@tree.command(
    name="randomsong",
    description="ランダムで神曲を紹介",
    guild=GUILD
)
async def randomsong(interaction: discord.Interaction):
    songs = load_json(RANDOM_FILE, [])

    if not songs:
        await interaction.response.send_message(
            "⚠ 神曲リストが空です（random_songs.json）",
            ephemeral=True
        )
        return

    song = random.choice(songs)
    await interaction.response.send_message(
        f"🔥 **今日の神曲**\n{song}\n{spotify_search(song)}"
    )

# =====================
# /favorite_add
# =====================
@tree.command(
    name="favorite_add",
    description="お気に入りに曲を追加",
    guild=GUILD
)
@app_commands.describe(name="曲名")
async def favorite_add(interaction: discord.Interaction, name: str):
    data = load_json(FAVORITES_FILE, {})
    uid = str(interaction.user.id)

    data.setdefault(uid, [])
    if name not in data[uid]:
        data[uid].append(name)
        save_json(FAVORITES_FILE, data)

    await interaction.response.send_message(
        f"⭐ 追加しました\n{spotify_search(name)}",
        ephemeral=True
    )

# =====================
# /favorite_list
# =====================
@tree.command(
    name="favorite_list",
    description="お気に入り一覧",
    guild=GUILD
)
async def favorite_list(interaction: discord.Interaction):
    data = load_json(FAVORITES_FILE, {})
    uid = str(interaction.user.id)

    songs = data.get(uid, [])
    if not songs:
        await interaction.response.send_message(
            "📭 お気に入りはまだありません",
            ephemeral=True
        )
        return

    msg = "🎧 **お気に入り一覧**\n"
    msg += "\n".join(f"- {spotify_search(s)}" for s in songs)
    await interaction.response.send_message(msg, ephemeral=True)

# =====================
# /favorite_remove
# =====================
@tree.command(
    name="favorite_remove",
    description="お気に入りから削除",
    guild=GUILD
)
@app_commands.describe(name="曲名")
async def favorite_remove(interaction: discord.Interaction, name: str):
    data = load_json(FAVORITES_FILE, {})
    uid = str(interaction.user.id)

    if uid in data and name in data[uid]:
        data[uid].remove(name)
        save_json(FAVORITES_FILE, data)
        await interaction.response.send_message("🗑 削除しました", ephemeral=True)
    else:
        await interaction.response.send_message(
            "⚠ その曲は登録されていません",
            ephemeral=True
        )
@client.event
async def on_ready():
    tree.clear_commands(guild=GUILD)
    await tree.sync(guild=GUILD)
    print("🧹 ゴーストコマンド全削除完了")
    await client.close()

# =====================
# 起動
# =====================
client.run(TOKEN)
