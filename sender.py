# sender.py

# 25 ta email akkauntlar to'liq bazasi
# Gmaillar uchun 16 xonali App Password, Domen-emaillar uchun akkaunt paroli ishlatiladi.

ACCOUNTS = [
    # ==========================================
    # 1. GMAIL AKKAUNTLAR (6 ta)
    # ==========================================
    {
        "type": "gmail",
        "email": "behruzrozmetov246@gmail.com",
        "password": "sgaiqylkgsqxnvrd",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com"
    },
    {
        "type": "gmail",
        "email": "dildoramatkarimiva@gmail.com",
        "password": "dwzcpblpoipivfbk",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com"
    },
    {
        "type": "gmail",
        "email": "g84687216@gmail.com",
        "password": "xzouchunuqiqjpbo",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com"
    },
    {
        "type": "gmail",
        "email": "userliders0@gmail.com",
        "password": "qfpdwvgahdpazzxp",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com"
    },
    {
        "type": "gmail",
        "email": "xsxsdromer@gmail.com",
        "password": "nhgchivappnmhogy",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com"
    },
    {
        "type": "gmail",
        "email": "pcofficee@gmail.com",
        "password": "xjufgtiulckenzxw",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com"
    },

    # ==========================================
    # 2. DOMEN EMAILLAR (19 ta)
    # Server: premium357.web-hosting.com | Port: 465 (SSL)
    # ==========================================
    {
        "type": "domain",
        "email": "web@diyor.store",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "team@diyor.website",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "sites@diyor.website",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "services@diyor.store",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "sales@diyor.website",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "outreach@diyor.space",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "official@diyor.website",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "impact@diyor.space",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "hq@diyor.space",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "hi@diyor.store",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "hello@diyor.store",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "growth@diyor.website",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "diyor.talks@diyor.space",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "diyor@diyor.store",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "create@diyor.store",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "dev@diyor.website",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "connect@diyor.space",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "ceo@diyor.website",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    },
    {
        "type": "domain",
        "email": "alex@diyor.store",
        "password": "AKKAUNT.SCAM",
        "smtp_host": "premium357.web-hosting.com",
        "smtp_port": 465,
        "imap_host": "premium357.web-hosting.com"
    }
]
