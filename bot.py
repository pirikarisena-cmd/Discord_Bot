import os
import discord
from discord import app_commands
import urllib.parse

# ===== 設定 =====
GUILD_ID = 1455898610750197974  # 自分のサーバーID
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN が設定されていません")

# ===== Discord Client =====
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
GUILD = discord.Object(id=GUILD_ID)

# ===== 起動時 =====
@client.event
async def on_ready():
    await tree.sync(guild=GUILD)
    print(f"✅ Logged in as {client.user}")

# ===== /spotify =====
@tree.command(
    name="spotify",
    description="曲名からSpotify検索リンクを生成",
    guild=GUILD
)
@app_commands.describe(name="曲名")
async def spotify(interaction: discord.Interaction, name: str):
    query = urllib.parse.quote(name)
    url = f"https://open.spotify.com/search/{query}"
    await interaction.response.send_message(url)

# ===== /randomsong（仮）=====
@tree.command(
    name="randomsong",
    description="ランダム曲（開発中）",
    guild=GUILD
)
async def randomsong(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🚧 現在開発中です。しばらくお待ち下さい。"
    )

# ===== /sync（ゴースト対策用）=====
@tree.command(
    name="sync",
    description="コマンドを再同期（管理者用）",
    guild=GUILD
)
async def sync_cmd(interaction: discord.Interaction):
    await tree.sync(guild=GUILD)
    await interaction.response.send_message("✅ 同期しました", ephemeral=True)

# ===== 起動 =====
client.run(TOKEN)
