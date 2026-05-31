import os
import requests
import time
import random

# Terminal Renklendirmeleri
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

TOKEN_FILE = "token.txt"
headers = {}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """By Neptun Pasha Giriş Logosu"""
    clear_screen()
    banner = f"""{CYAN}
============================================================
 ███▄    █ ▓█████  ██▓███  ▄▄▄█████▓ █  █  ██▄   █ █ 
 ██ ▀█   █ ▓█   ▀ ▓██░  ██▒▓  ██▒ ▓▒ █  █  █  █  █ █ 
▓██  ▀█ ██▒▒███   ▓██░ ██▓▒▒ ▓██░ ▒░ █▄▄█  █▄▄█  █▄▄█
▓██▒  ▐▌██▒▒▓█  ▄ ▒██▄█▓▒ ▒░ ▓██░ ░  █  █  █  █  █ █ 
▒██░   ▓██░░▒████▒▒██▒ ░  ░  ▒██░ ░  █  █  █  █  █ █ 
                                                     
         D I S C O R D   T E M I Z L I K   A R A C I
                      By Neptun Pasha
============================================================{RESET}"""
    print(banner)

def get_token():
    """Kayıtlı tokeni yükler veya yeni token alıp isteğe göre kaydeder."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                saved_token = f.read().strip()
            if saved_token:
                masked = saved_token[:6] + "..." + saved_token[-6:] if len(saved_token) > 12 else saved_token
                secim = input(f"{YELLOW}Kayıtlı token bulundu ({masked}). Kullanılsın mı? (E/H, Varsayılan: E): {RESET}").strip().lower()
                if secim == '' or secim == 'e':
                    return saved_token
        except Exception as e:
            print(f"{RED}Token dosyası okunurken hata oluştu: {e}{RESET}")
    
    new_token = input(f"{YELLOW}Lütfen Kullanıcı Tokeninizi Girin: {RESET}").strip()
    if new_token:
        save_secim = input(f"{YELLOW}Bu tokeni sonraki girişler için kaydedelim mi? (E/H, Varsayılan: E): {RESET}").strip().lower()
        if save_secim == '' or save_secim == 'e':
            try:
                with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                    f.write(new_token)
                print(f"{GREEN}Token başarıyla '{TOKEN_FILE}' dosyasına kaydedildi!{RESET}")
            except Exception as e:
                print(f"{RED}Token kaydedilemedi: {e}{RESET}")
    return new_token

def get_my_id():
    """Kullanıcının kendi ID'sini doğrular."""
    url = "https://discord.com/api/v9/users/@me"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"{GREEN}Giriş Başarılı:{RESET} {BOLD}{data['username']}#{data['discriminator']}{RESET}")
        return data["id"]
    else:
        print(f"{RED}Hata: Token geçersiz veya API hatası (Durum Kodu: {response.status_code}){RESET}")
        return None

def get_dms():
    """Aktif DM kanallarını çeker."""
    url = "https://discord.com/api/v9/users/@me/channels"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def get_friends():
    """Arkadaş listesini çeker."""
    url = "https://discord.com/api/v9/users/@me/relationships"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [r for r in response.json() if r.get("type") == 1]
    return []

def get_or_create_dm(recipient_id):
    """Kullanıcı ile DM kanalı yoksa oluşturur veya var olan kanal ID'sini döner."""
    url = "https://discord.com/api/v9/users/@me/channels"
    payload = {"recipient_id": recipient_id}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get("id")
    return None

def get_guilds():
    """Üye olunan sunucuları çeker."""
    url = "https://discord.com/api/v9/users/@me/guilds"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def get_guild_channels(guild_id):
    """Sunucu içerisindeki yazı ve thread kanallarını çeker."""
    url = f"https://discord.com/api/v9/guilds/{guild_id}/channels"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [c for c in response.json() if c["type"] in [0, 5, 11, 12]]
    return []

def get_messages(channel_id, limit=50, before=None):
    """Kanaldaki son mesajları listeler."""
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}"
    if before:
        url += f"&before={before}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def delete_message(channel_id, message_id):
    """Mesajı siler. Durum kodunu ve varsa bekleme süresini döner."""
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
    response = requests.delete(url, headers=headers)
    
    retry_after = 0.0
    if response.status_code == 429:
        try:
            retry_after = float(response.json().get("retry_after", 5.0))
        except Exception:
            try:
                retry_after = float(response.headers.get("Retry-After", 5.0))
            except Exception:
                retry_after = 5.0
                
    return response.status_code, retry_after

