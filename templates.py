# templates.py

# 1-GURUH: Ism va Kompaniya nomi BOR bo'lganda yuboriladigan xatlar
TEMPLATE_WITH_NAME = [
    # 1-Xat
    {
        "subject": "Quick build for {company}",
        "body": """Hi {name},

Love what you’re building at {company}.

Quick pitch: We build clean, high-converting websites and landing pages setup for $500–$600. Fast turnaround, no AI-slop, and we strictly take Crypto.

Interested in upgrading {company}’s site this week?

Best,
Diyor - http://diyor.site"""
    },
    # 2-Xat
    {
        "subject": "I don't waste your time!",
        "body": """{name}, we're not reaching out to promote some "average" stuff!

I built an entire website for {company}. Modern looking, zero distraction and minimalistic style. Helps to dominate your competitors in your niche.

No upfront payments!

Would you like to work with us?

Best, Diyor
http://diyor.site"""
    }
]

# 2-GURUH: Ism va/yoki Kompaniya nomi BO'LMAGANDA yuboriladigan xatlar
TEMPLATES_WITHOUT_NAME = [
    # 1-Xat (Faqat Kompaniya nomi bor bo'lganda)
    {
        "subject": "Quick build for {company}",
        "body": """Hi,

Love what you’re building at {company}.

Quick pitch: We build clean, high-converting websites and landing pages setup for $500–$600. Fast turnaround, no AI-slop, and we strictly take Crypto.

Interested in upgrading {company}’s site this week?

Best,
Diyor - http://diyor.site"""
    },
    # 2-Xat (Faqat Kompaniya nomi bor bo'lganda)
    {
        "subject": "Quick question about {company}",
        "body": """I know you're busy so I need 20 seconds only.

We build modern, minimalistic and high-converting websites for heroes like you!

Actually, I've already built one for you, would you like to take a look?

Best, Diyor DEV
http://diyor.site"""
    },
    # 3-Xat (Faqat Kompaniya nomi bor bo'lganda)
    {
        "subject": "I don't waste your time!",
        "body": """We're not reaching out to promote some "average" stuff!

I built an entire website for {company}. Modern looking, zero distraction and minimalistic style. Helps to dominate your competitors in your niche.

No upfront payments!

Would you like to work with us?

Best, Diyor
http://diyor.site"""
    },
    # 4-Xat (Umuman ISMI ham, KOMPANIYA NOMI ham bo'lmaganda)
    {
        "subject": "I don't waste your time!",
        "body": """I know you're busy, so this will only take 20 seconds!

I really admire the work you're doing — it’s clear you guys are experts in your field.

The only thing missing is a digital home; without it, you're losing leads to competitors who are just easier to find online.

So I built an entire website for you, want to see?
No upfront payments required!

Best, Diyor
Portfolio: http://diyor.site"""
    },
    # 5-Xat (Umuman ISMI ham, KOMPANIYA NOMI ham bo'lmaganda)
    {
        "subject": "I built this for you!",
        "body": """Hi,

I'm a professional web developer and a big fan of the work you're doing!

I built a complete website specifically for your business to help you capture more leads from your current traffic. Do you have a moment to take a look if I send it over?

100% Guarantee and quality work.

Best, Diyor
Portfolio: http://diyor.site"""
    }
]

# FOLLOW-UP SHABLONLARI (1, 2 VA 3-BOSQICH)
FOLLOWUP_TEMPLATES = {
    1: {
        "subject": "Re: {original_subject}",
        "body": "I know your inbox is probably flooded, so I wanted to bring this to the top of your inbox."
    },
    2: {
        "subject": "Re: {original_subject}",
        "body": "Reaching out to you is harder than reaching out to the president :)"
    },
    3: {
        "subject": "Re: {original_subject}",
        "body": "Quick thought — we recently helped a client rebuild their web platform, which boosted their client conversions significantly."
    }
}
