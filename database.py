import aiosqlite
import time
import json
from datetime import datetime

DB_NAME = "stats.db"

async def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    try:
        async with aiosqlite.connect(DB_NAME, timeout=30) as db:
            cursor = await db.execute(query, params)
            if commit: await db.commit()
            if fetchone: return await cursor.fetchone()
            if fetchall: return await cursor.fetchall()
            return True
    except Exception as e:
        if "no such table" not in str(e): print(f"⚠️ DB Error: {e}")
        return None

async def init_db():
    print("🔋 DATABASE: Tablolar Kuruluyor...")
    queries = [
        """CREATE TABLE IF NOT EXISTS user_stats (
            guild_id INTEGER, user_id INTEGER, 
            msg_day INTEGER DEFAULT 0, msg_week INTEGER DEFAULT 0, msg_month INTEGER DEFAULT 0, msg_year INTEGER DEFAULT 0, msg_total INTEGER DEFAULT 0,
            voice_day INTEGER DEFAULT 0, voice_week INTEGER DEFAULT 0, voice_month INTEGER DEFAULT 0, voice_year INTEGER DEFAULT 0, voice_total INTEGER DEFAULT 0,
            stream_day INTEGER DEFAULT 0, stream_week INTEGER DEFAULT 0, stream_month INTEGER DEFAULT 0, stream_year INTEGER DEFAULT 0, stream_total INTEGER DEFAULT 0,
            game_day INTEGER DEFAULT 0, game_week INTEGER DEFAULT 0, game_month INTEGER DEFAULT 0, game_year INTEGER DEFAULT 0, game_total INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1,
            rep INTEGER DEFAULT 0, last_rep_time INTEGER DEFAULT 0, bg_url TEXT DEFAULT NULL,
            PRIMARY KEY (guild_id, user_id))""",
        "CREATE TABLE IF NOT EXISTS game_stats (guild_id INTEGER, user_id INTEGER, game_name TEXT, play_duration INTEGER DEFAULT 0, PRIMARY KEY (guild_id, user_id, game_name))",
        "CREATE TABLE IF NOT EXISTS channel_stats (guild_id INTEGER, channel_id INTEGER, msg_count INTEGER DEFAULT 0, voice_duration INTEGER DEFAULT 0, PRIMARY KEY (guild_id, channel_id))",
        "CREATE TABLE IF NOT EXISTS settings (guild_id INTEGER PRIMARY KEY, authorized_role_id INTEGER, language TEXT DEFAULT NULL, role_system_active INTEGER DEFAULT 0, level_system_active INTEGER DEFAULT 0, quest_system_active INTEGER DEFAULT 0, gazete_system_active INTEGER DEFAULT 0, daily_channel_id INTEGER DEFAULT NULL)",
        "CREATE TABLE IF NOT EXISTS daily_quests (guild_id INTEGER, user_id INTEGER, date_id INTEGER, q1_type TEXT, q1_target INTEGER, q1_progress INTEGER DEFAULT 0, q1_done INTEGER DEFAULT 0, q2_type TEXT, q2_target INTEGER, q2_progress INTEGER DEFAULT 0, q2_done INTEGER DEFAULT 0, q3_type TEXT, q3_target INTEGER, q3_progress INTEGER DEFAULT 0, q3_done INTEGER DEFAULT 0, PRIMARY KEY (guild_id, user_id, date_id))",
        "CREATE TABLE IF NOT EXISTS reset_timers (id INTEGER PRIMARY KEY, last_day INTEGER, last_week INTEGER, last_month INTEGER)",
        # ARCHIVE TABLOSU (JSON FORMATINDA SAKLAR)
        "CREATE TABLE IF NOT EXISTS archived_data (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER, user_id INTEGER DEFAULT NULL, data_type TEXT, json_data TEXT, deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    ]
    for q in queries: await execute_query(q, commit=True)
    
    now = datetime.now()
    week_num = now.isocalendar()[1]
    await execute_query("INSERT OR IGNORE INTO reset_timers (id, last_day, last_week, last_month) VALUES (1, ?, ?, ?)", (now.day, week_num, now.month), commit=True)
    print("✅ DATABASE: Hazır!")

async def check_and_reset_timers():
    try:
        res = await execute_query("SELECT last_day, last_week, last_month FROM reset_timers WHERE id=1", fetchone=True)
        if not res: return
        last_d, last_w, last_m = res
        now = datetime.now()
        curr_d, curr_w, curr_m = now.day, now.isocalendar()[1], now.month
        
        if curr_d != last_d:
            await execute_query("UPDATE user_stats SET msg_day=0, voice_day=0, stream_day=0, game_day=0", commit=True)
            await execute_query("UPDATE reset_timers SET last_day=? WHERE id=1", (curr_d,), commit=True)
        if curr_w != last_w:
            await execute_query("UPDATE user_stats SET msg_week=0, voice_week=0, stream_week=0, game_week=0", commit=True)
            await execute_query("UPDATE reset_timers SET last_week=? WHERE id=1", (curr_w,), commit=True)
        if curr_m != last_m:
            await execute_query("UPDATE user_stats SET msg_month=0, voice_month=0, stream_month=0, game_month=0", commit=True)
            await execute_query("UPDATE reset_timers SET last_month=? WHERE id=1", (curr_m,), commit=True)
    except: pass

# --- GETTERS ---
async def get_language(gid):
    r = await execute_query("SELECT language FROM settings WHERE guild_id=?", (gid,), fetchone=True)
    return r[0] if r else None

async def set_language(gid, lang):
    await execute_query("INSERT OR IGNORE INTO settings (guild_id) VALUES (?)", (gid,), commit=True)
    await execute_query("UPDATE settings SET language=? WHERE guild_id=?", (lang, gid), commit=True)

async def get_settings(gid):
    r = await execute_query("SELECT role_system_active, level_system_active, quest_system_active, gazete_system_active, daily_channel_id FROM settings WHERE guild_id=?", (gid,), fetchone=True)
    return r if r else (0, 0, 0, 0, None)

# --- WRITERS ---
async def add_message_stats(gid, uid, cid, wc, cc):
    await execute_query("INSERT OR IGNORE INTO user_stats (guild_id, user_id) VALUES (?, ?)", (gid, uid), commit=True)
    await execute_query("UPDATE user_stats SET msg_day=msg_day+1, msg_week=msg_week+1, msg_month=msg_month+1, msg_year=msg_year+1, msg_total=msg_total+1 WHERE guild_id=? AND user_id=?", (gid, uid), commit=True)
    if cid:
        await execute_query("INSERT OR IGNORE INTO channel_stats (guild_id, channel_id) VALUES (?, ?)", (gid, cid), commit=True)
        await execute_query("UPDATE channel_stats SET msg_count=msg_count+1 WHERE guild_id=? AND channel_id=?", (gid, cid), commit=True)

async def add_time_stats(gid, uid, cid, v=0, s=0):
    await execute_query("INSERT OR IGNORE INTO user_stats (guild_id, user_id) VALUES (?, ?)", (gid, uid), commit=True)
    if v: 
        await execute_query("UPDATE user_stats SET voice_day=voice_day+?, voice_week=voice_week+?, voice_month=voice_month+?, voice_year=voice_year+?, voice_total=voice_total+? WHERE guild_id=? AND user_id=?", (v,v,v,v,v, gid, uid), commit=True)
        if cid:
            await execute_query("INSERT OR IGNORE INTO channel_stats (guild_id, channel_id) VALUES (?, ?)", (gid, cid), commit=True)
            await execute_query("UPDATE channel_stats SET voice_duration=voice_duration+? WHERE guild_id=? AND channel_id=?", (v, gid, cid), commit=True)
    if s: await execute_query("UPDATE user_stats SET stream_day=stream_day+?, stream_week=stream_week+?, stream_month=stream_month+?, stream_year=stream_year+?, stream_total=stream_total+? WHERE guild_id=? AND user_id=?", (s,s,s,s,s, gid, uid), commit=True)

async def update_game_stats(gid, uid, gname, pt=0):
    if pt <= 0: return
    await execute_query("INSERT OR IGNORE INTO user_stats (guild_id, user_id) VALUES (?, ?)", (gid, uid), commit=True)
    await execute_query("UPDATE user_stats SET game_day=game_day+?, game_week=game_week+?, game_month=game_month+?, game_year=game_year+?, game_total=game_total+? WHERE guild_id=? AND user_id=?", (pt,pt,pt,pt,pt, gid, uid), commit=True)
    await execute_query("INSERT OR IGNORE INTO game_stats (guild_id, user_id, game_name) VALUES (?, ?, ?)", (gid, uid, gname), commit=True)
    await execute_query("UPDATE game_stats SET play_duration=play_duration+? WHERE guild_id=? AND user_id=? AND game_name=?", (pt, gid, uid, gname), commit=True)

async def add_xp(gid, uid, amount):
    s = await execute_query("SELECT level_system_active FROM settings WHERE guild_id=?", (gid,), fetchone=True)
    if not s or s[0] == 0: return False, 0
    await execute_query("INSERT OR IGNORE INTO user_stats (guild_id, user_id) VALUES (?, ?)", (gid, uid), commit=True)
    r = await execute_query("SELECT xp, level FROM user_stats WHERE guild_id=? AND user_id=?", (gid, uid), fetchone=True)
    xp, lvl = (r[0] or 0) + amount, r[1] or 1
    if xp >= lvl * 500:
        xp -= lvl * 500; lvl += 1
        await execute_query("UPDATE user_stats SET xp=?, level=? WHERE guild_id=? AND user_id=?", (xp, lvl, gid, uid), commit=True)
        return True, lvl
    await execute_query("UPDATE user_stats SET xp=? WHERE guild_id=? AND user_id=?", (xp, gid, uid), commit=True)
    return False, lvl

# --- READ ---
async def get_stats(gid, uid):
    u = await execute_query("SELECT * FROM user_stats WHERE guild_id=? AND user_id=?", (gid, uid), fetchone=True)
    g = await execute_query("SELECT game_name, play_duration FROM game_stats WHERE guild_id=? AND user_id=? ORDER BY play_duration DESC LIMIT 5", (gid, uid), fetchall=True)
    return u, g

async def get_top_leaderboard(gid, type_val):
    if "user_" in type_val:
        c = {"user_msg":"msg_total", "user_voice":"voice_total", "user_stream":"stream_total", "user_game":"game_total"}.get(type_val, "msg_total")
        return await execute_query(f"SELECT user_id, {c} FROM user_stats WHERE guild_id=? ORDER BY {c} DESC LIMIT 10", (gid,), fetchall=True)
    elif "channel_" in type_val:
        c = "msg_count" if type_val == "channel_msg" else "voice_duration"
        return await execute_query(f"SELECT channel_id, {c} FROM channel_stats WHERE guild_id=? ORDER BY {c} DESC LIMIT 10", (gid,), fetchall=True)
    return []

async def get_server_totals(gid):
    return await execute_query("SELECT SUM(msg_total), SUM(voice_total) FROM user_stats WHERE guild_id=?", (gid,), fetchone=True), None

async def get_rank_data(gid, uid):
    r = await execute_query("SELECT xp, level, rep, bg_url FROM user_stats WHERE guild_id=? AND user_id=?", (gid, uid), fetchone=True)
    if not r: return 0, 1, 0, None, 1
    rank = (await execute_query("SELECT COUNT(*) FROM user_stats WHERE guild_id=? AND (level > ? OR (level = ? AND xp > ?))", (gid, r[1], r[1], r[0]), fetchone=True))[0] + 1
    return r[0], r[1], r[2], r[3], rank

async def give_rep(gid, f_uid, t_uid):
    now = int(time.time())
    await execute_query("INSERT OR IGNORE INTO user_stats (guild_id, user_id) VALUES (?, ?)", (gid, f_uid), commit=True)
    l = (await execute_query("SELECT last_rep_time FROM user_stats WHERE guild_id=? AND user_id=?", (gid, f_uid), fetchone=True))[0] or 0
    if now - l < 86400: return False, l + 86400
    await execute_query("INSERT OR IGNORE INTO user_stats (guild_id, user_id) VALUES (?, ?)", (gid, t_uid), commit=True)
    await execute_query("UPDATE user_stats SET rep=rep+1 WHERE guild_id=? AND user_id=?", (gid, t_uid), commit=True)
    await execute_query("UPDATE user_stats SET last_rep_time=? WHERE guild_id=? AND user_id=?", (now, gid, f_uid), commit=True)
    return True, 0

async def set_bg_url(gid, uid, url):
    await execute_query("INSERT OR IGNORE INTO user_stats (guild_id, user_id) VALUES (?, ?)", (gid, uid), commit=True)
    await execute_query("UPDATE user_stats SET bg_url=? WHERE guild_id=? AND user_id=?", (url, gid, uid), commit=True)

# --- QUESTS ---
async def get_or_create_quests(gid, uid):
    now = time.localtime(); did = int(f"{now.tm_year}{now.tm_yday}")
    s = await execute_query("SELECT quest_system_active FROM settings WHERE guild_id=?", (gid,), fetchone=True)
    if not s or s[0] == 0: return None
    q = await execute_query("SELECT * FROM daily_quests WHERE guild_id=? AND user_id=? AND date_id=?", (gid, uid, did), fetchone=True)
    if q: return q
    await execute_query("INSERT INTO daily_quests (guild_id, user_id, date_id, q1_type, q1_target, q2_type, q2_target, q3_type, q3_target) VALUES (?, ?, ?, 'msg', 50, 'voice', 1800, 'game', 3600)", (gid, uid, did), commit=True)
    return await execute_query("SELECT * FROM daily_quests WHERE guild_id=? AND user_id=? AND date_id=?", (gid, uid, did), fetchone=True)

async def update_quest_progress(gid, uid, t, amt):
    q = await get_or_create_quests(gid, uid)
    if not q: return
    for i, idx in enumerate([3, 7, 11], 1):
        if q[idx] == t and not q[idx+3]:
            p = q[idx+2] + amt
            await execute_query(f"UPDATE daily_quests SET q{i}_progress=? WHERE guild_id=? AND user_id=? AND date_id=?", (p, gid, uid, q[2]), commit=True)
            if p >= q[idx+1]: await execute_query(f"UPDATE daily_quests SET q{i}_done=1 WHERE guild_id=? AND user_id=? AND date_id=?", (gid, uid, q[2]), commit=True)

# --- ADMIN ACTIONS (YENİ SİLME VE GERİ YÜKLEME) ---
async def set_daily_channel(gid, cid): await execute_query("INSERT OR IGNORE INTO settings (guild_id) VALUES (?)", (gid,), commit=True); await execute_query("UPDATE settings SET daily_channel_id=? WHERE guild_id=?", (cid, gid), commit=True)
async def set_role_system(gid, v): await execute_query("INSERT OR IGNORE INTO settings (guild_id) VALUES (?)", (gid,), commit=True); await execute_query("UPDATE settings SET role_system_active=? WHERE guild_id=?", (v, gid), commit=True)
async def set_level_system(gid, v): await execute_query("INSERT OR IGNORE INTO settings (guild_id) VALUES (?)", (gid,), commit=True); await execute_query("UPDATE settings SET level_system_active=? WHERE guild_id=?", (v, gid), commit=True)
async def set_quest_system(gid, v): await execute_query("INSERT OR IGNORE INTO settings (guild_id) VALUES (?)", (gid,), commit=True); await execute_query("UPDATE settings SET quest_system_active=? WHERE guild_id=?", (v, gid), commit=True)
async def set_gazete_system(gid, v): await execute_query("INSERT OR IGNORE INTO settings (guild_id) VALUES (?)", (gid,), commit=True); await execute_query("UPDATE settings SET gazete_system_active=? WHERE guild_id=?", (v, gid), commit=True)

# 1. VERİLERİ ÖNCE OKU, JSON YAP, ARŞİVE AT, SONRA SİL
async def archive_data(gid, uid=None):
    if uid: # TEK KULLANICI
        u_data = await execute_query("SELECT * FROM user_stats WHERE guild_id=? AND user_id=?", (gid, uid), fetchone=True)
        if u_data:
            # Row'u Dictionary'e çevirip saklayabiliriz ama basitlik için listeyi string yapıyorum
            await execute_query("INSERT INTO archived_data (guild_id, user_id, data_type, json_data) VALUES (?, ?, ?, ?)", (gid, uid, 'user_stats', json.dumps(u_data)), commit=True)
            await execute_query("DELETE FROM user_stats WHERE guild_id=? AND user_id=?", (gid, uid), commit=True)
            await execute_query("DELETE FROM game_stats WHERE guild_id=? AND user_id=?", (gid, uid), commit=True)
            return True
    else: # TÜM SUNUCU
        # Tüm user_stats'i çek
        all_users = await execute_query("SELECT * FROM user_stats WHERE guild_id=?", (gid,), fetchall=True)
        if all_users:
            await execute_query("INSERT INTO archived_data (guild_id, data_type, json_data) VALUES (?, ?, ?)", (gid, 'server_dump', json.dumps(all_users)), commit=True)
            await execute_query("DELETE FROM user_stats WHERE guild_id=?", (gid,), commit=True)
            await execute_query("DELETE FROM game_stats WHERE guild_id=?", (gid,), commit=True)
            await execute_query("DELETE FROM channel_stats WHERE guild_id=?", (gid,), commit=True)
            return True
    return False

# 2. ARŞİVDEN OKU, MEVCUT VERİNİN ÜSTÜNE EKLE (MERGE)
async def restore_data(gid, uid=None):
    try:
        # En son alınan yedeği bul
        if uid:
            row = await execute_query("SELECT json_data FROM archived_data WHERE guild_id=? AND user_id=? AND data_type='user_stats' ORDER BY id DESC LIMIT 1", (gid, uid), fetchone=True)
            if row:
                data = json.loads(row[0])
                # data formatı: [gid, uid, msg_day, msg_week... ] (Tablo sırasına göre)
                # Sadece Total değerleri eklemek yeterli: msg_total(6), voice_total(11), stream_total(16), game_total(21), xp(22)
                await execute_query("INSERT OR IGNORE INTO user_stats (guild_id, user_id) VALUES (?, ?)", (gid, uid), commit=True)
                await execute_query("""UPDATE user_stats SET 
                    msg_total = msg_total + ?, 
                    voice_total = voice_total + ?, 
                    stream_total = stream_total + ?, 
                    game_total = game_total + ?,
                    xp = xp + ?
                    WHERE guild_id=? AND user_id=?""", 
                    (data[6], data[11], data[16], data[21], data[22], gid, uid), commit=True)
                return True
        else:
            # Server Restore: En son server_dump'ı al
            row = await execute_query("SELECT json_data FROM archived_data WHERE guild_id=? AND data_type='server_dump' ORDER BY id DESC LIMIT 1", (gid,), fetchone=True)
            if row:
                users_list = json.loads(row[0])
                for u in users_list:
                    uid = u[1]
                    await execute_query("INSERT OR IGNORE INTO user_stats (guild_id, user_id) VALUES (?, ?)", (gid, uid), commit=True)
                    await execute_query("""UPDATE user_stats SET 
                        msg_total = msg_total + ?, 
                        voice_total = voice_total + ?, 
                        stream_total = stream_total + ?, 
                        game_total = game_total + ?,
                        xp = xp + ?
                        WHERE guild_id=? AND user_id=?""", 
                        (u[6], u[11], u[16], u[21], u[22], gid, uid), commit=True)
                return True
    except Exception as e:
        print(f"Restore Error: {e}")
    return False