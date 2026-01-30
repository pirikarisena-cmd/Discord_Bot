import discord
from discord import app_commands
import urllib.parse
import json
import os

# =============================
# 設定
# =============================
GUILD_ID = 1455898610750197974  # 自分のサーバーID
TOKEN = os.getenv("DISCORD_TOKEN")
FAV_FILE = "favorites.json"

# =============================
# Discord 初期化
# =============================
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
GUILD = discord.Object(id=GUILD_ID)

# =============================
# お気に入り保存
# =============================
if os.path.exists(FAV_FILE):
    with open(FAV_FILE, "r", encoding="utf-8") as f:
        favorites = json.load(f)
else:
    favorites = {}

def save_favorites():
    with open(FAV_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

# =============================
# 共通Embed生成
# =============================
def create_embed(song: str):
    q = urllib.parse.quote(song)
    embed = discord.Embed(
        title=f"🎵 {song}",
        color=0x1DB954
    )
    embed.add_field(name="Spotify", value=f"https://open.spotify.com/search/{q}", inline=False)
    embed.add_field(name="YouTube Music", value=f"https://music.youtube.com/search?q={q}", inline=False)
    embed.add_field(name="Apple Music", value=f"https://music.apple.com/search?term={q}", inline=False)
    return embed

# =============================
# オートコンプリート
# =============================
async def favorite_autocomplete(interaction: discord.Interaction, current: str):
    uid = str(interaction.user.id)
    return [
        app_commands.Choice(name=s, value=s)
        for s in favorites.get(uid, [])
        if current.lower() in s.lower()
    ][:25]

# =============================
# /spotify
# =============================
@tree.command(
    name="spotify",
    description="曲名から音楽リンクを生成",
    guild=GUILD
)
@app_commands.describe(name="曲名")
async def spotify(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(embed=create_embed(name), ephemeral=True)

# =============================
# /randomsong（開発中）
# =============================
@tree.command(
    name="randomsong",
    description="ランダム神曲を紹介（開発中）",
    guild=GUILD
)
async def randomsong(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🚧 現在 /randomsong は開発中です。しばらくお待ち下さい。",
        ephemeral=True
    )

# =============================
# /favorite_add
# =============================
@tree.command(
    name="favorite_add",
    description="お気に入りに曲を追加",
    guild=GUILD
)
@app_commands.describe(name="曲名")
async def favorite_add(interaction: discord.Interaction, name: str):
    uid = str(interaction.user.id)
    favorites.setdefault(uid, [])
    if name not in favorites[uid]:
        favorites[uid].append(name)
        save_favorites()
    embed = create_embed(name)
    embed.set_footer(text="✅ お気に入りに追加しました")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# =============================
# /favorite_remove
# =============================
@tree.command(
    name="favorite_remove",
    description="お気に入りから曲を削除",
    guild=GUILD
)
@app_commands.describe(name="曲名")
@app_commands.autocomplete(name=favorite_autocomplete)
async def favorite_remove(interaction: discord.Interaction, name: str):
    uid = str(interaction.user.id)
    if name in favorites.get(uid, []):
        favorites[uid].remove(name)
        save_favorites()
        await interaction.response.send_message(f"🗑 {name} を削除しました", ephemeral=True)
    else:
        await interaction.response.send_message("⚠ その曲は登録されていません", ephemeral=True)

# =============================
# /favorite_list
# =============================
@tree.command(
    name="favorite_list",
    description="お気に入り一覧表示",
    guild=GUILD
)
async def favorite_list(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    songs = favorites.get(uid, [])
    if not songs:
        await interaction.response.send_message("お気に入りはまだありません", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"{interaction.user.name} のお気に入り",
        color=0xFFD700
    )
    for s in songs:
        embed.add_field(
            name=s,
            value=f"https://open.spotify.com/search/{urllib.parse.quote(s)}",
            inline=False
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# =============================
# 起動時処理
# =============================
@client.event
async def on_ready():
    await tree.sync(guild=GUILD)
    print("Bot Ready | Commands synced")

client.run(TOKEN)

