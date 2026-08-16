import os
import json

# ==============================================================================
# 1. GITHUB SECRETS / ENVIRONMENT VARIABLES ORQALI O'QISH
# ==============================================================================
accounts_json_env = os.environ.get("ACCOUNTS_JSON")

HOST = "business99.web-hosting.com"
SMTP_PORT = 465
IMAP_PORT = 993

ACCOUNTS = []

if accounts_json_env:
    try:
        data = json.loads(accounts_json_env)
        
        # Har bir akkauntni individual parol bilan shakllantirish
        if isinstance(data, list):
            for item in data:
                email = item.get("email", "").strip()
                password = item.get("password", "").strip()
                if email and password:
                    ACCOUNTS.append({
                        "type": "domain",
                        "email": email,
                        "password": password,
                        "smtp_host": HOST,
                        "smtp_port": SMTP_PORT,
                        "imap_host": HOST,
                        "imap_port": IMAP_PORT
                    })
        elif isinstance(data, dict) and "accounts" in data:
            common_pwd = data.get("common_password", "").strip()
            for acc in data["accounts"]:
                ACCOUNTS.append({
                    "type": "domain",
                    "email": acc.strip(),
                    "password": common_pwd,
                    "smtp_host": HOST,
                    "smtp_port": SMTP_PORT,
                    "imap_host": HOST,
                    "imap_port": IMAP_PORT
                })

        print(f"✅ ACCOUNTS: Environment Variable'dan {len(ACCOUNTS)} ta akkaunt muvaffaqiyatli o'qildi.")
    except Exception as e:
        print(f"❌ ACCOUNTS_JSON parsing xatoligi: {e}")
        ACCOUNTS = []
else:
    print("⚠️ ACCOUNTS_JSON environment variable topilmadi!")