def deletion_wizard(channel_id, my_id, name):
    """Silme ayarlarını yapılandırır."""
    print_banner()
    print(f"{CYAN}{BOLD}=== SİLME AYARLARI: {name} ==={RESET}")
    
    filter_word = input(f"\n{YELLOW}Belirli bir kelimeyi içeren mesajları mı silelim?\n(Hepsini silmek için boş bırakıp Enter'a basın): {RESET}").strip()
    
    print(f"\n{YELLOW}Hız Modunu Seçin:{RESET}")
    print("[1] Güvenli (Yavaş - 2.5 - 4.5 sn arası bekler, ban riskini azaltır)")
    print("[2] Hızlı (Orta Hız - 0.5 - 1.2 sn arası bekler)")
    print(f"[3] {RED}{BOLD}TURBO (Yüksek Sürat - 0.05 - 0.20 sn arası bekler, BAN RİSKİ YÜKSEKTİR){RESET}")
    speed_choice = input(f"{YELLOW}Seçiminiz (1, 2 veya 3): {RESET}").strip()
    
    if speed_choice == '2':
        min_delay, max_delay = (0.5, 1.2)
    elif speed_choice == '3':
        min_delay, max_delay = (0.05, 0.20)
    else:
        min_delay, max_delay = (2.5, 4.5)
    
    print(f"\n{GREEN}Silme işlemi başlıyor... İptal etmek için Ctrl+C tuşlarına basabilirsiniz.{RESET}\n")
    time.sleep(1.5)
    
    execute_deletion(channel_id, my_id, filter_word, min_delay, max_delay)
    input(f"\n{GREEN}Ana menüye dönmek için Enter'a basın...{RESET}")

def execute_deletion(channel_id, my_id, filter_word, min_delay, max_delay):
    """Silme işlemini yürütür."""
    last_message_id = None
    deleted_count = 0
    try:
        while True:
            messages = get_messages(channel_id, limit=100, before=last_message_id)
            if not messages:
                print(f"{YELLOW}Kanal sonuna ulaşıldı veya mesaj bulunamadı.{RESET}")
                break

            for msg in messages:
                last_message_id = msg["id"]
                
                if msg["author"]["id"] == my_id:
                    content = msg.get("content", "")
                    if filter_word and filter_word.lower() not in content.lower():
                        continue
                    
                    status, retry_after = delete_message(channel_id, msg["id"])
                    if status == 204:
                        deleted_count += 1
                        preview = content[:20].replace('\n', ' ')
                        print(f"{GREEN}[SİLİNDİ]{RESET} '{preview}...' (Toplam: {deleted_count})")
                        time.sleep(random.uniform(min_delay, max_delay))
                    elif status == 429:
                        print(f"{RED}[HIZ SINIRI]{RESET} Discord limiti tetiklendi. {retry_after} saniye otomatik bekleniyor...")
                        time.sleep(retry_after)
                    else:
                        print(f"{RED}[HATA]{RESET} Silinemedi (HTTP {status})")
                        time.sleep(1)
            
            if len(messages) < 100:
                break
    except KeyboardInterrupt:
        print(f"\n{YELLOW}İşlem kullanıcı tarafından durduruldu.{RESET}")

def mass_deletion_wizard(channel_ids, my_id, name):
    """Sunucudaki tüm kanallarda silme işlemi yapar."""
    print_banner()
    print(f"{CYAN}{BOLD}=== TOPLU SİLME AYARLARI: {name} ==={RESET}")
    print(f"{YELLOW}Seçilen sunucudaki toplam {len(channel_ids)} yazı kanalında arama yapılacaktır.{RESET}")
    
    filter_word = input(f"\n{YELLOW}Belirli bir kelimeyi içeren mesajları mı silelim?\n(Hepsini silmek için boş bırakıp Enter'a basın): {RESET}").strip()
    
    print(f"\n{YELLOW}Hız Modunu Seçin:{RESET}")
    print("[1] Güvenli (Slow)")
    print("[2] Hızlı (Fast)")
    print(f"[3] {RED}{BOLD}TURBO (Yüksek Sürat - BAN RİSKİ YÜKSEKTİR){RESET}")
    speed_choice = input(f"{YELLOW}Seçiminiz (1, 2 veya 3): {RESET}").strip()
    
    if speed_choice == '2':
        min_delay, max_delay = (0.5, 1.2)
    elif speed_choice == '3':
        min_delay, max_delay = (0.05, 0.2)
    else:
        min_delay, max_delay = (2.5, 4.5)
    
    print(f"\n{GREEN}Toplu işlem başlıyor...{RESET}\n")
    time.sleep(1.5)
    
    total_deleted = 0
    try:
        for idx, channel_id in enumerate(channel_ids):
            print(f"\n{CYAN}[Kanal {idx+1}/{len(channel_ids)}] ID {channel_id} taranıyor...{RESET}")
            last_message_id = None
            
            while True:
                messages = get_messages(channel_id, limit=100, before=last_message_id)
                if not messages:
                    break
                
                for msg in messages:
                    last_message_id = msg["id"]
                    
                    if msg["author"]["id"] == my_id:
                        content = msg.get("content", "")
                        if filter_word and filter_word.lower() not in content.lower():
                            continue
                        
                        status, retry_after = delete_message(channel_id, msg["id"])
                        if status == 204:
                            total_deleted += 1
                            preview = content[:20].replace('\n', ' ')
                            print(f"{GREEN}[SİLİNDİ]{RESET} '{preview}...' (Toplam: {total_deleted})")
                            time.sleep(random.uniform(min_delay, max_delay))
                        elif status == 429:
                            print(f"{RED}[HIZ SINIRI]{RESET} Discord limiti tetiklendi. {retry_after} saniye otomatik bekleniyor...")
                            time.sleep(retry_after)
                        else:
                            time.sleep(1)
                
                if len(messages) < 100:
                    break
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Toplu işlem kullanıcı tarafından durduruldu.{RESET}")
        
    print(f"\n{GREEN}Toplu silme bitti! Toplam silinen mesaj: {total_deleted}{RESET}")
    input(f"\n{GREEN}Ana menüye dönmek için Enter'a basın...{RESET}")

