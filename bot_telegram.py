# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Bot Telegram AM Preset Finder — kirim link vt, terima link preset.
# Tanpa dependensi baru: hanya requests + index.py (AMPresetFinder).
#
# Cara pakai:
#   1. Buat bot via @BotFather di Telegram, salin tokennya.
#   2. Jalankan:  BOT_TOKEN=123456:ABC-DEF python bot_telegram.py
#      (atau: python bot_telegram.py 123456:ABC-DEF)
#   3. Chat ke bot: kirim link video TikTok (boleh vt/vm.tiktok.com pendek).
#      Tambahkan kata "hemat" untuk mode cepat, mis: "<link> hemat"
#
# Perilaku: mode LENGKAP default (tidak ada link hilang), filter domain cerdas
# yang sama dengan CLI (alightcreative.com / alight.link / drive.google.com).

import os
import re
import sys
import time
import json
import requests
from typing import List, Dict, Any, Optional

from index import AMPresetFinder

# === KONFIG ===
BOT_TOKEN = os.environ.get("BOT_TOKEN", sys.argv[1] if len(sys.argv) > 1 else "")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""
POLL_TIMEOUT = 30       # long-poll getUpdates (detik)
MAX_MSG = 3500          # batas aman di bawah limit Telegram 4096
DEFAULT_DOMAINS = list(AMPresetFinder.PRESET_DOMAINS)

TIKTOK_URL_RE = re.compile(r"https?://(?:www\.|vm\.|vt\.)?tiktok\.com\S*", re.IGNORECASE)
SHORT_URL_RE = re.compile(r"https?://(?:vm|vt)\.tiktok\.com/\S+", re.IGNORECASE)

HELP_TEXT = (
    "🎨 *AM Preset Finder Bot*\n\n"
    "Kirim link video TikTok (boleh link pendek vt/vm), "
    "bot akan memindai komentar dan membalas link preset Alight Motion.\n\n"
    "Contoh:\n"
    "`https://vt.tiktok.com/ZSbHuVCGU/`\n"
    "`https://vt.tiktok.com/ZSbHuVCGU/ hemat` _(mode cepat)_\n\n"
    "Domain yang diambil: `alightcreative.com`, `alight.link`, `drive.google.com`.\n"
    "Mode default: *lengkap* (balasan tetap dicek, tidak ada link hilang)."
)


def tg_api(method: str, params: Optional[dict] = None, timeout: int = 40) -> dict:
    """Panggil Bot API Telegram, return JSON."""
    r = requests.post(f"{API_BASE}/{method}", json=params or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def send_msg(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """Kirim 1 pesan (sudah harus <= limit)."""
    return tg_api("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": parse_mode,
                                  "disable_web_page_preview": True})


def send_chunked(chat_id: int, header: str, items: List[str]):
    """Kirim list bernomor dalam beberapa pesan agar tidak melebihi limit."""
    buf = header
    for i, item in enumerate(items, 1):
        line = f"\n{i}. {item}"
        if len(buf) + len(line) > MAX_MSG:
            send_msg(chat_id, buf)
            buf = f"(lanjutan){line}"
        else:
            buf += line
    if buf.strip():
        send_msg(chat_id, buf)


def find_tiktok_url(text: str) -> Optional[str]:
    """Ambil URL TikTok pertama dari teks chat."""
    m = SHORT_URL_RE.search(text or "")
    if m:
        return m.group(0).rstrip(".,;!?)'\"")
    m = TIKTOK_URL_RE.search(text or "")
    if m:
        return m.group(0).rstrip(".,;!?)'\"")
    return None


def scan_presets(video_url: str, hemat: bool = False) -> Dict[str, Any]:
    """Jalankan finder non-interaktif, return ringkasan + link unik."""
    finder = AMPresetFinder()
    vid = finder._get_video_id(video_url)
    if not vid:
        return {"ok": False, "error": "Link tidak valid / Video ID tidak ditemukan."}
    finder.video_url = video_url
    try:
        threads = finder._get_all_comments_and_replies(
            preset_domains=DEFAULT_DOMAINS, skip_replies_if_parent_miss=hemat)
    except Exception as e:
        return {"ok": False, "error": f"Gagal fetch: {e}"}
    flat = finder._collect_preset_links(threads, DEFAULT_DOMAINS)
    seen: Dict[str, dict] = {}
    for e in flat:
        seen.setdefault(e["url"], e)
    return {"ok": True, "video_id": vid, "threads": len(threads),
            "replies": sum(len(t.get("replies", [])) for t in threads),
            "links": list(seen.values())}


def handle_text(chat_id: int, text: str):
    """Proses 1 pesan masuk."""
    t = (text or "").strip()
    if t.startswith("/start") or t.startswith("/help"):
        send_msg(chat_id, HELP_TEXT)
        return
    url = find_tiktok_url(t)
    if not url:
        send_msg(chat_id, "Kirim link video TikTok (contoh: `https://vt.tiktok.com/XXXX/`). Ketik /help untuk panduan.")
        return
    hemat = "hemat" in t.lower()
    status = send_msg(chat_id, f"🔍 Memindai komentar…\n`{url}`\nMode: {'hemat (cepat)' if hemat else 'lengkap'}",
                      )
    try:
        res = scan_presets(url, hemat=hemat)
    except Exception as e:
        send_msg(chat_id, f"❌ Error tak terduga: `{e}`")
        return
    if not res["ok"]:
        send_msg(chat_id, f"❌ {res['error']}")
        return
    links = res["links"]
    if not links:
        send_msg(chat_id, f"⚠ Tidak ada link preset ditemukan (scan {res['threads']} thread). Coba video lain.")
        return
    kind_label = {"alight_link": "Alight", "drive_xml": "Drive", "preset_link": "Preset"}
    header = (f"🎨 *{len(links)} link preset* (dari {res['threads']} thread)\n"
              f"Video ID: `{res['video_id']}`")
    items = [f"{u['url']} _(_{kind_label.get(u['kind'], u['kind'])} | @{u['username']}_)_" for u in links]
    send_chunked(chat_id, header, items)


def run_polling():
    """Loop long-poll getUpdates."""
    if not BOT_TOKEN:
        print("BOT_TOKEN kosong. Cara pakai: BOT_TOKEN=<token> python bot_telegram.py")
        sys.exit(1)
    # Validasi token
    me = tg_api("getMe")
    print(f"Bot aktif sebagai @{me['result'].get('username')} — menunggu chat…")
    offset = 0
    seen_updates = set()  # cegah update yang sama diproses 2x (redelivery Telegram)
    while True:
        try:
            data = tg_api("getUpdates", {"offset": offset, "timeout": POLL_TIMEOUT}, timeout=POLL_TIMEOUT + 10)
        except Exception as e:
            print(f"getUpdates error (retry 3s): {e}")
            time.sleep(3)
            continue
        for upd in data.get("result", []):
            offset = upd["update_id"] + 1
            if upd["update_id"] in seen_updates:
                continue
            seen_updates.add(upd["update_id"])
            if len(seen_updates) > 1000:
                seen_updates.clear()
            msg = upd.get("message") or upd.get("edited_message") or {}
            chat = msg.get("chat", {})
            text = msg.get("text", "")
            if chat and text:
                try:
                    handle_text(chat["id"], text)
                except Exception as e:
                    print(f"handle error: {e}")
                    try:
                        send_msg(chat["id"], f"❌ Error: `{e}`")
                    except Exception:
                        pass


if __name__ == "__main__":
    run_polling()
