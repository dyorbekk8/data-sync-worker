# templates.py

# 1-GURUH: Ism va Kompaniya nomi BOR bo'lganda yuboriladigan xatlar
TEMPLATE_WITH_NAME = [
    # 1-Xat
    {
        "subject": "Quick build for {company}",
        "body": """Hi {name},

Love what you’re building at {company}.

Quick pitch: We build clean, high-converting websites and landing pages. Plus, we provide daily qualified leads to fuel your sales. Fast turnaround, no AI-slop, and we accept Crypto.

Interested in upgrading {company}’s web presence this week?

Best,
Diyor | Web Developer"""
    },
    # 2-Xat
    {
        "subject": "I don't waste your time!",
        "body": """{name}, we're not reaching out to promote some "average" stuff!

We build modern-looking, zero-distraction, minimalistic websites that help you dominate competitors in your niche. Along with the website, we also bring you qualified leads.

No upfront payments!

Would you like to work with us?

Best, Diyor
CEO | Web Developer"""
    }
]

# 2-GURUH: Ism va/yoki Kompaniya nomi BO'LMAGANDA yuboriladigan xatlar
TEMPLATES_WITHOUT_NAME = [
    # 1-Xat (Faqat Kompaniya nomi bor bo'lganda)
    {
        "subject": "Quick build for {company}",
        "body": """Hi,

Love what you’re building at {company}.

Quick pitch: We build clean, high-converting websites and landing pages. Plus, we provide daily qualified leads to fuel your sales. Fast turnaround and we accept Crypto.

Interested in upgrading {company}’s web presence this week?

Best,
Diyor - CEO\DEV"""
    },
    # 2-Xat (Faqat Kompaniya nomi bor bo'lganda)
    {
        "subject": "Quick question about {company}",
        "body": """I know you're busy so I need 20 seconds only.

We build modern, minimalistic, high-converting websites and deliver daily qualified leads for businesses like yours!

Would you be open to a quick web and lead system upgrade for {company}?

Best, Diyor DEV"""
    },
    # 3-Xat (Faqat Kompaniya nomi bor bo'lganda)
    {
        "subject": "I don't waste your time!",
        "body": """We're not reaching out to promote some "average" stuff!

We build modern, zero-distraction websites for brands like {company} and supply them with fresh qualified leads.

No upfront payments!

Would you like to work with us?

Best, Diyor"""
    },
    # 4-Xat (Umuman ISMI ham, KOMPANIYA NOMI ham bo'lmaganda)
    {
        "subject": "I don't waste your time!",
        "body": """I know you're busy, so this will only take 20 seconds!

I really admire the work you're doing — it’s clear you guys are experts in your field.

We build modern websites and provide daily qualified leads to make sure you never run out of clients.

No upfront payments required! Would you be open to chatting?

Best, Diyor"""
    },
    # 5-Xat (Umuman ISMI ham, KOMPANIYA NOMI ham bo'lmaganda)
    {
        "subject": "Quick web development & lead offer",
        "body": """Hi,

I'm a professional web developer and a big fan of the work you're doing!

We specialize in building custom websites and delivering daily qualified leads to help you capture more clients consistently.

100% Guarantee and quality work. Would you be open to getting more clients this week?

Best, Diyor"""
    }
]

# YAGONA FOLLOW-UP SHABLONI
FOLLOWUP_TEMPLATES = {
    1: {
        "subject": "Re: Quick question",
        "body": "Reaching out to you is harder than reaching out to the president :)"
    }
}
