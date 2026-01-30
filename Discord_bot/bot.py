import discord
from discord import app_commands
from discord.ext import tasks
import urllib.parse
import json
import os

# -----------------------------
TOKEN = "MTQ2NjY2MTk5MTU3MjcwNTMyNw.GdbpSb.ZNKuc43eXQadu-5gswbGp_dI60LKxjtmlypa6k"
GUILD_ID = 1455898610750197974  # 自分のサーバーID
FAV_FILE = "favorites.json"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# -----------------------------
# お気に入りロード
if os.path.exists(FAV_FILE):
    with open(FAV_FILE, "r", encoding="utf-8") as f:
        favorites = json.load(f)
else:
    favorites = {}

def save_favorites():
    with open(FAV_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

# -----------------------------
async def song_autocomplete(interaction: discord.Interaction, current: str):
    user_id = str(interaction.user.id)
    # ユーザーのお気に入りのみ補完
    choices = [app_commands.Choice(name=s, value=s) for s in favorites.get(user_id, []) if current.lower() in s.lower()]
    return choices[:25]

# -----------------------------
def create_embed(song_name: str):
    query = urllib.parse.quote(song_name)
    links = {
        "Spotify": f"https://open.spotify.com/search/{query}",
        "YouTube Music": f"https://music.youtube.com/search?q={query}",
        "Apple Music": f"https://music.apple.com/search?term={query}"
    }
    embed = discord.Embed(title=f"🎵 {song_name} のリンク", color=0x1DB954)
    for service, url in links.items():
        embed.add_field(name=service, value=f"[▶ 再生]({url})", inline=False)
    return embed

# -----------------------------
@tree.command(name="spotify", description="曲名からリンク生成")
@app_commands.describe(name="曲名を入力")
@app_commands.autocomplete(name=song_autocomplete)
async def spotify(interaction: discord.Interaction, name: str):
    embed = create_embed(name)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# -----------------------------
@tree.command(name="randomsong", description="ランダム曲リンク生成（開発中）")
async def randomsong(interaction: discord.Interaction):
    await interaction.response.send_message("🚧 /randomsong は現在開発中です。しばらくお待ち下さい。", ephemeral=True)

# -----------------------------
@tree.command(name="favorite_add", description="お気に入りに曲を追加")
@app_commands.describe(name="曲名")
@app_commands.autocomplete(name=song_autocomplete)
async def favorite_add(interaction: discord.Interaction, name: str):
    user_id = str(interaction.user.id)
    if user_id not in favorites:
        favorites[user_id] = []
    if name not in favorites[user_id]:
        favorites[user_id].append(name)
    save_favorites()
    embed = create_embed(name)
    embed.set_footer(text="✅ お気に入りに追加されました")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# -----------------------------
@tree.command(name="favorite_remove", description="お気に入りから曲を削除")
@app_commands.describe(name="曲名")
@app_commands.autocomplete(name=song_autocomplete)
async def favorite_remove(interaction: discord.Interaction, name: str):
    user_id = str(interaction.user.id)
    if user_id not in favorites or name not in favorites[user_id]:
        await interaction.response.send_message(f"⚠ {name} はお気に入りに存在しません。", ephemeral=True)
        return
    favorites[user_id].remove(name)
    save_favorites()
    await interaction.response.send_message(f"🗑 {name} をお気に入りから削除しました。", ephemeral=True)

# -----------------------------
@tree.command(name="favorite_list", description="お気に入り一覧リンク表示")
async def favorite_list(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    songs = favorites.get(user_id, [])
    if not songs:
        await interaction.response.send_message("お気に入りはまだありません。", ephemeral=True)
        return
    embed = discord.Embed(title=f"{interaction.user.name} のお気に入り曲", color=0xFFD700)
    for s in songs:
        embed.add_field(name=s, value=f"[▶ 再生](https://open.spotify.com/search/{urllib.parse.quote(s)})", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# -----------------------------
@tree.command(name="sync", description="開発用ギルドにコマンド同期")
async def sync(interaction: discord.Interaction):
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    await interaction.response.send_message("✅ コマンド同期完了（開発用ギルド）", ephemeral=True)

# -----------------------------
@client.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    print("Bot Ready. 開発用ギルドにコマンド同期済み")

client.run(TOKEN)
