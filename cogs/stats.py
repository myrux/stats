import discord
from discord.ext import commands, tasks
from discord import app_commands
import database
import time
from datetime import datetime
import io
import aiohttp
import functools

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ HATA: 'Pillow' kütüphanesi eksik!")

# --- DİL AYARLARI ---
LANG = {
    "tr": {
        "lang_set_msg": "✅ Dil **Türkçe** yapıldı! İşlem devam ediyor...",
        "stats_title": "📊 İstatistikler",
        "stats_desc": "**{user}**:\n❤️ Saygınlık: {rep}",
        "lbl_msg": "Mesaj", "lbl_voice": "Ses", "lbl_stream": "Yayın", "lbl_game": "Oyun",
        "no_data": "Veri yok.",
        "time_day": "Bugün", "time_week": "Bu Hafta", "time_month": "Bu Ay", "time_total": "Tüm Zamanlar",
        "setup_title": "⚙️ Yönetim Paneli",
        "btn_role_on": "Rol: AÇIK", "btn_role_off": "Rol: KAPALI",
        "btn_level_on": "Level: AÇIK", "btn_level_off": "Level: KAPALI",
        "btn_quest_on": "Görev: AÇIK", "btn_quest_off": "Görev: KAPALI",
        "btn_gazete_on": "Gazete: AÇIK", "btn_gazete_off": "Gazete: KAPALI",
        "btn_wipe": "🗑️ Veri Sil", "btn_restore": "♻️ Geri Yükle",
        "daily_title": "📰 Gazete Kanalı", "daily_set": "✅ Gazete kanalı: {channel}", "daily_btn": "Gazete Kanalı Seç",
        "perm_error": "⛔ Yetkin yok.",
        "rep_success": "✅ **{user}** +1 Rep!", "rep_fail": "⏳ Bekle: **{time}**", "rep_self": "❌ Kendine rep veremezsin.",
        "vs_title": "🥊 KAPIŞMA: {u1} 🆚 {u2}", "vs_winner": "👑 Kazanan: **{winner}**", "vs_draw": "🤝 BERABERE",
        "server_title": "Sunucu İstatistikleri",
        "srv_total": "Toplam", "srv_top": "Lider",
        "select_placeholder": "Bir kategori seçin...",
        "top_title": "🏆 Liderlik Tablosu",
        "quest_title": "📜 Günlük Görevler", "quest_done": "✅ TAMAMLANDI", "quest_prog": "İlerleme",
        "help_title": "🛠️ Yardım Menüsü",
        "help_desc": "Mevcut komutlar:",
        "cat_user": "Kullanıcı Sıralaması", "cat_channel": "Kanal Sıralaması",
        "ch_msg": "En Aktif Metin Kanalı", "ch_voice": "En Aktif Ses Kanalı",
        "srv_msg": "Mesaj Verileri", "srv_voice": "Ses Verileri",
        "game_list": "🎮 **Oynanan Oyunlar**",
        "wipe_mode_title": "İşlem Modunu Seçiniz",
        "restore_mode_title": "Geri Yükleme Modunu Seçiniz",
        "btn_wipe_user": "👤 Tek Kullanıcı",
        "btn_wipe_server": "🌐 Tüm Sunucu",
        "select_user_wipe": "🗑️ Verisini silmek istediğin kullanıcıyı seç:",
        "select_user_restore": "♻️ Verisini geri yüklemek istediğin kullanıcıyı seç:",
        "confirm_wipe_user": "⚠️ **{user}** verileri silinecek! (Geri yüklenebilir)",
        "confirm_wipe_server": "‼️ **TÜM SUNUCU VERİLERİ SİLİNECEK!** (Arşivlenecek)",
        "confirm_restore_user": "♻️ **{user}** verileri mevcut verilerin üzerine EKLENECEK. Emin misin?",
        "confirm_restore_server": "♻️ **TÜM SUNUCU** verileri geri yüklenecek (Merge). Emin misin?",
        "action_success": "✅ İşlem başarılı.",
        "action_cancel": "❌ İptal edildi.",
        "btn_yes": "EVET", "btn_no": "HAYIR",
        "cmd_desc": {
            "/stats": "Kullanıcı istatistikleri.",
            "/top": "Liderlik tablosu.",
            "/vs": "İki kullanıcıyı karşılaştır.",
            "/rank": "Seviye kartı.",
            "/gorev": "Günlük görevler.",
            "/rep": "Saygınlık puanı ver.",
            "/server": "Sunucu toplam verileri.",
            "/setup": "Ayarlar ve Silme (Admin).",
            "/lang": "Dili değiştir."
        }
    },
    "en": {
        "lang_set_msg": "✅ Language set to **English**! Resuming...",
        "stats_title": "📊 Statistics",
        "stats_desc": "**{user}**:\n❤️ Rep: {rep}",
        "lbl_msg": "Msg", "lbl_voice": "Voice", "lbl_stream": "Stream", "lbl_game": "Game",
        "no_data": "No Data", "time_day": "Today", "time_week": "This Week", "time_month": "This Month", "time_total": "All Time",
        "setup_title": "⚙️ Admin Panel",
        "btn_role_on": "Role: ON", "btn_role_off": "Role: OFF",
        "btn_level_on": "Level: ON", "btn_level_off": "Level: OFF",
        "btn_quest_on": "Quest: ON", "btn_quest_off": "Quest: OFF",
        "btn_gazete_on": "Paper: ON", "btn_gazete_off": "Paper: OFF",
        "btn_wipe": "🗑️ Wipe Data", "btn_restore": "♻️ Restore Data",
        "daily_title": "📰 Paper Channel", "daily_set": "✅ Channel set: {channel}", "daily_btn": "Set Channel",
        "perm_error": "⛔ No Permission.",
        "rep_success": "✅ **{user}** +1 Rep!", "rep_fail": "⏳ Wait: **{time}**", "rep_self": "❌ No self-rep.",
        "vs_title": "🥊 VS: {u1} 🆚 {u2}", "vs_winner": "👑 Winner: **{winner}**", "vs_draw": "🤝 DRAW",
        "server_title": "Server Stats",
        "srv_total": "Total", "srv_top": "Leader",
        "select_placeholder": "Select category...",
        "top_title": "🏆 Leaderboard",
        "quest_title": "📜 Daily Quests", "quest_done": "✅ COMPLETED", "quest_prog": "Progress",
        "help_title": "🛠️ Help Menu", "help_desc": "Available commands:",
        "cat_user": "User Ranking", "cat_channel": "Channel Ranking",
        "ch_msg": "Top Text Channel", "ch_voice": "Top Voice Channel",
        "srv_msg": "Message Stats", "srv_voice": "Voice Stats",
        "game_list": "🎮 **Played Games**",
        "wipe_mode_title": "Select Mode",
        "restore_mode_title": "Select Restore Mode",
        "btn_wipe_user": "👤 Single User",
        "btn_wipe_server": "🌐 Full Server",
        "select_user_wipe": "🗑️ Select user:",
        "select_user_restore": "♻️ Select user:",
        "confirm_wipe_user": "⚠️ Wiping **{user}**! Sure?",
        "confirm_wipe_server": "‼️ **WIPING ALL DATA!** Sure?",
        "confirm_restore_user": "♻️ Restoring/Merging **{user}**. Sure?",
        "confirm_restore_server": "♻️ Restoring **FULL SERVER**. Sure?",
        "action_success": "✅ Success.",
        "action_cancel": "❌ Cancelled.",
        "btn_yes": "YES", "btn_no": "NO",
        "cmd_desc": {
            "/stats": "User statistics.",
            "/top": "Leaderboard.",
            "/vs": "Compare users.",
            "/rank": "Rank card.",
            "/gorev": "Daily quests.",
            "/rep": "Give rep.",
            "/server": "Server totals.",
            "/setup": "Settings & Wipe (Admin).",
            "/lang": "Change language."
        }
    }
}

