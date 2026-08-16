import os
import json

# ==============================================================================
# 1. GITHUB SECRETS / ENVIRONMENT VARIABLES ORQALI O'QISH (PUBLIC REPO UCHUN)
# ==============================================================================
accounts_json_env = os.environ.get("ACCOUNTS_JSON")

if accounts_json_env:
    try:
        data = json.loads(accounts_json_env)
        # Agar JSON strukturangiz bitta umumiy parol va emaillar ro'yxatidan iborat bo'lsa:
        if isinstance(data, dict) and "accounts" in data:
            common_pwd = data.get("common_password", "HAQIQY_PAROLI")
            smtp_p = data.get("smtp_port", 465)
            ACCOUNTS = []
            for acc in data["accounts"]:
                # Domen nomiga qarab mos hosting serverini tanlash
                domain = acc.split("@")[-1]
                if domain in ["diyors.online"]:
                    host = "mail.diyors.online"
                else:
                    host = "premium357.web-hosting.com"

                ACCOUNTS.append({
                    "type": "domain",
                    "email": acc,
                    "password": common_pwd,
                    "smtp_host": host,
                    "smtp_port": smtp_p,
                    "imap_host": host
                })
        else:
            ACCOUNTS = data

        print(f"✅ ACCOUNTS: Environment Variable'dan {len(ACCOUNTS)} ta akkaunt o'qildi.")
    except Exception as e:
        print(f"❌ ACCOUNTS_JSON parsing xatoligi: {e}")
        ACCOUNTS = []
else:
    # Local test yoki zaxira ro'yxat (Aynan 23 ta akkaunt)
    COMMON_PASS = "HAQIQY_PAROLI"
    
    RAW_EMAILS = [
        "alex@diyor.store",
        "ceo@diyor.website",
        "connect@diyor.space",
        "create@diyor.store",
        "dev@diyor.website",
        "diyor@diyor.store",
        "diyor.talks@diyor.space",
        "growth@diyor.website",
        "hello@diyor.store",
        "hi@diyor.store",
        "hq@diyor.space",
        "impact@diyor.space",
        "me@diyors.online",
        "offer@diyors.online",
        "official@diyor.website",
        "outreach@diyor.space",
        "sales@diyor.website",
        "services@diyor.store",
        "sites@diyor.website",
        "team@diyor.website",
        "web@diyor.store",
        "work@diyor.space",
        "xyz@diyors.online"
    ]

    ACCOUNTS = []
    for email in RAW_EMAILS:
        domain = email.split("@")[-1]
        host = "mail.diyors.online" if domain == "diyors.online" else "premium357.web-hosting.com"
        
        ACCOUNTS.append({
            "type": "domain",
            "email": email,
            "password": COMMON_PASS,
            "smtp_host": host,
            "smtp_port": 465,
            "imap_host": host
        })
