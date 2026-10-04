<div align="center">

# 🎨 AM Preset Finder

### Temukan link preset Alight Motion yang tersebar di komentar TikTok — dalam hitungan detik.

[![Python](https://img.shields.io/badge/python-3.8+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-22c55e.svg?style=for-the-badge)](LICENSE)
[![Author](https://img.shields.io/badge/author-Nihongo-ef4444.svg?style=for-the-badge)](https://github.com/Ikyletwar)
[![Platform](https://img.shields.io/badge/runs_on-PC_%7C_Termux-8b5cf6.svg?style=for-the-badge)](#-instalasi)

*Filter domain cerdas · Streaming saat fetch · CLI-only ringan · Print link siap copy*

Dibuat dengan ❤️ oleh **[Nihongo](https://github.com/Ikyletwar)**

</div>

---

## 📑 Daftar Isi

- [Kenapa AM Preset Finder?](#-kenapa-am-preset-finder)
- [Fitur Unggulan](#-fitur-unggulan)
- [Demo](#️-demo)
- [Cara Kerja Singkat](#-cara-kerja-singkat)
- [Instalasi](#-instalasi)
- [Penggunaan](#-penggunaan)
- [Mode Filter](#-mode-filter)
- [Domain Preset Terkonfirmasi](#-domain-preset-terkonfirmasi)
- [Tampilan Console](#-tampilan-console)
- [Ekspor File (Opsional)](#-ekspor-file-opsional)
- [Skema Data](#-skema-data)
- [Contoh Sesi Nyata](#-contoh-sesi-nyata)
- [Struktur Repo & API Internal](#️-struktur-repo--api-internal)
- [Konfigurasi Lanjutan](#️-konfigurasi-lanjutan)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#️-disclaimer)
- [Berkontribusi](#-berkontribusi)
- [Lisensi & Author](#-lisensi--author)

---

## 💎 Kenapa AM Preset Finder?

Komentar video preset Alight Motion penuh dengan orang berbagi link — tapi linknya tenggelam di ratusan komentar basa-basi (*"presetnya mana bang"*, *"bagi dong"*). Tool ini memindai **semua komentar + semua balasan**, menyaring hanya yang mengandung **link preset asli**, lalu **me-print full URL-nya langsung di layar** — siap copy, tanpa buka file.

| Tanpa tool | Dengan AM Preset Finder |
|---|---|
| Scroll ratusan komentar manual | Scan otomatis + progress live |
| Link `vt.tiktok.com` / spam ikut kebawa | Hanya `alightcreative.com` / `alight.link` / `drive.google.com` yang lolos |
| Copy satu-satu dari HP | Daftar bernomor + list mentah satu URL per baris |

---

## ✨ Fitur Unggulan

| | Fitur | Detail |
|---|---|---|
| 🧠 | **Filter domain cerdas** | Bukan sekadar cari kata `https`. URL diekstrak via regex, domain dinormalisasi (`www.`/caps/subdomain aman), lalu dicocokkan ke daftar terkonfirmasi. `vt.tiktok.com` otomatis dibuang. |
| ⚡ | **Streaming saat fetch** | Komentar dicek **per item saat diterima dari API**, bukan ditampung semua dulu. Progress live: `Scan / Preset / Balasan preset`. |
| 🎭 | **2 mode fetch** | `Lengkap` — balasan tetap dicek walau induknya bukan preset (tidak ada link hilang). `Hemat` — skip request balasan jika induk bukan preset (jauh lebih cepat). |
| 🖨️ | **Print langsung di console** | Panel bernomor full-URL + tabel sumber (`User`/`Jenis`/`induk`-`balasan`) + list mentah tanpa wrap untuk copy-paste. Duplikat di-dedup (`dibagikan 2x`). |
| 📱 | **Ringan & Termux-ready** | Default **CLI-only tanpa tulis file**. `pandas` opsional — tanpanya otomatis fallback CSV. |
| 🎨 | **CLI premium** | Banner `pyfiglet`, panel/tabel/progress `rich`, klasifikasi jenis link (`Alight Link` / `Drive XML`). |
| 🧩 | **Siap jadi library** | `from index import AMPresetFinder` (`TikTokScraper` tetap tersedia sebagai alias). |

---

## 🖼️ Demo

![AM Preset Finder Demo](img/cmd.png)

---

## ⚙️ Cara Kerja Singkat

```
URL video → ekstrak video_id → paginasi komentar (cursor/has_more, 50/page)
  → tiap komentar: ekstrak URL → cek domain preset?
      → ya: simpan thread (+ fetch & saring balasannya)
      → tidak: hemat? buang : fetch balasan & cek (balasan ber-preset tetap disimpan sebagai konteks)
  → print tabel + link preset + COMPLETE!
```

> TikTok tidak punya filter server-side, jadi semua page tetap dipindai — yang cerdas adalah **penyaringannya**: regex URL + normalisasi domain + klasifikasi jenis, per item, saat streaming.

---

## 📦 Instalasi

```bash
git clone https://github.com/Ikyletwar/tiktok-scraper.git
cd tiktok-scraper
```

**PC / Laptop:**

```bash
pip install --upgrade pip
pip install requests rich pyfiglet jmespath
python server.py   # cek + auto-install dependensi (opsional)
```

**Termux (Android):**

```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/Ikyletwar/tiktok-scraper.git
cd tiktok-scraper
pip install --upgrade pip
pip install requests rich pyfiglet jmespath
```

> Tanpa `pandas`/`openpyxl` pun jalan penuh (mode CLI-only). Tambahkan keduanya hanya jika butuh ekspor `.xlsx`.

---

## 🚀 Penggunaan

```bash
python index.py
```

1. Tempel link video saat prompt — mendukung link penuh maupun pendek:
   - `https://www.tiktok.com/@user/video/7686108135475580181`
   - `https://vt.tiktok.com/ZSbHuVCGU/` (otomatis di-resolve)
2. `» Hanya ambil komentar ber-link preset AM?` → `y`
3. `» Mode hemat?` → `n` = lengkap (disarankan), `y` = cepat
4. Tunggu progress `Scan / Preset / Balasan preset`, lalu copy link dari layar.

Sebagai library:

```python
from index import AMPresetFinder
s = AMPresetFinder()
s.video_id = "7686108135475580181"
threads = s._get_all_comments_and_replies(
    preset_domains=AMPresetFinder.PRESET_DOMAINS,  # default cerdas
    skip_replies_if_parent_miss=False,            # False = lengkap, True = hemat
)
links = s._collect_preset_links(threads)
print(links[0]["url"], links[0]["kind"])
```

---

## 🎭 Mode Filter

| Mode | Pilih | Request balasan | Hasil | Cocok untuk |
|---|---|---|---|---|
| **Lengkap** (default) | `y` → `n` | Semua balasan di-fetch & dicek | Induk biasa + balasan ber-preset **tetap disimpan sebagai konteks**. Nol link hilang. | Panen exhaustive |
| **Hemat** | `y` → `y` | Di-skip bila induk bukan preset | Hanya thread ber-preset. Jauh lebih sedikit request. | Video raksasa / koneksi lemot |
| **Tanpa filter** | `n` | Semua | Arsip penuh semua komentar | Riset / sentimen |

---

## 🔗 Domain Preset Terkonfirmasi

```python
PRESET_DOMAINS = [
    "alightcreative.com",  # Link Resmi: .../am/share/... → terbuka otomatis di Alight Motion
    "alight.link",         # Link pendek resmi → impor otomatis ke AM
    "drive.google.com",    # File XML mentah: .../file/d/... → unduh lalu impor manual
]
```

Klasifikasi otomatis (`kind`):

| `kind` | Arti | Contoh |
|---|---|---|
| `alight_link` | Share resmi, klik → impor otomatis | `https://alightcreative.com/am/share/u/…/p/…`, `https://alight.link/7sgfjYKk2fK1CqUu8` |
| `drive_xml` | XML mentah di Drive | `https://drive.google.com/file/d/1jONrJttOMJBUp_UTuKnC7JAGRoW8yq4F/view` |
| `preset_link` | Domain preset, pola lain | `https://alightcreative.com/blog/...` (tetap disimpan) |
| *dibuang* | Bukan preset | `vt.tiktok.com`, `tiktok.com`, link lain |

Pencocokan **case-insensitive**, tahan `www.`, sub-domain, tanda baca tepi (`(url).`, `url...`), dan aman terhadap teks kosong/`None`.

<details>
<summary><b>Contoh nyata yang lolos ✅ / dibuang ❌</b></summary>

✅ `https://alightcreative.com/am/share/u/sAcfaVla13XF1gd6h08dnyU0SUS2/p/2cd68b9e-a8f9-45b7-a6ab-ab5dcd5d9ae7`
✅ `https://alight.link/7sgfjYKk2fK1CqUu8`
✅ `https://drive.google.com/file/d/1oOsPD4mXSuzSMQ-GTRzH-wyNVpDrfw89/view`
❌ `https://vt.tiktok.com/ZSqgnDSDk/` (bukan preset)
❌ `presetnya mana bang` (tanpa link)

</details>

---

## 🖥️ Tampilan Console

Setiap run yang menemukan preset menampilkan 3 lapis (berurutan):

1. **Tabel ringkasan** — `Tinjauan Preset AM` (20 teratas: user, link terpotong, likes, jml balasan).
2. **Panel link** — `🎨 N Link Preset Ditemukan`: full URL bernomor + `(Jenis | @user | dibagikan Nx)`.
3. **Tabel sumber** — tiap URL unik + user pertama + asal `induk`/`balasan`.
4. **List mentah** — satu URL per baris, `soft_wrap` (tidak terpotong logikanya) — bagian terbaik untuk copy-paste / pipe ke file:

```bash
python index.py | grep -o 'https://[^ ]*'
```

---

## 💾 Ekspor File (Opsional)

Default **mati** (CLI-only, cocok untuk Termux / HP). Aktifkan di baris atas `index.py`:

```python
ENABLE_SAVE_JSON = True    # → am_preset_<VIDEO_ID>.json
ENABLE_SAVE_EXCEL = True   # → am_preset_<VIDEO_ID>.xlsx (butuh pandas+openpyxl) / .csv fallback
```

| File | Isi |
|---|---|
| `am_preset_<ID>.json` | Nested `comments[].replies[]`, tiap item membawa `preset_links: [{url, domain, kind}]` + `preset_kinds` |
| `am_preset_<ID>.xlsx` / `.csv` | Flat per baris + kolom `Link_Preset` (`; `-joined) dan `Jenis_Preset` |

---

## 🧾 Skema Data

Komentar (induk & balasan) setelah parsing:

```json
{
  "cid": "7554751430977897223",
  "username": "epan_761",
  "nickname": "FAN|~astro",
  "comment": "nih https://alight.link/abc123",
  "create_time": "2025-09-27 12:54:05 UTC",
  "avatar": "https://...",
  "digg_count": 17,
  "total_reply": 1,
  "preset_links": [{ "url": "https://alight.link/abc123", "domain": "alight.link", "kind": "alight_link" }],
  "preset_kinds": ["alight_link"],
  "replies": []
}
```

---

## ✅ Contoh Sesi Nyata

Video `7489012581231824136` (mode hemat, 13 komentar dipindai):

```
✅ Scan 13 komentar, dapat 2 thread + 0 balasan preset
🎨 1 Link Preset Ditemukan (dibagikan 2x)
1. https://alightcreative.com/am/share/u/GIZDmEkL9OhCOYGci3w6Xrm9FjM2/p/7yU94IwVCo-682954025947399b
```

Video `7686108135475580181` (mode lengkap): `268` komentar → `22` thread + `16` balasan ber-preset, dominan `alightcreative.com/am/share/...`.

---

## 🏗️ Struktur Repo & API Internal

```
tiktok-scraper/
├── index.py        # AMPresetFinder: fetch + filter + display + ekspor
├── server.py       # dependency checker + auto-install
├── README.md       # dokumentasi ini
├── .gitignore      # __pycache__, *.pyc, am_preset_* / tiktok_comments_* (legacy)
└── img/cmd.png     # screenshot demo
```

| Metode | Peran |
|---|---|
| `_get_video_id(url)` | Ekstrak ID; resolve `vm/vt.tiktok.com` via `HEAD` |
| `_get_video_details()` | `GET api/video/detail/` + `jmespath`; fallback `N/A` saat `403` |
| `_parse_comment()` | Normalisasi 1 komentar + `preset_links` |
| `extract_urls / extract_preset_links / has_preset_link` | Mesin filter domain (classmethod, bisa dipakai mandiri) |
| `_get_replies(cid, total, progress, preset_domains)` | Paginasi balasan + saring per item |
| `_get_all_comments_and_replies(preset_domains, skip_hemat)` | Paginasi komentar + orkestrasi filter streaming |
| `_collect_preset_links / _display_preset_links` | Kumpulkan + print link ke console |
| `_save_to_json / _save_to_excel` | Ekspor (di belakang toggle) |
| `run()` | Orkestrasi interaktif penuh |

Endpoint (tidak resmi, dapat berubah): `api/video/detail/`, `api/comment/list/`, `api/comment/list/reply/` — params `aid=1988`, `count=50`, `cursor`; berhenti saat `comments == []` / `has_more == false`; jeda `1s`/`0.5s` anti rate-limit.

---

## 🛠️ Konfigurasi Lanjutan

- **Tambah domain preset** — edit `PRESET_DOMAINS`, mis. `"mega.nz"`, `"mediafire.com"`.
- **Ukuran page** — `count: 50` (praktis 50–100).
- **Jeda** — `time.sleep(1)` komentar / `0.5` balasan; naikkan bila sering `429/403`.
- **User-Agent / timeout** — di `__init__()` dan tiap `session.get(timeout=10)`.

---

## ❓ Troubleshooting

| Gejala | Penyebab | Solusi |
|---|---|---|
| `403` di `api/video/detail/` | Video privat/dihapus atau IP di-rate-limit (umum di IP seluler) | Otomatis fallback `N/A`, komentar tetap diambil; coba IP lain / tunggu |
| `Total: 0` / tidak ada preset | Video memang tanpa link preset | Jawab `n` (tanpa filter) untuk memastikan |
| `Missing optional dependency 'openpyxl'` | Ekspor Excel tanpa `openpyxl` | `pip install openpyxl pandas`, atau biarkan CLI-only |
| `No such file: tiktok_scrapper.py` | Typo nama lama (dobel-p) | Yang benar: `python index.py` |
| Balasan ber-preset hilang (hemat) | Sesuai desain hemat | Ulangi dengan mode lengkap (`n`) |
| Link terpotong saat copy dari panel | Wrap visual panel (bukan data) | Copy dari bagian **list mentah** paling bawah |

---

## ⚠️ Disclaimer

Scraping melanggar **ToS TikTok**; tool ini membanjiri API dengan banyak request dan dapat menyebabkan blokir IP sementara/permanen. Gunakan dengan risiko dan tanggung jawab sendiri.

---

## 🤝 Berkontribusi

Fork → branch → pull request. Saat lapor bug sertakan: video ID, log terminal, `python --version`, dan daftar domain preset baru bila ada yang belum tercakup.

---

## 📜 Lisensi & Author

MIT — lihat `LICENSE` (tambahkan jika belum ada).

Dibuat dengan ❤️ oleh **[Nihongo](https://github.com/Ikyletwar)** · `AM Preset Finder v5`