def dm_menu(my_id):
    """DM Menüsü."""
    while True:
        print_banner()
        print(f"{CYAN}{BOLD}--- DM (ÖZEL MESAJ) KANALLARI ---{RESET}")
        dms = get_dms()
        if not dms:
            print(f"{RED}Aktif DM kanalı bulunamadı veya yüklenemedi.{RESET}")
        else:
            for idx, dm in enumerate(dms[:30]):
                recipients = ", ".join([r["username"] for r in dm.get("recipients", [])])
                print(f"[{idx}] {recipients or 'Grup DM'} (Kanal ID: {dm['id']})")
        
        print(f"\n{YELLOW}[b] Geri Dön  |  [r] Listeyi Yenile (Güncelle){RESET}")
        
        secim = input(f"\n{YELLOW}Seçiminiz: {RESET}").strip().lower()
        
        if secim == 'b':
            return
        elif secim == 'r':
            print(f"{GREEN}Liste güncelleniyor...{RESET}")
            time.sleep(1)
            continue
        
        try:
            idx = int(secim)
            if 0 <= idx < len(dms):
                target_channel = dms[idx]
                recipients = ", ".join([r["username"] for r in target_channel.get("recipients", [])])
                deletion_wizard(target_channel["id"], my_id, name=f"DM ({recipients or 'Grup DM'})")
                return
            else:
                print(f"{RED}Geçersiz numara!{RESET}")
                time.sleep(1)
        except ValueError:
            print(f"{RED}Geçersiz girdi!{RESET}")
            time.sleep(1)

def friends_menu(my_id):
    """Arkadaş listesini listeleyen menü."""
    while True:
        print_banner()
        print(f"{CYAN}{BOLD}--- ARKADAŞLARINIZ ---{RESET}")
        friends = get_friends()
        if not friends:
            print(f"{RED}Arkadaş listeniz boş veya yüklenemedi.{RESET}")
        else:
            for idx, relation in enumerate(friends[:50]):
                user = relation.get("user", {})
                username = user.get("username", "Bilinmeyen")
                global_name = user.get("global_name")
                display_name = f"{global_name} (@{username})" if global_name else f"@{username}"
                print(f"[{idx}] {display_name} (ID: {user.get('id')})")
                
        print(f"\n{YELLOW}[b] Geri Dön  |  [r] Listeyi Yenile (Güncelle){RESET}")
        
        secim = input(f"\n{YELLOW}Seçiminiz: {RESET}").strip().lower()
        
        if secim == 'b':
            return
        elif secim == 'r':
            print(f"{GREEN}Arkadaş listesi güncelleniyor...{RESET}")
            time.sleep(1)
            continue
            
        try:
            idx = int(secim)
            if 0 <= idx < len(friends):
                selected_friend = friends[idx]
                friend_user = selected_friend.get("user", {})
                friend_id = friend_user.get("id")
                friend_name = friend_user.get("username")
                
                print(f"\n{CYAN}Bu arkadaşınızla DM kanalı açılıyor/doğrulanıyor...{RESET}")
                channel_id = get_or_create_dm(friend_id)
                
                if channel_id:
                    deletion_wizard(channel_id, my_id, name=f"DM (@{friend_name})")
                    return
                else:
                    print(f"{RED}Hata: DM kanalı oluşturulamadı.{RESET}")
                    time.sleep(2.5)
            else:
                print(f"{RED}Geçersiz numara!{RESET}")
                time.sleep(1)
        except ValueError:
            print(f"{RED}Geçersiz girdi!{RESET}")
            time.sleep(1)

