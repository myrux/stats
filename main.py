import discord
from discord.ext import commands
import os
import asyncio
import database

# --- BURAYA TOKENİNİ YAZ ---
TOKEN = ""

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await database.init_db()
    print(f"✅ Bot Giriş Yaptı: {bot.user}")
    try:
        s = await bot.tree.sync()
        print(f"🔄 {len(s)} komut senkronize edildi.")
    except Exception as e:
        print(e)

async def load_extensions():
    # cogs klasöründeki stats dosyasını yükler
    if os.path.exists("./cogs/stats.py"):
        await bot.load_extension("cogs.stats")
        print("⚙️  Modül yüklendi: stats")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    # ------------------------------------------------------------------
    # 🔥 KRİTİK AYAR: GoodbyeDPI ve VPN ile çalışması için gerekli kod 🔥
    # Bu satır, "Ağ adı geçersiz" (WinError 64) hatasını engeller.
    # ------------------------------------------------------------------
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())