def format_time(s, lang="tr"):
    if s is None: s = 0
    h = s // 3600; m = (s % 3600) // 60; sec = s % 60
    if h > 0: return f"{h} sa {m} dk" if lang=="tr" else f"{h}h {m}m"
    if m > 0: return f"{m} dk" if lang=="tr" else f"{m}m"
    return f"{sec} sn" if lang=="tr" else f"{sec}s"

def format_quest_list(l, q_data, lang_code="tr"):
    txt = ""
    types = {"msg": l["lbl_msg"], "voice": l["lbl_voice"], "game": l["lbl_game"]}
    emojis = {"msg": "💬", "voice": "🎙️", "game": "🎮"}
    for i, idx in enumerate([3, 7, 11], 1):
        q_type = q_data[idx]; target, prog, done = q_data[idx+1], q_data[idx+2], q_data[idx+3]
        t_name = types.get(q_type, q_type); emo = emojis.get(q_type, "❓")
        tgt_fmt, prog_fmt = str(target), str(prog)
        if q_type in ["voice", "game"]:
            tgt_fmt, prog_fmt = format_time(target, lang_code), format_time(prog, lang_code)
        status = l["quest_done"] if done else f"`{prog_fmt} / {tgt_fmt}`"
        txt += f"**{i}. {emo} {t_name}:** {status}\n"
    return txt

async def safe_send(i, **kwargs):
    try:
        if i.response.is_done(): await i.followup.send(**kwargs)
        else: await i.response.send_message(**kwargs)
    except: pass

def draw_rank_sync(name, xp, level, rank, next_xp, avatar, bg):
    try:
        img = Image.new("RGB", (900, 250), (35, 39, 42))
        if bg:
            try: img.paste(Image.open(io.BytesIO(bg)).convert("RGBA").resize((900, 250)), (0, 0))
            except: pass
        draw = ImageDraw.Draw(img)
        draw.rectangle([250, 180, 850, 210], fill=(72, 75, 78))
        ratio = xp / next_xp if next_xp else 0
        draw.rectangle([250, 180, 250 + int(600 * min(1, ratio)), 210], fill=(88, 101, 242))
        draw.text((250, 50), name, fill="white", font_size=50)
        draw.text((250, 120), f"LEVEL {level} | RANK #{rank}", fill="white", font_size=30)
        if avatar:
            try: img.paste(Image.open(io.BytesIO(avatar)).convert("RGBA").resize((180, 180)), (35, 35))
            except: pass
        buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
        return buf
    except: return None

