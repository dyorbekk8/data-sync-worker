# sender.py
import os
import json

# ==============================================================================
# 1. GITHUB SECRETS / ENVIRONMENT VARIABLES ORQALI O'QISH (PUBLIC REPO UCHUN)
# ==============================================================================
accounts_json_env = os.environ.get("ACCOUNTS_JSON")

if accounts_json_env:
    try:
        ACCOUNTS = json.loads(accounts_json_env)
        print(f"✅ ACCOUNTS: Environment Variable'dan {len(ACCOUNTS)} ta akkaunt o'qildi.")
    except Exception as e:
        print(f"❌ ACCOUNTS_JSON parsing xatoligi: {e}")
        ACCOUNTS = []
else:
    # Local test yoki standart zaxira ro'yxat
    ACCOUNTS = [
        # ==========================================
        # 1. DOMEN EMAILLAR (19 ta)
        # Server: premium357.web-hosting.com | Port: 465 (SSL)
        # ==========================================
        {
            "type": "domain",
            "email": "web@diyor.store",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "team@diyor.website",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "sites@diyor.website",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "services@diyor.store",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "sales@diyor.website",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "outreach@diyor.space",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "official@diyor.website",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "impact@diyor.space",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "hq@diyor.space",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "hi@diyor.store",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "hello@diyor.store",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "growth@diyor.website",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "diyor.talks@diyor.space",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "diyor@diyor.store",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "create@diyor.store",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "dev@diyor.website",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "connect@diyor.space",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "ceo@diyor.website",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        },
        {
            "type": "domain",
            "email": "alex@diyor.store",
            "password": "HAQIQY_PAROLI",
            "smtp_host": "premium357.web-hosting.com",
            "smtp_port": 465,
            "imap_host": "premium357.web-hosting.com"
        }
    ]
