import modal
import time
import random

app = modal.App("cold-email-continuous")

# requirements.txt dagi barcha kutubxonalarni yuklaymiz
image = modal.Image.debian_slim().pip_install(
    "gspread", 
    "google-auth", 
    "python-dotenv"
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("email-secrets")],
    timeout=86400  # 24 soat to'xtovsiz ishlash
)
def run_infinite_loop():
    print("Modal 24/7 sikl ishga tushdi...")
    
    while True:
        try:
            # run.py faylini to'g'ridan-to me'yorida ishga tushirish
            import run
            if hasattr(run, 'main'):
                run.main()
            elif hasattr(run, 'start'):
                run.start()
            else:
                # Agar run.py ichida funksiya bo'lmasa, faylning o'zini o'qiydi
                exec(open("run.py").read())
                
            # 20-30 sekundlik pauza
            sleep_time = random.randint(20, 30)
            print(f"Bitta sikl tugadi. {sleep_time}s pauza...")
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"Skriptda xatolik: {e}. 10 sekunddan keyin qayta uruniladi...")
            time.sleep(10)

# Deploy bo'lishi bilanoq Modal bulutida siklni yurgizib yuborish
@app.local_entrypoint()
def main():
    run_infinite_loop.remote()
