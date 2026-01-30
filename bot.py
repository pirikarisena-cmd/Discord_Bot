@client.event
async def on_ready():
    tree.clear_commands(guild=GUILD)
    await tree.sync(guild=GUILD)
    print("🧹 ゴーストコマンド全削除完了")
    await client.close()
