# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Hargai karya creator dengan tidak mengklaim sebagai milik Anda
# Pelanggaran akan ditandai
# Jangan merubah nama author (Nihongo) pada script ini
# Karya ini dibuat sepenuhnya oleh kami
import requests
import pandas as pd
import time
import os
import json
import jmespath
from datetime import datetime, timezone
from typing import List, Dict, Any, Iterator, Optional
import base64


import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn,
    TaskProgressColumn
)
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule

class TikTokScraper:
    """
    Scraper TikTok modern berbasis Class untuk mengambil detail video,
    semua komentar, dan semua balasan dengan tampilan CLI yang menarik.
    """
    

    API_VIDEO_DETAIL_URL = "https://www.tiktok.com/api/video/detail/"
    API_COMMENT_LIST_URL = "https://www.tiktok.com/api/comment/list/"
    API_REPLY_LIST_URL = "https://www.tiktok.com/api/comment/list/reply/"
    API_AID = "1988"

    def __init__(self):
        """Inisialisasi scraper."""
        self.console = Console()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.tiktok.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
        
        self.video_id: Optional[str] = None
        self.video_url: Optional[str] = None

        self.video: Optional[Dict[str, Any]] = None
        self.comments: List[Dict[str, Any]] = []
        self.replies: List[Dict[str, Any]] = []
        
    def _print_banner(self):
        """Menampilkan banner dan disclaimer dengan desain yang lebih menarik dan warna cerah."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        banner_text = pyfiglet.figlet_format("TikTok Scraper", font="slant")
        self.console.print(Align.center(f"[bold bright_cyan]{banner_text}[/bold bright_cyan]"))
        
        info_panel = Panel(
            "[bold bright_yellow]Created By : Nihongo[/bold bright_yellow]",
            title="[bold bright_magenta]TikTok Comment Scraper v4.1[/bold bright_magenta]",
            subtitle="[dim bright_white]Modern Class-Based Scraper with Enhanced UI[/dim bright_white]",
            border_style="bright_blue",
            width=80
        )
        self.console.print(Align.center(info_panel))

        encoded_message = b'RGlsYXJhbmcga2VyYXMgdW50dWsgbWVyZWNvZGUgYXRhdSBtZW5ndWJhaCBuYW1hIGF1dGhvciAoTmlob25nbykgcGFkYSBzY3JpcHQgaW5pLiBLYXJ5YSBpbmkgZGlidWF0IHNlcGVudWhueWEgb2xlaCBrYW1pLiBNb2hvbiBoYXJnYWkga2FyeWEgY3JlYXRvciBkZW5nYW4gdGlkYWsgbWVuZ2tsYWltIHNlYmFnYWkgbWlsaWsgQW5kYS4gUGVsYW5nZ2FyYW4gYWthbiBkaXRhbmRhaS4='

        decoded_message = base64.b64decode(encoded_message).decode('utf-8')

        
        # -------------------
        
        respect_panel = Panel(
            f"[bold bright_white]{decoded_message}[/bold bright_white]",
            title="[bold bright_yellow]⚠ HARGAI KARYA CREATOR ⚠[/bold bright_yellow]", 
            border_style="bright_yellow", 
            width=80
        )
        self.console.print(Align.center(respect_panel))

        warning_panel = Panel(
            "[bold bright_red]⚠ PERINGATAN:[/] [bright_yellow]Scraping melanggar ToS TikTok. "
            "Skrip ini membuat BANYAK permintaan API dan bisa menyebabkan blokir IP. "
            "Gunakan dengan risiko Anda sendiri.[/bright_yellow]",
            title="[bold bright_red]Disclaimer[/bold bright_red]",
            border_style="bright_red",
            width=80
        )
        self.console.print(Align.center(warning_panel))
        self.console.print(f"[dim]DEBUG: {decoded_message}[/dim]")

        self.console.print(Rule(style="bright_cyan"))

    def _get_video_id(self, url: str) -> Optional[str]:
        """Mengambil Video ID dari berbagai format URL TikTok."""
        self.console.print(f"[bright_cyan]🔍 Memproses URL:[/] [bold bright_white]{url}[/bold bright_white]")
        
        with Progress(
            SpinnerColumn(style="bright_magenta"),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Mengekstrak Video ID...", total=None)
            
            try:
                if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
                    progress.update(task, description="Mengarahkan URL...")
                    response = self.session.head(url, stream=True, allow_redirects=True, timeout=5)
                    url = response.url
                
                progress.update(task, description="Mengekstrak ID Video...")
                video_id = url.split("/video/")[1].split("?", 1)[0] if "/video/" in url else url.split("/")[5].split("?", 1)[0]
                
                if not video_id.isdigit():
                    self.console.print(f"[bold bright_red]❌ Error:[/] Tidak dapat menemukan Video ID yang valid dari URL.[/bold bright_red]")
                    return None
                
                progress.update(task, description="[bright_green]✅ Video ID berhasil diekstrak![/bright_green]")
                time.sleep(0.5)
                return video_id
            except Exception as e:
                self.console.print(f"[bold bright_red]❌ Error:[/] Gagal memproses URL: {e}")
                return None

    def _format_timestamp(self, ts: int) -> str:
        """Mengonversi UNIX timestamp ke format yang mudah dibaca."""
        try:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except Exception:
            return "N/A"

    def _format_number(self, num: int) -> str:
        """Format angka dengan pemisah ribuan."""
        return f"{num:,}"
# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Hargai karya creator dengan tidak mengklaim sebagai milik Anda
# Pelanggaran akan ditandai
# Jangan merubah nama author (Nihongo) pada script ini
# Karya ini dibuat sepenuhnya oleh kami
    def _get_video_details(self) -> Dict[str, Any]:
        """Mengambil detail video (caption, author, view count) dari API dengan perbaikan."""
        self.console.print("[bright_cyan]📥 Mengambil detail video...[/bright_cyan]")
        
        with Progress(
            SpinnerColumn(style="bright_magenta"),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Menghubungi API TikTok...", total=None)
            
            params = {'aid': self.API_AID, 'aweme_id': self.video_id}
            try:
                progress.update(task, description="Mengambil data video...")
                response = self.session.get(self.API_VIDEO_DETAIL_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get("status_code") != 0:
                    error_msg = data.get("status_msg", "Alasan tidak diketahui.")
                    self.console.print(f"[bold bright_red]❌ Error dari API:[/] {error_msg}")
                    return self._get_default_video_details()

                details = jmespath.search(
                    """
                    {
                        caption: itemInfo.itemStruct.desc,
                        author: itemInfo.itemStruct.author.uniqueId,
                        view_count: itemInfo.itemStruct.stats.playCount,
                        like_count: itemInfo.itemStruct.stats.diggCount,
                        comment_count: itemInfo.itemStruct.stats.commentCount,
                        share_count: itemInfo.itemStruct.stats.shareCount,
                        create_time: itemInfo.itemStruct.createTime
                    }
                    """,
                    data
                )
                
                if not details or not details.get('author'):
                    self.console.print("[bold bright_yellow]⚠ Peringatan:[/] Struktur JSON detail video tidak ditemukan. Mungkin video privat atau dihapus.")
                    return self._get_default_video_details()

                progress.update(task, description="[bright_green]✅ Detail video berhasil diambil![/bright_green]")
                time.sleep(0.5)
                
                self._display_video_details(details)
                return details
                
            except requests.exceptions.HTTPError as http_err:
                self.console.print(f"[bold bright_red]❌ Error HTTP:[/] {http_err} - Video mungkin privat atau dihapus.")
                return self._get_default_video_details()
            except Exception as e:
                self.console.print(f"[bold bright_red]❌ Error Tak Terduga:[/] {e}")
                return self._get_default_video_details()

    def _get_default_video_details(self) -> Dict[str, Any]:
        """Mengembalikan detail video default jika pengambilan gagal."""
        return {
            "caption": "Gagal mengambil caption", 
            "author": "N/A",
            "view_count": 100000000,
            "like_count": 1000000,
            "comment_count": 0,
            "share_count": 0,
            "create_time": 0
        }

    def _display_video_details(self, details: Dict[str, Any]):
        """Menampilkan detail video dengan format yang menarik dan warna cerah."""
        details_text = (
            f"[bold bright_cyan]Pembuat:[/] [bright_yellow]@{details['author']}[/bright_yellow]\n"
            f"[bold bright_cyan]Caption:[/] [bright_white]{details['caption'][:80]}{'...' if len(details['caption']) > 80 else ''}[/bright_white]\n"
            f"[bold bright_cyan]Dibuat:[/] [bright_green]{self._format_timestamp(details.get('create_time', 0))}[/bright_green]"
        )
        
        details_panel = Panel(
            details_text,
            title="[bold bright_blue]Detail Video[/bold bright_blue]",
            border_style="bright_blue",
            width=80
        )
        self.console.print(Align.center(details_panel))
        
        stats_table = Table(title="[bold bright_magenta]Statistik Video[/bold bright_magenta]", show_header=True, header_style="bold bright_white", border_style="bright_cyan")
        stats_table.add_column("Metrik", style="bright_cyan", width=15)
        stats_table.add_column("Jumlah", style="bright_yellow", justify="right")
        
        stats_table.add_row("👁️ Views", f"[bold bright_green]{self._format_number(details.get('view_count', 0))}[/bold bright_green]")
        stats_table.add_row("❤️ Likes", f"[bold bright_red]{self._format_number(details.get('like_count', 0))}[/bold bright_red]")
        stats_table.add_row("💬 Komentar", f"[bold bright_blue]{self._format_number(details.get('comment_count', 0))}[/bold bright_blue]")
        stats_table.add_row("📤 Shares", f"[bold bright_magenta]{self._format_number(details.get('share_count', 0))}[/bold bright_magenta]")
        
        self.console.print(Align.center(stats_table))
        self.console.print(Rule(style="bright_cyan"))


# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Hargai karya creator dengan tidak mengklaim sebagai milik Anda
# Pelanggaran akan ditandai
# Jangan merubah nama author (Nihongo) pada script ini
# Karya ini dibuat sepenuhnya oleh kami

    def _parse_comment(self, comment_json: Dict[str, Any]) -> Dict[str, Any]:
        """Mem-parsing satu objek JSON komentar."""
        parsed_data = jmespath.search(
            """
            {
                cid: cid,
                username: user.unique_id,
                nickname: user.nickname,
                comment: text,
                create_time: create_time,
                avatar: user.avatar_thumb.url_list[0],
                digg_count: digg_count,
                total_reply: reply_comment_total
            }
            """,
            comment_json
        )
        
        parsed_data['create_time'] = self._format_timestamp(parsed_data.get('create_time', 0))
        parsed_data['username'] = parsed_data.get('username', 'N/A')
        parsed_data['avatar'] = parsed_data.get('avatar', None)
        parsed_data['digg_count'] = parsed_data.get('digg_count', 0)
        parsed_data['total_reply'] = parsed_data.get('total_reply', 0)
        parsed_data['replies'] = []
        
        return parsed_data

    def _get_replies(self, comment_id: str, total_replies: int, progress: Progress, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mengambil balasan untuk satu komentar. Jika keyword diisi, hanya balasan mengandung keyword yang disimpan (filter saat streaming)."""
        replies_list = []
        cursor = 0
        kw = (keyword or "").lower() if keyword else ""
        task_replies = progress.add_task(f"[dim] -> Mengambil {total_replies} balasan...", total=total_replies, visible=True)

        while True:
            params = {
                'aid': self.API_AID, 'aweme_id': self.video_id, 'comment_id': comment_id,
                'count': 50, 'cursor': cursor
            }
            try:
                response = self.session.get(self.API_REPLY_LIST_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                replies = data.get("comments", [])
                if not replies: break

                for reply in replies:
                    parsed = self._parse_comment(reply)
                    if kw and kw not in (parsed.get('comment') or "").lower():
                        progress.update(task_replies, advance=1)
                        continue
                    replies_list.append(parsed)
                    progress.update(task_replies, advance=1)
                
                if not data.get("has_more", False): break
                cursor = data.get("cursor")
                time.sleep(0.5)
            except Exception as e:
                self.console.print(f"[bright_red]Error saat ambil balasan: {e}[/bright_red]")
                break
        
        progress.update(task_replies, visible=False)
        progress.remove_task(task_replies)
        return replies_list

# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Hargai karya creator dengan tidak mengklaim sebagai milik Anda
# Pelanggaran akan ditandai
# Jangan merubah nama author (Nihongo) pada script ini
# Karya ini dibuat sepenuhnya oleh kami

    def _get_all_comments_and_replies(self, keyword: Optional[str] = None, skip_replies_if_parent_miss: bool = False) -> List[Dict[str, Any]]:
        """Mengambil komentar utama dan balasannya. Jika keyword diisi, filter langsung saat streaming (tidak tampung semua dulu)."""
        all_comments = []
        cursor = 0
        kw = (keyword or "").lower() if keyword else ""
        total_scanned = 0
        total_replies_scanned = 0
        total_matched_replies = 0
        
        with Progress(
            SpinnerColumn(style="bright_magenta"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style="bright_cyan", complete_style="bright_green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TextColumn("[bold bright_white]Total:[/bold bright_white] {task.completed}"),
            console=self.console
        ) as progress:
            task_comments = progress.add_task("[bold bright_cyan]📥 Mengambil Komentar Utama...[/bold bright_cyan]", total=None)

            while True:
                params = {'aid': self.API_AID, 'aweme_id': self.video_id, 'count': 50, 'cursor': cursor}
                try:
                    response = self.session.get(self.API_COMMENT_LIST_URL, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    comments = data.get("comments", [])
                    if not comments:
                        progress.update(task_comments, description="[bold bright_green]✅ Selesai Komentar Utama[/bold bright_green]", total=len(all_comments))
                        break

                    for comment_json in comments:
                        comment_data = self._parse_comment(comment_json)
                        total_scanned += 1
                        parent_match = (not kw) or (kw in (comment_data.get('comment') or "").lower())

                        if kw and not parent_match and skip_replies_if_parent_miss:
                            # Mode hemat: induk tidak match -> buang, jangan fetch balasan sama sekali.
                            progress.update(task_comments, advance=1, description=f"[bright_cyan]📥 Scan:[/] [bright_white]{total_scanned}[/] [bright_cyan]🔗 Match:[/] [bright_white]{len(all_comments)}[/] [bright_cyan]💬 Balasan match:[/] [bright_white]{total_matched_replies}[/]")
                            continue

                        if comment_data["total_reply"] > 0:
                            replies = self._get_replies(comment_data['cid'], comment_data['total_reply'], progress, keyword=keyword if kw else None)
                            total_replies_scanned += comment_data["total_reply"]
                            total_matched_replies += len(replies)
                            comment_data["replies"] = replies
                        # Filter streaming: hanya simpan thread yang induk match atau ada balasan match
                        if kw and not parent_match and not comment_data.get("replies"):
                            progress.update(task_comments, advance=1, description=f"[bright_cyan]📥 Scan:[/] [bright_white]{total_scanned}[/] [bright_cyan]🔗 Match:[/] [bright_white]{len(all_comments)}[/] [bright_cyan]💬 Balasan match:[/] [bright_white]{total_matched_replies}[/]")
                            continue
                        if kw and parent_match and not comment_data.get("replies"):
                            comment_data["replies"] = []
                        all_comments.append(comment_data)
                        progress.update(task_comments, advance=1, description=f"[bright_cyan]📥 Scan:[/] [bright_white]{total_scanned}[/] [bright_cyan]🔗 Match:[/] [bright_white]{len(all_comments)}[/] [bright_cyan]💬 Balasan match:[/] [bright_white]{total_matched_replies}[/]" if kw else f"[bright_cyan]📥 Komentar:[/] [bright_white]{len(all_comments)}[/] [bright_cyan]💬 Balasan:[/] [bright_white]{total_matched_replies if kw else total_replies_scanned}[/]")
                    
                    if not data.get("has_more", False):
                        progress.update(task_comments, description="[bold bright_green]✅ Selesai Komentar Utama[/bold bright_green]", total=len(all_comments))
                        break
                    cursor = data.get("cursor")
                    time.sleep(1)
                except requests.exceptions.HTTPError as http_err:
                    self.console.print(f"[bold bright_red]❌ Error HTTP:[/] {http_err}")
                    break
                except Exception as e:
                    self.console.print(f"[bold bright_red]❌ Error:[/] {e}")
                    break

        if kw:
            self.console.print(f"\n[bold bright_green]✅ Scan {total_scanned} komentar, dapat {len(all_comments)} thread + {total_matched_replies} balasan mengandung '{keyword}'.[/bold bright_green]")
        else:
            self.console.print(f"\n[bold bright_green]✅ Total {len(all_comments)} komentar utama dan {total_replies_scanned} balasan berhasil diambil.[/bold bright_green]")
        return all_comments

    def _filter_by_keyword(self, comments_list: List[Dict[str, Any]], keyword: str = "https") -> List[Dict[str, Any]]:
        """Filter komentar dan balasan yang teksnya mengandung keyword (case-insensitive)."""
        kw = (keyword or "").lower()
        if not kw:
            return comments_list
        filtered = []
        for c in comments_list:
            parent_text = (c.get('comment') or "").lower()
            parent_match = kw in parent_text
            matching_replies = [r for r in c.get('replies', []) if kw in (r.get('comment') or "").lower()]
            if parent_match or matching_replies:
                new_c = dict(c)
                # Jika induk match, pertahankan semua balasan yang match;
                # jika induk tidak match tapi balasan match, pertahankan induk sebagai konteks.
                if parent_match and not matching_replies:
                    # induk match, tidak ada balasan match -> balasan dikosongkan agar output bersih
                    new_c['replies'] = []
                else:
                    new_c['replies'] = matching_replies
                filtered.append(new_c)
        return filtered

    def _save_to_json(self, data: dict):
        """Menyimpan data akhir ke file JSON."""
        filename = f"tiktok_comments_{self.video_id}.json"
        self.console.print(f"\n[cyan]💾 Menyimpan data JSON ke [bold bright_yellow]{filename}[/bold bright_yellow]...[/cyan]")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self.console.print(f"[bold bright_green]✅ Berhasil![/] Data JSON tersimpan.")
        except Exception as e:
            self.console.print(f"[bold bright_red]❌ Error:[/] Gagal menyimpan file JSON: {e}")
# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Hargai karya creator dengan tidak mengklaim sebagai milik Anda
# Pelanggaran akan ditandai
# Jangan merubah nama author (Nihongo) pada script ini
# Karya ini dibuat sepenuhnya oleh kami
    def _save_to_excel(self, comments_list: List[Dict[str, Any]]):
        """Menyimpan data ke file Excel."""
        filename = f"tiktok_comments_{self.video_id}.xlsx"
        self.console.print(f"[cyan]💾 Menyimpan data Excel ke [bold bright_yellow]{filename}[/bold bright_yellow]...[/cyan]")
        
        flat_list = []
        for comment in comments_list:
            flat_list.append({"Tipe": "Komentar Utama", "ID_Komentar_Induk": "", "ID_Komentar": comment.get('cid'), "Username": comment.get('username'), "Nickname": comment.get('nickname'), "Komentar": comment.get('comment'), "Waktu": comment.get('create_time'), "Jumlah_Like": comment.get('digg_count'), "Total_Balasan": comment.get('total_reply')})
            for reply in comment.get('replies', []):
                flat_list.append({"Tipe": "Balasan", "ID_Komentar_Induk": comment.get('cid'), "ID_Komentar": reply.get('cid'), "Username": reply.get('username'), "Nickname": reply.get('nickname'), "Komentar": reply.get('comment'), "Waktu": reply.get('create_time'), "Jumlah_Like": reply.get('digg_count'), "Total_Balasan": 0})
                    
        if not flat_list:
            self.console.print("[bright_yellow]⚠ Tidak ada data untuk disimpan ke Excel.[/bright_yellow]")
            return
        try:
            df = pd.DataFrame(flat_list)
            df.to_excel(filename, index=False, engine='openpyxl')
            self.console.print(f"[bold bright_green]✅ Berhasil![/] Data Excel tersimpan.")
        except Exception as e:
            self.console.print(f"[bold bright_red]❌ Error:[/] Gagal menyimpan file Excel: {e}")

    def _display_summary_table(self, comments_list: List[Dict[str, Any]], video_details: Dict[str, Any]):
        """Menampilkan tabel ringkasan di konsol."""
        video_info = (
            f"[bold bright_cyan]Video:[/] [bright_yellow]@{video_details['author']}[/bright_yellow]\n"
            f"[bold bright_cyan]Views:[/] [bright_green]{self._format_number(video_details.get('view_count', 0))}[/bright_green] | "
            f"[bold bright_cyan]Likes:[/] [bright_red]{self._format_number(video_details.get('like_count', 0))}[/bright_red]"
        )
        
        video_panel = Panel(video_info, title="[bold bright_blue]Informasi Video[/bold bright_blue]", border_style="bright_blue", width=80)
        self.console.print(Align.center(video_panel))
        
        self.console.print(f"\n[bold bright_white]Tinjauan {min(20, len(comments_list))} Komentar Utama Teratas:[/bold bright_white]")
        
        table = Table(title="Tinjauan Komentar", show_header=True, header_style="bold bright_blue", border_style="bright_cyan")
        table.add_column("Username", style="bright_white", width=15)
        table.add_column("Nickname", style="bright_cyan", width=20)
        table.add_column("Komentar", style="bright_white", min_width=30, max_width=50)
        table.add_column("Likes", style="bright_yellow", justify="right")
        table.add_column("Balasan", style="bright_blue", justify="right")

        for c in comments_list[:20]:
            table.add_row(c['username'], c['nickname'], c['comment'].replace('\n', ' ') if c['comment'] else "", str(c['digg_count']), str(c['total_reply']))
        
        self.console.print(table)

# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Hargai karya creator dengan tidak mengklaim sebagai milik Anda
# Pelanggaran akan ditandai
# Jangan merubah nama author (Nihongo) pada script ini
# Karya ini dibuat sepenuhnya oleh kami

    def _display_completion_screen(self, comments_count: int, replies_count: int):
        """Menampilkan layar penyelesaian."""
        complete_text = pyfiglet.figlet_format("COMPLETE!", font="standard")
        self.console.print(Align.center(f"[bold bright_green]{complete_text}[/bold bright_green]"))
        
        confirmation_panel = Panel(
            f"[bold bright_green]✅ PROSES SELESAI![/bold bright_green]\n\n"
            f"Data lengkap ([bright_yellow]{comments_count}[/bright_yellow] komentar utama dan [bright_yellow]{replies_count}[/bright_yellow] balasan) telah disimpan.\n"
            f"1. [bold bright_cyan]tiktok_comments_{self.video_id}.json[/bold bright_cyan]\n"
            f"2. [bold bright_cyan]tiktok_comments_{self.video_id}.xlsx[/bold bright_cyan]\n\n"
            f"[bright_yellow]Buka file untuk melihat seluruh data.[/bright_yellow]",
            title="[bold bright_green]Konfirmasi Ekspor[/bold bright_green]",
            border_style="bright_green",
            width=80
        )
        self.console.print(Align.center(confirmation_panel))
        
        footer_text = pyfiglet.figlet_format("Thank You!", font="small")
        self.console.print(Align.center(f"[bold bright_magenta]{footer_text}[/bold bright_magenta]"))
        self.console.print(Rule(style="bright_cyan"))
# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Hargai karya creator dengan tidak mengklaim sebagai milik Anda
# Pelanggaran akan ditandai
# Jangan merubah nama author (Nihongo) pada script ini
# Karya ini dibuat sepenuhnya oleh kami
    def run(self):
        """Metode utama untuk menjalankan seluruh proses scraper."""
        try:
            self._print_banner()
            url = Prompt.ask("[bold bright_magenta]» Masukkan Link Video TikTok[/bold bright_magenta]")
            
            self.video_id = self._get_video_id(url)
            if not self.video_id: return
            self.video_url = url

            details = self._get_video_details()
            only_link = Prompt.ask("[bold bright_magenta]» Hanya ambil komentar berisi link (https)? Filter langsung saat fetch[/bold bright_magenta]", choices=["y", "n"], default="y")
            keyword = "https" if only_link.lower() == "y" else None
            skip_mode = False
            if keyword:
                skip_mode = Prompt.ask("[bold bright_magenta]» Mode hemat (skip fetch balasan jika induk tidak match)? y=cepat tapi balasan-link bisa hilang, n=lengkap[/bold bright_magenta]", choices=["y", "n"], default="n") == "y"
            all_comments = self._get_all_comments_and_replies(keyword=keyword, skip_replies_if_parent_miss=skip_mode)

            if not all_comments:
                msg = "[bright_yellow]⚠ Tidak ada komentar yang mengandung 'https'.[/bright_yellow]" if keyword else "[bright_yellow]⚠ Tidak ada komentar yang ditemukan untuk video ini.[/bright_yellow]"
                self.console.print(msg)
                return

            comments_out = all_comments

            final_output = {
                "caption": f"@{details['author']}: {details['caption']}",
                "date_now": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
                "video_url": self.video_url,
                "video_stats": {
                    "view_count": details.get('view_count', 0), "like_count": details.get('like_count', 0),
                    "comment_count": details.get('comment_count', 0), "share_count": details.get('share_count', 0)
                },
                "comments": comments_out
            }
            
            self._save_to_json(final_output)
            self._save_to_excel(comments_out)
            self._display_summary_table(comments_out, details)
            self._display_completion_screen(len(comments_out), sum(len(c.get('replies', [])) for c in comments_out))

        except KeyboardInterrupt:
            self.console.print("\n[bold bright_yellow]⚠ Proses dihentikan oleh pengguna.[/bold bright_yellow]")
        except Exception as e:
            self.console.print(f"\n[bold bright_red]❌ Terjadi error tak terduga:[/] {e}")
# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Hargai karya creator dengan tidak mengklaim sebagai milik Anda
# Pelanggaran akan ditandai
# Jangan merubah nama author (Nihongo) pada script ini
# Karya ini dibuat sepenuhnya oleh kami
# --- Titik Masuk Eksekusi Wak---
if __name__ == "__main__":
    scraper = TikTokScraper()
    scraper.run()