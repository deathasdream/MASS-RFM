import requests
from concurrent.futures import ThreadPoolExecutor
import os
from colorama import Fore, init
import threading
import traceback  

init(autoreset=True)

header = r"""
    __  ______   __________     ____  ________  ___
   /  |/  /   | / ___/ ___/    / __ \/ ____/  |/  /
  / /|_/ / /| | \__ \\__ \    / /_/ / /_  / /|_/ / 
 / /  / / ___ |___/ /__/ /   / _, _/ __/ / /  / /  
/_/  /_/_/  |_/____/____/   /_/ |_/_/   /_/  /_/   

https://github.com/deathasdream
"""

checked_urls = set()
write_lock = threading.Lock()

def check_rfm(url, paths, result_file):
    global checked_urls
    if not url.startswith("http://") and not url.startswith("https://"):
        url_https = "https://" + url
        url_http = "http://" + url
    else:
        url_https = url
        url_http = url

    for scheme_url in [url_https, url_http]:
        try:
            for path in paths:
                full_url = scheme_url.rstrip("/") + "/" + path.lstrip("/")
                
                if full_url in checked_urls:
                    continue  

                print(Fore.CYAN + f"[CHECK] {full_url}")  
                response = requests.get(full_url, timeout=10, allow_redirects=False)  

                if response.status_code == 200:
                    if "FileManager" in response.text or "Responsive FileManager" in response.text:
                        found_message = f"[FOUND] {scheme_url} -> Path: {path}"
                        print(Fore.GREEN + found_message)
                                               
                        with write_lock:
                            with open(result_file, "a") as f:
                                f.write(found_message + "\n")
                       
                        checked_urls.add(full_url)

                else:
                    print(Fore.RED + f"[ERROR] {full_url} -> HTTP Status: {response.status_code}")

        except requests.RequestException as e:
            print(Fore.RED + f"[ERROR] {scheme_url} -> {e}")

def main():
    print(Fore.MAGENTA + header)  

    websites_file = input(Fore.YELLOW + "MASUKAN LIST TARGET    : ").strip()
    paths_file = input(Fore.YELLOW + "MASUKAN LIST PATH      : ").strip()
    result_file = "results.txt"

    if not os.path.exists(websites_file) or not os.path.exists(paths_file):
        print(Fore.RED + "[ERROR] File input tidak ditemukan.")
        return

    with open(websites_file, "r") as wf:
        websites = [line.strip() for line in wf.readlines() if line.strip()]
    with open(paths_file, "r") as pf:
        paths = [line.strip() for line in pf.readlines() if line.strip()]

    if not websites or not paths:
        print(Fore.RED + "[ERROR] Tidak ada target atau path untuk diperiksa.")
        return

    if os.path.exists(result_file):
        os.remove(result_file)

    try:
        max_threads = int(input(Fore.YELLOW + "THREAD   : "))
        if max_threads < 1:
            raise ValueError
    except ValueError:
        print(Fore.RED + "[ERROR] Jumlah thread harus angka positif.")
        return

    try:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for website in websites:
                executor.submit(check_rfm, website, paths, result_file)

        print(Fore.CYAN + "\n[INFO] Hasil disimpan di 'results.txt'.")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Terjadi kesalahan: {e}")
        traceback.print_exc() 

if __name__ == "__main__":
    main()