# --- WIPE & RESTORE FLOW ---
class ConfirmView(discord.ui.View):
    def __init__(self, mode, target_user, l, gid): super().__init__(timeout=60); self.mode=mode; self.u=target_user; self.l=l; self.gid=gid
    @discord.ui.button(label="EVET / YES", style=discord.ButtonStyle.danger)
    async def confirm(self, i, b):
        if not i.user.guild_permissions.administrator: return
        await i.response.defer()
        
        if self.mode == "wipe_user": await database.archive_data(self.gid, self.u.id)
        elif self.mode == "wipe_server": await database.archive_data(self.gid)
        elif self.mode == "restore_user": await database.restore_data(self.gid, self.u.id)
        elif self.mode == "restore_server": await database.restore_data(self.gid)
            
        await i.edit_original_response(content=self.l["action_success"], embed=None, view=None)
    @discord.ui.button(label="HAYIR / NO", style=discord.ButtonStyle.secondary)
    async def cancel(self, i, b): await i.response.edit_message(content=self.l["action_cancel"], embed=None, view=None)

class ModeSelectionView(discord.ui.View):
    def __init__(self, l, action_type): # action_type: "wipe" or "restore"
        super().__init__(timeout=60); self.l=l; self.action=action_type
    
    @discord.ui.button(label="👤 User", style=discord.ButtonStyle.primary)
    async def user_btn(self, i, b):
        msg = self.l["select_user_wipe"] if self.action == "wipe" else self.l["select_user_restore"]
        mode = "wipe_user" if self.action == "wipe" else "restore_user"
        await i.response.edit_message(content=msg, view=AdminActionView(mode, self.l), embed=None)

    @discord.ui.button(label="🌐 Server", style=discord.ButtonStyle.danger)
    async def server_btn(self, i, b):
        mode = "wipe_server" if self.action == "wipe" else "restore_server"
        desc = self.l["confirm_wipe_server"] if self.action == "wipe" else self.l["confirm_restore_server"]
        embed = discord.Embed(description=desc, color=0x992D22)
        await i.response.edit_message(content=None, embed=embed, view=ConfirmView(mode, None, self.l, i.guild.id))

class AdminActionView(discord.ui.View):
    def __init__(self, mode, l): super().__init__(timeout=60); self.add_item(AdminUserSelect(mode, l))

class AdminUserSelect(discord.ui.UserSelect):
    def __init__(self, mode, l): super().__init__(placeholder="User...", min_values=1, max_values=1); self.mode=mode; self.l=l
    async def callback(self, i):
        if not i.user.guild_permissions.administrator: return
        u = self.values[0]
        desc = self.l["confirm_wipe_user"].format(user=u.name) if "wipe" in self.mode else self.l["confirm_restore_user"].format(user=u.name)
        await i.response.edit_message(content=None, embed=discord.Embed(description=desc, color=0xE74C3C), view=ConfirmView(self.mode, u, self.l, i.guild.id))

