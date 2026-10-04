# 💬 TikTok Comment Scraper

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/author-Nihongo-red.svg)](https://github.com/Ikyletwar)
[![Made with ❤️](https://img.shields.io/badge/made%20with-❤️-red.svg)]()

CLI tool untuk mengambil **semua komentar utama + semua balasan** dari video TikTok apa pun, dengan **filter link (`https`) langsung saat fetch (streaming)**, progress live, dan ekspor ganda **JSON (nested) + Excel (flat)**.

Dibuat oleh: [Nihongo](https://github.com/Ikyletwar).

---

## 📑 Daftar Isi

- [Fitur](#-fitur)
- [Demo](#️-demo--screenshot)
- [Arsitektur](#️-arsitektur)
- [Endpoint API](#-endpoint-api)
- [Prerequisites](#️-prerequisites)
- [Instalasi](#-instalasi)
- [Penggunaan](#-penggunaan)
- [Mode Filter Link](#-mode-filter-link-streaming)
- [Skema Output](#-skema-output)
- [Contoh Sesi Nyata](#-contoh-sesi-nyata)
- [Struktur Repo](#-struktur-repo)
- [Konfigurasi Lanjutan](#️-konfigurasi-lanjutan)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#️-disclaimer)
- [Berkontribusi](#-berkontribusi)
- [Lisensi](#-lisensi)
- [Author](#-author)

---

## 🌟 Fitur

| # | Fitur | Keterangan |
|---|-------|------------|
| 1 | 🎨 CLI interaktif | Banner `pyfiglet`, panel/tabel/progress `rich`, warna cerah |
| 2 | 💬 Komentar + balasan penuh | Paginasi `cursor` + `has_more`, `count=50` per request |
| 3 | 🔗 Filter link streaming | Keyword `https` dicek **per item saat diterima**, bukan di akhir. Progress menampilkan `Scan / Match / Balasan match` live |
| 4 | ⚡ 2 mode fetch | `lengkap` (cek balasan walau induk tidak match) vs `hemat` (skip request balasan jika induk tidak match) |
| 5 | 📊 Statistik video | Caption, author, views, likes, comment count, shares, create time via `api/video/detail/` |
| 6 | 💾 Ekspor ganda | JSON nested (`comments[].replies[]`) + Excel flat (`Komentar Utama` / `Balasan`) |
| 7 | 🧩 Class-based | Satu class `TikTokScraper` di `index.py`, mudah di-import sebagai library |
| 8 | 🛡️ Error handling | `403` (privat/dihapus/rate-limit), timeout, JSON abnormal, `total_reply` kosong |
| 9 | 🔧 Dependency checker | `server.py` cek + auto-`pip install` (`requests,pandas,pyfiglet,rich,jmespath,openpyxl`) |

---

## 🖼️ Demo / Screenshot

![TikTok Scraper Demo](img/cmd.png)

---

## 🏗️ Arsitektur

```
index.py
└── class TikTokScraper
    ├── __init__()                    # requests.Session + header browser Chrome 108
    ├── _print_banner()
    ├── _get_video_id(url)            # dukung vm.tiktok.com / vt.tiktok.com (HEAD redirect) + /video/ID
    ├── _get_video_details()          # GET api/video/detail/ + jmespath itemInfo.itemStruct
    ├── _get_default_video_details()  # fallback N/A saat 403/privat
    ├── _display_video_details()
    ├── _parse_comment(json)          # jmespath: cid, user.unique_id, nickname, text, create_time, avatar, digg_count, reply_comment_total
    ├── _format_timestamp() / _format_number()
    ├── _get_replies(cid, total, progress, keyword)              # GET api/comment/list/reply/, filter per-balasan
    ├── _get_all_comments_and_replies(keyword, skip_hemat)      # GET api/comment/list/, filter per-komentar, dispatch reply
    ├── _filter_by_keyword(list, keyword)  # filter pasca-proses (kompatibilitas, tidak dipakai di jalur utama)
    ├── _save_to_json() / _save_to_excel() # flat: Tipe, ID_Komentar_Induk, ID_Komentar, Username, Nickname, Komentar, Waktu, Jumlah_Like, Total_Balasan
    ├── _display_summary_table()       # 20 komentar teratas
    ├── _display_completion_screen()
    └── run()                         # orkestrasi: banner → URL → detail → prompt filter → fetch streaming → save → tampil
```

Call graph fetch:

```
run(keyword="https")
└── _get_all_comments_and_replies
    ├── GET api/comment/list/ (cursor loop)
    ├── _parse_comment → cek parent_match
    └── _get_replies (jika total_reply>0 dan tidak di-skip)
        ├── GET api/comment/list/reply/ (cursor loop)
        └── _parse_comment → cek keyword per-balasan
```

`server.py` bukan scraper — hanya bootstrap dependency checker (tampilan `rich`/`pyfiglet` dulu, lalu cek semua paket).

---

## 🔌 Endpoint API

Base tidak resmi (dapat berubah sewaktu-waktu oleh TikTok):

| Fungsi | Method | URL | Params |
|--------|--------|-----|--------|
| Detail video | GET | `https://www.tiktok.com/api/video/detail/` | `aid=1988`, `aweme_id=<video_id>` |
| Komentar utama | GET | `https://www.tiktok.com/api/comment/list/` | `aid=1988`, `aweme_id`, `count=50`, `cursor` |
| Balasan | GET | `https://www.tiktok.com/api/comment/list/reply/` | `aid=1988`, `aweme_id`, `comment_id`, `count=50`, `cursor` |

Respons: `{ comments: [...], has_more: bool, cursor: int, status_code: int }`.
Paginasi berhenti saat `comments == []` atau `has_more == false`.
Jeda `sleep(1)` antar page komentar, `sleep(0.5)` antar page balasan untuk menahan rate-limit.

> TikTok tidak menyediakan filter server-side (`?filter=https` tidak ada), jadi filter keyword selalu client-side. Mode streaming tetap harus memindai semua page — yang dihemat adalah memori/file output (mode lengkap) atau jumlah request balasan (mode hemat).

---

## ⚙️ Prerequisites

- **Python 3.8+**
- Koneksi internet langsung ke `tiktok.com` (tanpa proxy khusus)
- Terminal yang mendukung ANSI color (Windows Terminal / Linux / macOS)

---

## 📦 Instalasi

```bash
git clone https://github.com/Ikyletwar/tiktok-scraper.git
cd tiktok-scraper
```

Opsi A — otomatis (disarankan):

```bash
python server.py
# cek rich + pyfiglet dulu, lalu requests, pandas, pyfiglet, rich, jmespath
```

Opsi B — manual:

```bash
pip install requests pandas pyfiglet rich jmespath openpyxl
```

> `openpyxl` dibutuhkan oleh `pandas.DataFrame.to_excel()`. Jika belum ada, `python server.py` + `pip install openpyxl` akan menutup error `Missing optional dependency 'openpyxl'`.

---

## 🚀 Penggunaan

Perintah yang benar (nama file `index.py`):

```bash
python index.py
```

Alur interaktif:

1. Tempel link video saat prompt `» Masukkan Link Video TikTok`, contoh:
   - `https://www.tiktok.com/@rvennprst/video/7686108135475580181`
   - `https://vt.tiktok.com/ZSUc5CWKy/` (short link otomatis di-resolve via `HEAD`)
2. Tunggu detail video (jika `403` → dipakai fallback `author=N/A`, scraping komentar tetap jalan).
3. Jawab prompt filter:
   - `» Hanya ambil komentar berisi link (https)? Filter langsung saat fetch [y/n] (y):`
   - Jika `y`, jawab mode: `» Mode hemat ...? y=cepat tapi balasan-link bisa hilang, n=lengkap [y/n] (n):`
4. Progress menampilkan `Scan` (total dipindai) vs `Match` (thread disimpan) secara live.
5. Hasil tersimpan sebagai `tiktok_comments_<VIDEO_ID>.json` + `.xlsx`, lalu tabel 20 teratas + layar `COMPLETE!` ditampilkan.

Sebagai library:

```python
from index import TikTokScraper
s = TikTokScraper()
s.video_id = "7686108135475580181"
data = s._get_all_comments_and_replies(keyword="https", skip_replies_if_parent_miss=False)
print(len(data))
```

---

## 🔗 Mode Filter Link (Streaming)

| Mode | Cara pilih | Request balasan | Hasil | Cocok untuk |
|------|------------|-----------------|-------|-------------|
| Lengkap (default) | `y` lalu `n` | Tetap fetch semua balasan untuk dicek satu per satu | Induk tanpa link tapi balasannya ada link **tetap disimpan sebagai konteks** | Panen link exhaustive, tidak ada yang hilang |
| Hemat | `y` lalu `y` | Skip `GET reply` jika induk tidak mengandung keyword | Hanya induk ber-link yang disimpan. Lebih cepat, request jauh lebih sedikit | Video raksasa, butuh cepat, rela kehilangan reply-only link |
| Tanpa filter | `n` | Fetch semua | Semua komentar + balasan | Arsip penuh / analisis sentimen |

Contoh hasil uji mock (3 komentar, 2 punya balasan):

- `lengkap` → `[(1->[1r1]), (2->[])]` (thread `1` dipertahankan karena balasannya match)
- `hemat` → `[(2->[])]` (thread `1` hilang)
- `nofilter` → semua 3 thread

Ganti keyword (misal hanya `mega.nz`):

```python
s._get_all_comments_and_replies(keyword="mega.nz")
# atau pasca-proses:
s._filter_by_keyword(all_comments, keyword="drive.google")
```

Pencocokan selalu **case-insensitive** dan **aman terhadap `None`**.

---

## 📄 Skema Output

### JSON — `tiktok_comments_<VIDEO_ID>.json`

```json
{
  "caption": "@author: caption video",
  "date_now": "2025-10-24T12:19:48",
  "video_url": "https://...",
  "video_stats": { "view_count": 0, "like_count": 0, "comment_count": 0, "share_count": 0 },
  "comments": [
    {
      "cid": "7554751430977897223",
      "username": "Siapa?",
      "nickname": "Anony",
      "comment": "alat nya seharga beat...",
      "create_time": "2025-09-27 12:54:05 UTC",
      "avatar": "https://...",
      "digg_count": 17,
      "total_reply": 1,
      "replies": [
        {
          "cid": "7555830389871051536",
          "username": "Siapa?",
          "nickname": "Anony",
          "comment": "makanya ga usah...",
          "create_time": "2025-09-30 10:41:02 UTC",
          "avatar": "https://...",
          "digg_count": 1,
          "total_reply": null,
          "replies": []
        }
      ]
    }
  ]
}
```

### Excel — `tiktok_comments_<VIDEO_ID>.xlsx`

Flat, satu baris per komentar/balasan:

| Tipe | ID_Komentar_Induk | ID_Komentar | Username | Nickname | Komentar | Waktu | Jumlah_Like | Total_Balasan |
|------|-------------------|-------------|----------|----------|----------|-------|-------------|---------------|
| Komentar Utama | (kosong) | cid induk | ... | ... | teks | `YYYY-MM-DD HH:MM:SS UTC` | int | int |
| Balasan | cid induk | cid balasan | ... | ... | teks | ... | int | 0 |

---

## ✅ Contoh Sesi Nyata

Video `7686108135475580181` (mode lengkap, keyword `https`):

```
✅ Scan 268 komentar, dapat 22 thread + 16 balasan mengandung 'https'.
💾 tiktok_comments_7686108135475580181.json ✅
💾 tiktok_comments_7686108135475580181.xlsx ✅
```

Isi dominan: `https://alightcreative.com/am/share/...` (bagi preset XML), plus `https://vt.tiktok.com/...`.
Video `7554738914985020690` (17 induk / 17 balasan) → `0` match `https`/`http`, artinya tidak ada link sama sekali.

---

## 🗂️ Struktur Repo

```
tiktok-scraper/
├── index.py        # scraper utama (class TikTokScraper)
├── server.py       # dependency checker + auto-install
├── README.md       # dokumentasi ini
├── .gitignore      # __pycache__, *.pyc, output tiktok_comments_* 
├── img/
│   └── cmd.png     # screenshot demo
└── tiktok_comments_<ID>.json / .xlsx  # hasil (di-ignore git, tidak di-push)
```

---

## 🛠️ Konfigurasi Lanjutan

- Ubah ukuran page: `count: 50` di `_get_all_comments_and_replies()` / `_get_replies()` (maksimal praktis 50–100).
- Ubah jeda: `time.sleep(1)` (komentar) / `time.sleep(0.5)` (balasan) — naikkan jika sering `429/403`.
- Ganti User-Agent di `__init__()` jika diblokir.
- Timeout per request: `timeout=10` di semua `session.get()`.

---

## ❓ Troubleshooting

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| `403 Forbidden` di `api/video/detail/` | Video privat/dihapus atau IP di-rate-limit | Scraper lanjut dengan fallback `N/A`; coba VPN/IP lain atau tunggu |
| `Selesai Komentar Utama Total: 0` | Video tanpa komentar / semua komentar difilter privat | Jawab `n` (tanpa filter) untuk memastikan |
| `Missing optional dependency 'openpyxl'` | `openpyxl` belum install | `pip install openpyxl` |
| Dijalankan sebagai `python tiktok_scrapper.py` → `No such file` | Nama file salah (typo dobel-p) | Nama yang benar: `python index.py` |
| Filter `y` menghasilkan `0 match` | Memang tidak ada link di thread itu | Coba keyword `http` / cek file tanpa filter dulu |
| Balasan-link hilang di mode hemat | Sesuai desain hemat (skip fetch) | Ulangi dengan mode `lengkap` (`n`) |

---

## ⚠️ Disclaimer

Scraping TikTok melanggar **Syarat dan Ketentuan (ToS)** mereka. Skrip ini membuat **banyak request API** dan dapat menyebabkan blokir IP sementara/permanen. Gunakan dengan risiko sendiri dan secara bertanggung jawab.

---

## 🤝 Berkontribusi

Fork → buat branch → pull request. Untuk bug, buka issue dengan menyertakan: video ID (bukan full URL privat), log terminal, dan `python --version` + `pip freeze`.

---

## 📜 Lisensi

MIT. Lihat file `LICENSE` (tambahkan jika belum ada).

---

## 👨‍💻 Author

Dibuat dengan ❤️ oleh [Nihongo](https://github.com/Ikyletwar).