def guild_channels_menu(guild, my_id):
    """Seçilen sunucunun kanallarını yöneten menü."""
    while True:
        print_banner()
        print(f"{CYAN}{BOLD}--- {guild['name'].upper()} KANALLARI ---{RESET}")
        channels = get_guild_channels(guild["id"])
        
        if not channels:
            print(f"{RED}Yazı kanalı bulunamadı veya yetkiniz yok.{RESET}")
        else:
            print(f"{GREEN}[all] TÜM KANALLARDA SİL (Sunucudaki tüm kanallarda mesajlarını arar){RESET}")
            for idx, channel in enumerate(channels):
                print(f"[{idx}] #{channel['name']} (ID: {channel['id']})")
                
        print(f"\n{YELLOW}[b] Geri Dön  |  [r] Yenile{RESET}")
        
        secim = input(f"\n{YELLOW}Seçiminiz: {RESET}").strip().lower()
        
        if secim == 'b':
            return
        elif secim == 'r':
            print(f"{GREEN}Kanallar güncelleniyor...{RESET}")
            time.sleep(1)
            continue
        elif secim == 'all':
            channel_ids = [c["id"] for c in channels]
            mass_deletion_wizard(channel_ids, my_id, name=f"{guild['name']} (Tüm Sunucu)")
            return
            
        try:
            idx = int(secim)
            if 0 <= idx < len(channels):
                target_channel = channels[idx]
                deletion_wizard(target_channel["id"], my_id, name=f"#{target_channel['name']}")
                return
            else:
                print(f"{RED}Geçersiz kanal numarası!{RESET}")
                time.sleep(1)
        except ValueError:
            print(f"{RED}Geçersiz girdi!{RESET}")
            time.sleep(1)

def guild_menu(my_id):
    """Sunucu Menüsü."""
    while True:
        print_banner()
        print(f"{CYAN}{BOLD}--- SUNUCULARINIZ ---{RESET}")
        guilds = get_guilds()
        if not guilds:
            print(f"{RED}Sunucu bulunamadı veya yüklenemedi.{RESET}")
        else:
            for idx, guild in enumerate(guilds[:30]):
                print(f"[{idx}] {guild['name']} (ID: {guild['id']})")
        
        print(f"\n{YELLOW}[b] Geri Dön  |  [r] Listeyi Yenile (Güncelle){RESET}")
        
        secim = input(f"\n{YELLOW}Seçiminiz: {RESET}").strip().lower()
        
        if secim == 'b':
            return
        elif secim == 'r':
            print(f"{GREEN}Liste güncelleniyor...{RESET}")
            time.sleep(1)
            continue
            
        try:
            idx = int(secim)
            if 0 <= idx < len(guilds):
                selected_guild = guilds[idx]
                guild_channels_menu(selected_guild, my_id)
                return
            else:
                print(f"{RED}Geçersiz numara!{RESET}")
                time.sleep(1)
        except ValueError:
            print(f"{RED}Geçersiz girdi!{RESET}")
            time.sleep(1)

def main():
    global headers
    print_banner()
    
    token = get_token()
    if not token:
        print(f"{RED}Token boş bırakılamaz.{RESET}")
        input("\nÇıkmak için Enter'a basın...")
        return
        
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    my_id = get_my_id()
    if not my_id:
        input(f"\n{RED}Devam etmek için Enter'a basın...{RESET}")
        return

    time.sleep(1.2)

    while True:
        print_banner()
        print(f"{CYAN}{BOLD}=== ANA MENÜ ==={RESET}")
        print("[1] Aktif DM (Özel Mesaj) Kanallarını Listele")
        print("[2] Tüm Arkadaşlarımı Listele")
        print("[3] Sunucuları (Guilds) Listele")
        print(f"{YELLOW}[r] Menüyü Yenile{RESET}")
        print("[q] Çıkış")
        
        ana_secim = input(f"\n{YELLOW}Seçiminiz: {RESET}").strip().lower()

        if ana_secim == 'q':
            print(f"{GREEN}Çıkış yapıldı.{RESET}")
            break
        elif ana_secim == '1':
            dm_menu(my_id)
        elif ana_secim == '2':
            friends_menu(my_id)
        elif ana_secim == '3':
            guild_menu(my_id)
        elif ana_secim == 'r':
            print(f"{GREEN}Yenileniyor...{RESET}")
            time.sleep(0.5)
        else:
            print(f"{RED}Geçersiz seçim!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