# --- MAIN VIEWS ---
class TopSelect(discord.ui.Select):
    def __init__(self, l, gid, cog):
        self.l=l; self.gid=gid; self.cog=cog
        options = [
            discord.SelectOption(label=l["lbl_msg"], value="user_msg", emoji="💬", description=l["cat_user"]),
            discord.SelectOption(label=l["lbl_voice"], value="user_voice", emoji="🎙️", description=l["cat_user"]),
            discord.SelectOption(label=l["lbl_stream"], value="user_stream", emoji="🔴", description=l["cat_user"]),
            discord.SelectOption(label=l["lbl_game"], value="user_game", emoji="🎮", description=l["cat_user"]),
            discord.SelectOption(label=l["ch_msg"], value="channel_msg", emoji="#️⃣", description=l["cat_channel"]),
            discord.SelectOption(label=l["ch_voice"], value="channel_voice", emoji="🔊", description=l["cat_channel"])
        ]
        super().__init__(placeholder=l["select_placeholder"], min_values=1, max_values=1, options=options)
    async def callback(self, i):
        try:
            await i.response.defer()
            cat = self.values[0]
            for opt in self.options: opt.default = (opt.value == cat)
            d = await database.get_top_leaderboard(self.gid, cat)
            
            # --- CANLI VERİ HESAPLAMA ---
            now = time.time()
            merged_data = {}
            if d: merged_data = {r[0]: r[1] for r in d}

            if "user_" in cat:
                src = {}
                if "voice" in cat: src = self.cog.voice_states
                elif "stream" in cat: src = self.cog.stream_states
                elif "game" in cat: src = {k: v["time"] for k, v in self.cog.game_states.items()}
                for (gid, uid), start in src.items():
                    if gid == self.gid: merged_data[uid] = merged_data.get(uid, 0) + int(now - start)
                d = sorted(merged_data.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # YENİ: KANAL CANLI HESAPLAMA (SES KANALLARI İÇİN)
            elif "channel_voice" in cat:
                for (gid, uid), start in self.cog.voice_states.items():
                    if gid == self.gid:
                        # Üyenin şu an hangi kanalda olduğunu bul
                        m = i.guild.get_member(uid)
                        if m and m.voice and m.voice.channel:
                            cid = m.voice.channel.id
                            merged_data[cid] = merged_data.get(cid, 0) + int(now - start)
                d = sorted(merged_data.items(), key=lambda x: x[1], reverse=True)[:10]

            txt = ""
            if not d: txt = self.l["no_data"]
            else:
                count = 0
                for x,r in enumerate(d):
                    if "channel_" in cat:
                        ch = i.guild.get_channel(r[0])
                        if not ch: continue
                        if "msg" in cat and not isinstance(ch, (discord.TextChannel, discord.Thread)): continue
                        if "voice" in cat and not isinstance(ch, (discord.VoiceChannel, discord.StageChannel)): continue
                        val = r[1] if "msg" in cat else format_time(r[1], "tr" if self.l==LANG["tr"] else "en")
                        txt += f"**{count+1}.** {ch.mention} : `{val}`\n"; count+=1
                    else:
                        val = r[1] if "msg" in cat else format_time(r[1], "tr" if self.l==LANG["tr"] else "en")
                        txt += f"**{x+1}.** <@{r[0]}> : `{val}`\n"
            
            sel_lbl = next(o.label for o in self.options if o.value == cat)
            embed = discord.Embed(title=f"{self.l['top_title']} - {sel_lbl}", description=txt, color=0xF1C40F)
            await i.edit_original_response(embed=embed, view=self.view)
        except Exception as e: print(f"Top Error: {e}")

class PeriodSelect(discord.ui.Select):
    def __init__(self, target_id, ud, gd, l_code, cog, gid):
        self.target_id=target_id; self.ud=ud; self.gd=gd; self.l=LANG[l_code]; self.l_code=l_code; self.cog=cog; self.gid=gid
        options = [
            discord.SelectOption(label=self.l["time_day"], value="day", emoji="📅", default=True),
            discord.SelectOption(label=self.l["time_week"], value="week", emoji="📆"),
            discord.SelectOption(label=self.l["time_month"], value="month", emoji="🗓️"),
            discord.SelectOption(label=self.l["time_total"], value="total", emoji="📈")
        ]
        super().__init__(placeholder=self.l["select_placeholder"], min_values=1, max_values=1, options=options)
    async def callback(self, i):
        await i.response.defer(); p=self.values[0]
        for opt in self.options: opt.default = (opt.value == p)
        idx = {"day":0, "week":1, "month":2, "total":4}[p]
        m=self.ud[2+idx]; v=self.ud[7+idx]; s=self.ud[12+idx]; g=self.ud[17+idx]
        if (self.gid, self.target_id) in self.cog.voice_states: v += int(time.time() - self.cog.voice_states[(self.gid, self.target_id)])
        if (self.gid, self.target_id) in self.cog.stream_states: s += int(time.time() - self.cog.stream_states[(self.gid, self.target_id)])
        if (self.gid, self.target_id) in self.cog.game_states: g += int(time.time() - self.cog.game_states[(self.gid, self.target_id)]["time"])
        user_name = "User"; usr = i.guild.get_member(self.target_id)
        if usr: user_name = usr.display_name
        e = discord.Embed(title=self.l["stats_title"], description=self.l["stats_desc"].format(user=user_name, period=self.l["time_"+p], rep=self.ud[24]), color=0x2b2d31)
        if i.message.embeds and i.message.embeds[0].thumbnail: e.set_thumbnail(url=i.message.embeds[0].thumbnail.url)
        e.add_field(name=self.l["lbl_msg"], value=str(m)); e.add_field(name=self.l["lbl_voice"], value=format_time(v, self.l_code))
        e.add_field(name=self.l["lbl_stream"], value=format_time(s, self.l_code)); e.add_field(name=self.l["lbl_game"], value=format_time(g, self.l_code))
        if self.gd:
            g_list = ""; 
            for gname, dur in self.gd: g_list += f"▫️ **{gname}**: {format_time(dur, self.l_code)}\n"
            e.add_field(name=self.l["game_list"], value=g_list, inline=False)
        await i.edit_original_response(embed=e, view=self.view)

class ServerSelect(discord.ui.Select):
    def __init__(self, l, gid, cog):
        self.l=l; self.gid=gid; self.cog=cog
        options = [discord.SelectOption(label=l["srv_msg"], value="user_msg", emoji="💬"), discord.SelectOption(label=l["srv_voice"], value="user_voice", emoji="🎙️")]
        super().__init__(placeholder=l["select_placeholder"], min_values=1, max_values=1, options=options)
    async def callback(self, i):
        await i.response.defer(); cat = self.values[0]
        for opt in self.options: opt.default = (opt.value == cat)
        top = await database.get_top_leaderboard(self.gid, cat)
        m_data = {r[0]: r[1] for r in top}; now = time.time(); src = self.cog.voice_states if "voice" in cat else {}
        for (gid, uid), s in src.items():
            if gid == self.gid: m_data[uid] = m_data.get(uid, 0) + int(now - s)
        s_top = sorted(m_data.items(), key=lambda x: x[1], reverse=True)
        top_u = f"<@{s_top[0][0]}> ({s_top[0][1] if 'msg' in cat else format_time(s_top[0][1])})" if s_top else "Yok"
        t, _ = await database.get_server_totals(self.gid); tm = t[0] or 0; tv = t[1] or 0
        if "voice" in cat:
            for (gid, uid), s in self.cog.voice_states.items():
                if gid == self.gid: tv += int(now - s)
        val = str(tm) if "msg" in cat else format_time(tv)
        e = discord.Embed(title=f"{self.l['server_title']} - {next(o.label for o in self.options if o.value == cat)}", description=f"**{self.l['srv_total']}:** {val}\n**{self.l['srv_top']}:** {top_u}", color=0x3498db)
        if i.guild.icon: e.set_thumbnail(url=i.guild.icon.url)
        await i.edit_original_response(embed=e, view=self.view)

class StatsView(discord.ui.View):
    def __init__(self, uid, ud, gd, l_code, cog, gid): super().__init__(timeout=None); self.add_item(PeriodSelect(uid, ud, gd, l_code, cog, gid))
class TopView(discord.ui.View):
    def __init__(self, l, gid, cog): super().__init__(timeout=None); self.add_item(TopSelect(l, gid, cog))
class ServerStatsView(discord.ui.View):
    def __init__(self, l, gid, cog): super().__init__(timeout=None); self.add_item(ServerSelect(l, gid, cog))

class SetupView(discord.ui.View):
    def __init__(self, l, gid, settings):
        super().__init__(timeout=None); self.l=l; self.gid=gid
        self.add_item(self.cb(l["btn_role_on"] if settings[0] else l["btn_role_off"], settings[0], "role"))
        self.add_item(self.cb(l["btn_level_on"] if settings[1] else l["btn_level_off"], settings[1], "level"))
        self.add_item(self.cb(l["btn_quest_on"] if settings[2] else l["btn_quest_off"], settings[2], "quest"))
        self.add_item(self.cb(l["btn_gazete_on"] if settings[3] else l["btn_gazete_off"], settings[3], "gazete"))
        if settings[3]: self.add_item(ChannelSelect(l, gid))
        self.add_item(self.create_wipe_btn(l["btn_wipe"]))
        self.add_item(self.create_restore_btn(l["btn_restore"]))
    def cb(self, lbl, status, t):
        s = discord.ButtonStyle.success if status else discord.ButtonStyle.secondary
        b = discord.ui.Button(label=lbl, style=s); b.callback = functools.partial(self.act, t=t); return b
    def create_wipe_btn(self, label):
        b = discord.ui.Button(label=label, style=discord.ButtonStyle.danger, row=2); b.callback = self.wipe_action; return b
    def create_restore_btn(self, label):
        b = discord.ui.Button(label=label, style=discord.ButtonStyle.secondary, row=2); b.callback = self.restore_action; return b
    async def act(self, i, t):
        if not i.user.guild_permissions.administrator: return await i.response.send_message(self.l["perm_error"], ephemeral=True)
        curr = await database.get_settings(self.gid)
        if t=="role": await database.set_role_system(self.gid, 0 if curr[0] else 1)
        elif t=="level": await database.set_level_system(self.gid, 0 if curr[1] else 1)
        elif t=="quest": await database.set_quest_system(self.gid, 0 if curr[2] else 1)
        elif t=="gazete": await database.set_gazete_system(self.gid, 0 if curr[3] else 1)
        new_s = await database.get_settings(self.gid); await i.response.edit_message(view=SetupView(self.l, self.gid, new_s))
    async def wipe_action(self, i):
        if not i.user.guild_permissions.administrator: return await i.response.send_message(self.l["perm_error"], ephemeral=True)
        await i.response.send_message(self.l["wipe_mode_title"], view=ModeSelectionView(self.l, "wipe"), ephemeral=True)
    async def restore_action(self, i):
        if not i.user.guild_permissions.administrator: return await i.response.send_message(self.l["perm_error"], ephemeral=True)
        await i.response.send_message(self.l["restore_mode_title"], view=ModeSelectionView(self.l, "restore"), ephemeral=True)

class ChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, l, gid): super().__init__(placeholder=l["daily_btn"], channel_types=[discord.ChannelType.text]); self.l=l; self.gid=gid
    async def callback(self, i):
        if not i.user.guild_permissions.administrator: return await i.response.send_message(self.l["perm_error"], ephemeral=True)
        await database.set_daily_channel(self.gid, self.values[0].id)
        await i.response.send_message(self.l["daily_set"].format(channel=self.values[0].mention), ephemeral=True)

