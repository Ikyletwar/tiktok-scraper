"""
Script Pengecek dan Penginstal Dependensi
Dibuat untuk Nihongo

Script ini akan memeriksa apakah pustaka Python yang diperlukan 
(requests, pandas, pyfiglet, rich, jmespath) 
telah terinstal. Jika belum, script akan menginstalnya secara otomatis.
"""

# CODE: Nihongo
# Jangan hapus credit ini ya kak :D
# Hargai karya creator dengan tidak mengklaim sebagai milik Anda
# Pelanggaran akan ditandai
# Jangan merubah nama author (Nihongo) pada script ini
# Karya ini dibuat sepenuhnya oleh kami

import subprocess
import sys
import importlib.util
import time
import os


def bootstrap_dependencies():
    """
    Memastikan 'rich' dan 'pyfiglet' terinstal terlebih dahulu 
    menggunakan print() standar, agar bisa dipakai oleh skrip utama.
    """
    required_for_style = {
        "rich": "rich",
        "pyfiglet": "pyfiglet"
    }
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("============================================")
    print("== MEMULAI PENGECEK DEPENDENSI (BOOTSTRAP) ==")
    print("============================================")
    print("Memeriksa pustaka untuk tampilan CLI...")
    print("Created By: Nihongo")
    print("...")
    print("============================================")

    global styling_available
    styling_available = True

    for module_name, package_name in required_for_style.items():
        if importlib.util.find_spec(module_name) is None:
            print(f"-> Pustaka '{package_name}' tidak ditemukan. Menginstal...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"-> Berhasil menginstal '{package_name}'.")
            except subprocess.CalledProcessError:
                print(f"!!! GAGAL menginstal '{package_name}'.")
                print("!!! Skrip akan berjalan tanpa tampilan CLI penuh.")
                styling_available = False

    print("\n--- Bootstrap selesai. Menjalankan pengecekan utama... ---")
    time.sleep(2) 



def run_main_checker():
    """
    Fungsi utama yang berjalan SETELAH bootstrap.
    Fungsi ini akan mengimpor dan menggunakan rich & pyfiglet untuk CLI.
    """
    
    global styling_available

    if styling_available:
        try:
            from rich.console import Console
            from rich.panel import Panel
            from pyfiglet import Figlet
            console = Console()
        except ImportError:
            styling_available = False
            run_main_checker() 
            return
    else:
    
        print("Mode tampilan dasar aktif.")
    
        class MockConsole:
            def print(self, text, *args, **kwargs):
                import re
            
                clean_text = re.sub(r"\[/?.*?\]", "", str(text))
                print(clean_text)
        
        class MockFiglet:
            def __init__(self, *args, **kwargs): pass
            def renderText(self, text): return f"*** {text} ***"
        
        class MockPanel:
            def __init__(self, text, *args, **kwargs): self.text = text
            def __str__(self): return f"\n--- {self.text} ---\n"

        console = MockConsole()
        Figlet = MockFiglet
        
        Panel = lambda text, **kwargs: str(MockPanel(text, **kwargs))

    os.system('cls' if os.name == 'nt' else 'clear')
    f = Figlet(font='standard') 
    ascii_art = f.renderText('Dependency')
    console.print(f"[bold cyan]{ascii_art}[/bold cyan]")
    ascii_art = f.renderText('Checker')
    console.print(f"[bold cyan]{ascii_art}[/bold cyan]")

    console.print(Panel.fit(
        "Memeriksa & Menginstal Pustaka Python yang Dibutuhkan",
        style="bold blue",
        border_style="blue"
    ))
    console.print("\n") 

    packages_to_check = {
        "requests": "requests",
        "pandas": "pandas",
        "pyfiglet": "pyfiglet",
        "rich": "rich",
        "jmespath": "jmespath"
    }
    
    all_success = True

    for module_name, package_name in packages_to_check.items():
        
        check_message = f"Mengecek [bold magenta]{package_name}[/bold magenta]..."
        
        if styling_available:

            with console.status(check_message, spinner="dots12") as status:
                time.sleep(0.7) 

                spec = importlib.util.find_spec(module_name)
                
                if spec is not None:
            
                    status.stop()
                    console.print(f"  ✅ [bold green]{package_name}[/bold green] sudah terinstal.")
                else:
                    status.update(f"[bold yellow]Menginstal {package_name}...", spinner="monkey")
                    
                    try:
                        
                        subprocess.run(
                            [sys.executable, "-m", "pip", "install", package_name],
                            capture_output=True, 
                            text=True,
                            check=True 
                        )
                        status.stop()
                        console.print(f"  📦 [bold blue]Berhasil menginstal {package_name}.[/bold blue]")
                    except subprocess.CalledProcessError as e:
                        
                        status.stop()
                        console.print(f"  ❌ [bold red]Gagal menginstal {package_name}.[/bold red]")
                        console.print(f"[red]{e.stderr}[/red]")
                        all_success = False
        else:
    
            console.print(check_message)
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                console.print(f"  [OK] {package_name} sudah terinstal.")
            else:
                console.print(f"  [+] Menginstal {package_name}...")
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package_name],
                        capture_output=True, text=True, check=True
                    )
                    console.print(f"  [+] Berhasil menginstal {package_name}.")
                except subprocess.CalledProcessError:
                    console.print(f"  [!] Gagal menginstal {package_name}.")
                    all_success = False

    console.print("\n" + "="*40 + "\n")
    if all_success:
        console.print("[bold green]✨ Semua dependensi telah terpenuhi. Sistem siap![/bold green]")
    else:
        console.print("[bold red]Beberapa dependensi gagal diinstal. Silakan periksa error di atas.[/bold red]")

    console.print("\n\n")
    credit_text = "Created ... by: Nihongo \nSilahkan lanjut index.py untuk memulai..."
    console.print(Panel(
        credit_text, 
        style="dim white", 
        border_style="dim"
    ))


if __name__ == "__main__":
    
    bootstrap_dependencies()
    run_main_checker()