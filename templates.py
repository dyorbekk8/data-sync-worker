# templates.py

# 1-VARIANT: Ism talab qilinadigan xat va subject (B ustunda ism bo'lsa)
# Subject va Body bir-biriga bog'liq bo'lgani uchun juftlik holida saqlanadi
TEMPLATE_WITH_NAME = [
    {
        "subject": "{name}, you need this!",
        "body": """{name}, after that, you can increase your profits at least 2x times!

I appreciate the work you're doing, but you're missing a simple thing.

Normal websites feel outdated and don't make any progress, so I've built a professional, beautiful, and high-converting website for you.

30-day moneyback guarantee!

Want to take a look? Tell me
http://diyor.site - portfolio"""
    }
]

# 2 VA 3-VARIANTLAR: Ism talab qilinmaydigan xatlar va subject'lar (B ustun bo'sh bo'lsa ham yuboriladi)
TEMPLATES_WITHOUT_NAME = [
    # 1-Xat va Subject
    {
        "subject": "I don't waste your time!",
        "body": """I know you're busy, so this will only take 20 seconds!
I really admire the work you're doing — it’s clear you guys are experts in your field.

The only thing missing is a digital home; without it, you're losing leads to competitors who are just easier to find online.

So I built an entire website for you, want to see?
30-day moneyback guarantee!

Best, Diyor
Portfolio: http://diyor.site"""
    },
    
    # 3-Xat va Subject
    {
        "subject": "I know your problem (CLICK)",
        "body": """Hi,

I'm a local web developer and a big fan of the work you're doing!

I built a complete website specifically for your business to help you capture more leads from your current traffic. Do you have a moment to take a look if I send it over?

30-day moneyback guarantee!

Best, Diyor
Portfolio: http://diyor.site"""
    }
]

# FOLLOW-UP SHABLONLARI (1, 2 VA 3-BOSQICH)
FOLLOWUP_TEMPLATES = {
    1: {
        "subject": "Re: {original_subject}",
        "body": """Hi {name},

I know your inbox is probably flooded, so I wanted to bring this to the top of your inbox.

Best,
Diyor"""
    },
    2: {
        "subject": "Re: {original_subject}",
        "body": """Hi {name},

Reaching out to you is harder than reaching out to the president :)

Best,
Diyor"""
    },
    3: {
        "subject": "Re: {original_subject}",
        "body": """Hi {name},

Quick thought — we recently helped a client rebuild their web platform, which boosted their client conversions significantly.

Best,
Diyor"""
    }
}