class LanguageView(discord.ui.View):
    def __init__(self, cog, i, callback, *args): super().__init__(timeout=300); self.cog=cog; self.i=i; self.cb=callback; self.args=args
    async def set_lang(self, i, code):
        await i.response.defer(ephemeral=True); await database.set_language(i.guild.id, code); await i.followup.send(LANG[code]["lang_set_msg"], ephemeral=True)
        if self.cb: await self.cb(i, *self.args)
    @discord.ui.button(label="Türkçe", style=discord.ButtonStyle.green, emoji="🇹🇷")
    async def tr(self, i, b): await self.set_lang(i, "tr")
    @discord.ui.button(label="English", style=discord.ButtonStyle.blurple, emoji="🇬🇧")
    async def en(self, i, b): await self.set_lang(i, "en")

class OnlyLangView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Türkçe", style=discord.ButtonStyle.green, emoji="🇹🇷")
    async def tr(self, i, b): await database.set_language(i.guild.id, "tr"); await i.response.send_message("✅ Dil **Türkçe**!", ephemeral=True)
    @discord.ui.button(label="English", style=discord.ButtonStyle.blurple, emoji="🇬🇧")
    async def en(self, i, b): await database.set_language(i.guild.id, "en"); await i.response.send_message("✅ Language set to **English**!", ephemeral=True)

