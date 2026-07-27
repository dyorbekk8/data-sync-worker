import modal
import time
import random

app = modal.App("cold-email-continuous")

# Kerakli pip kutubxonalari
image = modal.Image.debian_slim().pip_install(
    "gspread", 
    "google-auth", 
    "python-dotenv"
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("email-secrets")],
    timeout=86400  # 24 soatlik to'xtovsiz sikl
)
def run_infinite_loop():
    from main import process_next_lead  # 1 ta leadga xat yuboruvchi funksiya
    
    print("24/7 To'xtovsiz rejim ishga tushdi...")
    
    while True:
        try:
            # Leadga xat yuborish
            has_more_leads = process_next_lead()
            
            if has_more_leads:
                # Faqat xat yuborilgandan keyin 20-30 sek interval
                sleep_time = random.randint(20, 30)
                print(f"Xat yuborildi. Keyingisi uchun {sleep_time}s pauza...")
                time.sleep(sleep_time)
            else:
                # Lead tugasa, UXLAMAYDI! Darhol qayta tekshiradi
                pass
                
        except Exception as e:
            # Xatolik bo'lsa ham UXLAMAYDI, darhol keyingi aylanishga o'tadi
            print(f"Xatolik: {e}. Qayta urunilmoqda...")
            pass

@app.local_entrypoint()
def main():
    run_infinite_loop.remote()