# --- COG ---
class StatsCog(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot; self.voice_states = {}; self.stream_states = {}; self.game_states = {}
    def cog_unload(self): self.loop.cancel()
    @tasks.loop(minutes=5)
    async def loop(self): 
        try: await database.check_and_reset_timers()
        except: pass

    async def ensure_lang(self, i, callback, *args):
        l_code = await database.get_language(i.guild.id)
        if not l_code:
            embed = discord.Embed(description="👋 **Please select a language / Lütfen bir dil seçin:**", color=0xFEE75C)
            await i.response.send_message(embed=embed, view=LanguageView(self, i, callback, *args), ephemeral=True)
            return None, None 
        return LANG[l_code], l_code

    @commands.Cog.listener()
    async def on_ready(self):
        self.loop.start(); now = time.time()
        for g in self.bot.guilds:
            for vc in g.voice_channels:
                for m in vc.members:
                    if m.bot: continue
                    self.voice_states[(g.id, m.id)] = now
                    if m.voice.self_stream: self.stream_states[(g.id, m.id)] = now
                    if m.activity and m.activity.type == discord.ActivityType.playing:
                        self.game_states[(g.id, m.id)] = {"name": m.activity.name, "time": now}

    @commands.Cog.listener()
    async def on_message(self, m):
        if m.author.bot or not m.guild: return
        await database.add_message_stats(m.guild.id, m.author.id, m.channel.id, len(m.content.split()), len(m.content))
        await database.add_xp(m.guild.id, m.author.id, 2)
        await database.update_quest_progress(m.guild.id, m.author.id, "msg", 1)

    @commands.Cog.listener()
    async def on_voice_state_update(self, m, b, a):
        if m.bot: return
        gid = m.guild.id; uid = m.id; now = time.time()
        if b.channel is None and a.channel: self.voice_states[(gid, uid)] = now
        elif b.channel and a.channel is None:
            if (gid, uid) in self.voice_states:
                d = int(now - self.voice_states.pop((gid, uid)))
                await database.add_time_stats(gid, uid, b.channel.id, v=d)
                await database.add_xp(gid, uid, (d//60)*5)
                await database.update_quest_progress(gid, uid, "voice", d)
        elif b.channel and a.channel and b.channel.id != a.channel.id:
             if (gid, uid) in self.voice_states:
                d = int(now - self.voice_states.pop((gid, uid)))
                await database.add_time_stats(gid, uid, b.channel.id, v=d)
                self.voice_states[(gid, uid)] = now
        if not b.self_stream and a.self_stream: self.stream_states[(gid, uid)] = now
        elif b.self_stream and (not a.self_stream or not a.channel):
            if (gid, uid) in self.stream_states:
                d = int(now - self.stream_states.pop((gid, uid)))
                await database.add_time_stats(gid, uid, b.channel.id, s=d)

    @commands.Cog.listener()
    async def on_presence_update(self, b, a):
        if a.bot: return
        gid = a.guild.id; uid = a.id; now = time.time()
        new_game = next((act for act in a.activities if act.type == discord.ActivityType.playing), None)
        old_game = next((act for act in b.activities if act.type == discord.ActivityType.playing), None)
        if new_game and not old_game: self.game_states[(gid, uid)] = {"name": new_game.name, "time": now}
        elif old_game and not new_game:
            if (gid, uid) in self.game_states:
                data = self.game_states.pop((gid, uid))
                dur = int(now - data["time"])
                await database.update_game_stats(gid, uid, data["name"], pt=dur)
                await database.update_quest_progress(gid, uid, "game", dur)

    # --- KOMUTLAR ---
    async def _stats_logic(self, i, user):
        l, lc = await self.ensure_lang(i, self._stats_logic, user)
        if not l: return
        if not i.response.is_done(): await i.response.defer()
        t = user or i.user
        ud, gd = await database.get_stats(i.guild.id, t.id)
        if not ud: ud = (i.guild.id, t.id, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0, 1, 0, 0, None)
        m, v, s, g = ud[2], ud[7], ud[12], ud[17]
        if (i.guild.id, t.id) in self.voice_states: v += int(time.time() - self.voice_states[(i.guild.id, t.id)])
        if (i.guild.id, t.id) in self.stream_states: s += int(time.time() - self.stream_states[(i.guild.id, t.id)])
        if (i.guild.id, t.id) in self.game_states: g += int(time.time() - self.game_states[(i.guild.id, t.id)]["time"])
        embed = discord.Embed(title=l["stats_title"], description=l["stats_desc"].format(user=t.display_name, period=l["time_day"], rep=ud[24]), color=0x2b2d31)
        if t.display_avatar: embed.set_thumbnail(url=t.display_avatar.url)
        lc = "tr" if l == LANG["tr"] else "en"
        embed.add_field(name=l["lbl_msg"], value=str(m)); embed.add_field(name=l["lbl_voice"], value=format_time(v, lc))
        embed.add_field(name=l["lbl_stream"], value=format_time(s, lc)); embed.add_field(name=l["lbl_game"], value=format_time(g, lc))
        if gd:
            g_list = ""; 
            for gname, dur in gd: g_list += f"▫️ **{gname}**: {format_time(dur, lc)}\n"
            embed.add_field(name=l["game_list"], value=g_list, inline=False)
        await safe_send(i, embed=embed, view=StatsView(t.id, ud, gd, lc, self, i.guild.id))

    @app_commands.command(name="stats", description="İstatistikler / Stats")
    async def stats(self, i: discord.Interaction, user: discord.User = None): await self._stats_logic(i, user)
    @app_commands.command(name="profil", description="Profil / Profile")
    async def profil(self, i: discord.Interaction, user: discord.User = None): await self._stats_logic(i, user)

    @app_commands.command(name="top", description="Sıralama / Leaderboard")
    async def top(self, i: discord.Interaction):
        l, lc = await self.ensure_lang(i, self.top)
        if not l: return
        if not i.response.is_done(): await i.response.defer()
        embed = discord.Embed(title=l["top_title"], description=l["select_placeholder"], color=0xF1C40F)
        await safe_send(i, embed=embed, view=TopView(l, i.guild.id, self))
    @app_commands.command(name="sıralama", description="Sıralama")
    async def sirlama(self, i: discord.Interaction): await self.top.callback(self, i)

    @app_commands.command(name="server", description="Sunucu / Server")
    async def server(self, i: discord.Interaction):
        l, lc = await self.ensure_lang(i, self.server)
        if not l: return
        if not i.response.is_done(): await i.response.defer()
        embed = discord.Embed(title=l["server_title"], description=l["select_placeholder"], color=0x3498db)
        if i.guild.icon: embed.set_thumbnail(url=i.guild.icon.url)
        await safe_send(i, embed=embed, view=ServerStatsView(l, i.guild.id, self))
    @app_commands.command(name="sunucu", description="Sunucu")
    async def sunucu(self, i: discord.Interaction): await self.server.callback(self, i)

    @app_commands.command(name="gorev", description="Görevler")
    async def gorev(self, i: discord.Interaction):
        l, lc = await self.ensure_lang(i, self.gorev)
        if not l: return
        if not i.response.is_done(): await i.response.defer()
        q = await database.get_or_create_quests(i.guild.id, i.user.id)
        txt = format_quest_list(l, q, lc) if q else "❌"
        await safe_send(i, embed=discord.Embed(title=l["quest_title"], description=txt, color=0xe67e22))
    @app_commands.command(name="quest", description="Quests")
    async def quest(self, i: discord.Interaction): await self.gorev.callback(self, i)

    @app_commands.command(name="setup", description="Ayarlar / Settings")
    async def setup(self, i: discord.Interaction):
        l, lc = await self.ensure_lang(i, self.setup)
        if not l: return
        if not i.response.is_done(): await i.response.defer(ephemeral=True)
        s = await database.get_settings(i.guild.id)
        await safe_send(i, embed=discord.Embed(title=l["setup_title"], color=0x9b59b6), view=SetupView(l, i.guild.id, s))
    @app_commands.command(name="ayarlar", description="Ayarlar")
    async def ayarlar(self, i: discord.Interaction): await self.setup.callback(self, i)

    @app_commands.command(name="vs", description="Karşılaştır / Compare")
    async def vs(self, i: discord.Interaction, user: discord.User): await self._vs_logic(i, user)
    @app_commands.command(name="kapışma", description="Karşılaştır")
    async def kapisma(self, i: discord.Interaction, user: discord.User): await self._vs_logic(i, user)

    async def _vs_logic(self, i, user):
        l, lc = await self.ensure_lang(i, self._vs_logic, user)
        if not l: return
        if not i.response.is_done(): await i.response.defer()
        d1,_ = await database.get_stats(i.guild.id, i.user.id); d2,_ = await database.get_stats(i.guild.id, user.id)
        if not d1: d1 = (0,)*27
        if not d2: d2 = (0,)*27
        m1=d1[6]; m2=d2[6]; v1=d1[11]; v2=d2[11]; g1=d1[21]; g2=d2[21]
        p1 = (1 if m1>m2 else 0)+(1 if v1>v2 else 0)+(1 if g1>g2 else 0)
        p2 = (1 if m2>m1 else 0)+(1 if v2>v1 else 0)+(1 if g2>g1 else 0)
        winner = i.user.display_name if p1>p2 else user.display_name if p2>p1 else l["vs_draw"]
        embed = discord.Embed(title=l["vs_title"].format(u1=i.user.display_name, u2=user.display_name), description=l["vs_winner"].format(winner=winner), color=0xe74c3c)
        embed.add_field(name=l["lbl_msg"], value=f"{m1} 🆚 {m2}", inline=True)
        embed.add_field(name=l["lbl_voice"], value=f"{format_time(v1, lc)} 🆚 {format_time(v2, lc)}", inline=True)
        embed.add_field(name=l["lbl_game"], value=f"{format_time(g1, lc)} 🆚 {format_time(g2, lc)}", inline=True)
        await safe_send(i, embed=embed)

    @app_commands.command(name="rep", description="Rep")
    async def rep(self, i: discord.Interaction, user: discord.User):
        l, lc = await self.ensure_lang(i, self.rep, user)
        if not l: return
        if not i.response.is_done(): await i.response.defer()
        if user.id == i.user.id: return await safe_send(i, content=l["rep_self"])
        res, t = await database.give_rep(i.guild.id, i.user.id, user.id)
        if res: await safe_send(i, content=l["rep_success"].format(user=user.name))
        else: await safe_send(i, content=l["rep_fail"].format(time=int(t-time.time())))

    @app_commands.command(name="help", description="Yardım / Help")
    async def help(self, i: discord.Interaction):
        l, lc = await self.ensure_lang(i, self.help)
        if not l: return
        if not i.response.is_done(): await i.response.defer()
        e = discord.Embed(title=l["help_title"], description=l["help_desc"], color=0x9b59b6)
        if self.bot.user.display_avatar: e.set_thumbnail(url=self.bot.user.display_avatar.url)
        for cmd, desc in l["cmd_desc"].items():
            e.add_field(name=f"`{cmd}`", value=desc, inline=True)
        await safe_send(i, embed=e)
    @app_commands.command(name="yardım", description="Yardım")
    async def yardim(self, i: discord.Interaction): await self.help.callback(self, i)

    # --- OTHER ---
    @app_commands.command(name="arkaplan", description="BG")
    async def arkaplan(self, i: discord.Interaction, url: str): await i.response.defer(ephemeral=True); await database.set_bg_url(i.guild.id, i.user.id, url); await safe_send(i, content="✅")
    @app_commands.command(name="bg", description="BG")
    async def bg(self, i: discord.Interaction, url: str): await self.arkaplan.callback(self, i, url)
    @app_commands.command(name="rank", description="Rank")
    async def rank(self, i: discord.Interaction, user: discord.User = None):
        l, lc = await self.ensure_lang(i, self.rank, user)
        if not l: return
        if not i.response.is_done(): await i.response.defer()
        t = user or i.user
        xp, level, rep, bg, rank = await database.get_rank_data(i.guild.id, t.id)
        av, bg_b = None, None
        if t.display_avatar: 
            async with aiohttp.ClientSession() as s: 
                async with s.get(t.display_avatar.url) as r: av = await r.read()
        if bg: 
            async with aiohttp.ClientSession() as s: 
                async with s.get(bg) as r: bg_b = await r.read()
        f = await self.bot.loop.run_in_executor(None, functools.partial(draw_rank_sync, t.name, xp, level, rank, level*500, av, bg_b))
        if f: await i.followup.send(file=discord.File(f, "rank.png"))
        else: await safe_send(i, content="❌ Error")
    @app_commands.command(name="seviye", description="Rank")
    async def seviye(self, i: discord.Interaction, user: discord.User = None): await self.rank.callback(self, i, user)
    @app_commands.command(name="set_lang", description="Lang")
    async def set_lang(self, i: discord.Interaction): 
        if not i.user.guild_permissions.administrator: return await i.response.send_message("⛔ Admin only", ephemeral=True)
        await i.response.send_message("Dil / Language:", view=OnlyLangView())
    @app_commands.command(name="lang", description="Lang")
    async def lang(self, i: discord.Interaction): await self.set_lang.callback(self, i)

async def setup(bot):
    await bot.add_cog(StatsCog(bot))