import os
import time
import random
import json
import smtplib
import imaplib
import email
import socket
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gspread

# --- RAILWAY / CLOUD SERVERLAR UCHUN IPv4 MAJBURINI SOZLASH ---
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response for response in responses if response[0] == socket.AF_INET]

socket.getaddrinfo = new_getaddrinfo

from sender import ACCOUNTS
from templates import TEMPLATE_WITH_NAME, TEMPLATES_WITHOUT_NAME, FOLLOWUP_TEMPLATES

# --- GOOGLE SHEETS SETUP ---
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# --- CREDENTIALS YUKLASH (RAILWAY VA LOCAL UCHUN OPTIMALLASHTIRILGAN) ---
CREDS_FILE = "creds.json"
creds_dict = None

# 1. Avvalo creds.json faylini tekshiramiz
if os.path.exists(CREDS_FILE):
    try:
        with open(CREDS_FILE, "r") as f:
            creds_dict = json.load(f)
    except Exception as e:
        print(f"⚠️ creds.json faylini o'qishda xatolik: {e}")

# 2. Agar fayl bo'lmasa, Railway / Environment Variables'dan o'qiymiz
if not creds_dict:
    creds_json = os.environ.get("GOOGLE_CREDENTIALS") or os.environ.get("GOOGLE_OAUTH_JSON")
    if creds_json:
        try:
            creds_dict = json.loads(creds_json, strict=False)
        except Exception as e:
            print(f"⚠️ Environment Variable'dan JSON parsing xatoligi: {e}")

if not creds_dict:
    raise ValueError("❌ Na 'creds.json' fayli va na 'GOOGLE_CREDENTIALS' environment variable topildi!")

# OAuth 2.0 va Service Account avtomatik integratsiyasi
if "installed" in creds_dict or "web" in creds_dict:
    from google.oauth2.credentials import Credentials as OAuthCredentials
    info = creds_dict.get("installed") or creds_dict.get("web")
    creds = OAuthCredentials(
        token=info.get("token"),
        refresh_token=info.get("refresh_token"),
        token_uri=info.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=info.get("client_id"),
        client_secret=info.get("client_secret"),
        scopes=SCOPE
    )
elif "refresh_token" in creds_dict and "client_id" in creds_dict:
    from google.oauth2.credentials import Credentials as OAuthCredentials
    creds = OAuthCredentials(
        token=creds_dict.get("token"),
        refresh_token=creds_dict.get("refresh_token"),
        token_uri=creds_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=creds_dict.get("client_id"),
        client_secret=creds_dict.get("client_secret"),
        scopes=SCOPE
    )
else:
    from google.oauth2.service_account import Credentials as SACredentials
    creds = SACredentials.from_service_account_info(creds_dict, scopes=SCOPE)

gc = gspread.authorize(creds)

SHEET_NAME = os.environ.get("SHEET_NAME", "Cold Email Leads")
sheet = gc.open(SHEET_NAME).sheet1

# O'zbekiston vaqti (UTC+5)
UZB_TZ = timezone(timedelta(hours=5))

# GLOBAL XOTIRA
GLOBAL_SENT_CACHE = set()

# O'z pochtalarimiz ro'yxati
MY_SENDER_EMAILS = set(acc['email'].lower() for acc in ACCOUNTS)

def get_uzb_now():
    return datetime.now(UZB_TZ)

def save_to_sent_folder(acc, msg):
    if acc.get('type') == 'gmail':
        return
    try:
        mail = imaplib.IMAP4_SSL(acc['imap_host'], timeout=15)
        mail.login(acc['email'], acc['password'])
        mail.append('Sent', '\\Seen', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        mail.logout()
    except Exception as e:
        print(f"⚠️ Sent papkasiga saqlashda xatolik ({acc['email']}): {e}")

def send_email_real(acc, to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = acc['email']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        smtp_host = acc.get('smtp_host', 'smtp.gmail.com')
        smtp_port = int(acc.get('smtp_port', 465))

        if acc.get('type') == 'gmail' or 'gmail.com' in smtp_host or smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, 465, timeout=20)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
            server.starttls()

        server.login(acc['email'], acc['password'])
        refused = server.send_message(msg)
        server.quit()

        if refused:
            print(f"❌ Xat rad etildi: {refused}")
            return False

        save_to_sent_folder(acc, msg)
        return True

    except Exception as e:
        print(f"❌ SMTP XATOLIK ({acc['email']} -> {to_email}): {e}")
        return False

def update_sent_total_and_replies_summary(all_values):
    try:
        if len(all_values) <= 1:
            return

        rows = all_values[1:]
        sent_yes_count = 0
        my_replied_senders = []

        for row in rows:
            status_val = row[2].strip().upper() if len(row) > 2 else ''
            if status_val == 'YES':
                sent_yes_count += 1

            replied_status = row[3].strip().upper() if len(row) > 3 else ''
            replied_to_my_email = row[5].strip() if len(row) > 5 else ''

            if replied_status == 'YES!' and replied_to_my_email:
                my_replied_senders.append(replied_to_my_email)

        updates = [
            {'range': 'J1', 'values': [['Sent total']]},
            {'range': 'J2', 'values': [[sent_yes_count]]},
            {'range': 'N1', 'values': [['All replies']]},
            {'range': 'N2', 'values': [[len(my_replied_senders)]]},
            {'range': 'N3:N200', 'values': [[""]] * 198} 
        ]

        if my_replied_senders:
            sender_cells = [[s] for s in my_replied_senders]
            end_row = 2 + len(my_replied_senders)
            updates.append({
                'range': f'N3:N{end_row}',
                'values': sender_cells
            })

        sheet.batch_update(updates)
        print(f"📊 Statistika yangilandi: Sent Total = {sent_yes_count}, Replies = {len(my_replied_senders)}")

    except Exception as e:
        print(f"⚠️ Totals va Replies yangilashda xatolik: {e}")

def check_replies():
    try:
        all_vals = sheet.get_all_values()
        if len(all_vals) <= 1:
            return

        rows = all_vals[1:]
        lead_map = {}
        for idx, row in enumerate(rows):
            email_val = str(row[0]).strip().lower() if len(row) > 0 else ''
            status_val = str(row[2]).strip().upper() if len(row) > 2 else ''
            reply_val = str(row[3]).strip().upper() if len(row) > 3 else ''
            
            if email_val and status_val == 'YES' and reply_val != 'YES!':
                lead_map[email_val] = idx + 2

        if not lead_map:
            print("📭 Hozircha tekshirish uchun yangi yuborilgan xatlar yo'q.")
            return

        print("🔍 IMAP: Javoblar qidirilmoqda...")
        batch_updates_for_replies = []
        
        IGNORE_PATTERNS = [
            'delivery status', 'undeliverable', 'automatic reply', 'auto-reply',
            'out of office', 'postmaster', 'mailer-daemon', 'failure notice',
            'noreply', 'no-reply', 'bounce', 'vacation', 'away'
        ]

        for acc in ACCOUNTS:
            try:
                mail = imaplib.IMAP4_SSL(acc['imap_host'], timeout=15)
                mail.login(acc['email'], acc['password'])
                mail.select('INBOX')

                status, messages = mail.search(None, 'ALL')

                if status == 'OK' and messages[0]:
                    msg_nums = messages[0].split()
                    recent_nums = msg_nums[-20:]

                    for num in recent_nums:
                        res, msg_data = mail.fetch(num, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])')
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                parsed = email.message_from_bytes(response_part[1])
                                from_addr = email.utils.parseaddr(parsed.get('From', ''))[1].lower()
                                subject_val = str(parsed.get('Subject', '')).lower()

                                if any(ign in subject_val for ign in IGNORE_PATTERNS) or any(ign in from_addr for ign in IGNORE_PATTERNS):
                                    continue

                                if from_addr in MY_SENDER_EMAILS:
                                    continue

                                if from_addr in lead_map:
                                    row_num = lead_map[from_addr]
                                    batch_updates_for_replies.append({'range': f'D{row_num}', 'values': [['YES!']]})
                                    batch_updates_for_replies.append({'range': f'F{row_num}', 'values': [[acc['email']]]})
                                    
                                    print(f"🎉 HAQIQIY JAVOB TOPILDI! Lead: {from_addr} | Qabul qildi: {acc['email']}")
                                    del lead_map[from_addr] 

                mail.logout()
            except Exception:
                pass 

        if batch_updates_for_replies:
            sheet.batch_update(batch_updates_for_replies)
            latest_vals = sheet.get_all_values()
            update_sent_total_and_replies_summary(latest_vals)
        else:
            print("📭 Yangi javoblar topilmadi.")

    except Exception as e:
        print(f"⚠️ IMAP umumiy tekshiruvida xato: {e}")

def calculate_daily_limit(acc, days_passed):
    base_limit = 15 + (days_passed * 5)
    return min(base_limit, 50) if acc['type'] == 'gmail' else min(base_limit, 100)

def main():
    print("🚀 Uzluksiz (24/7) yuborish tizimi Railway'da ishga tushdi...")

    # Sarlavhalarni tayyorlash
    try:
        sheet.batch_update([
            {'range': 'P1', 'values': [['FollowupStage']]},
            {'range': 'Q1', 'values': [['LastFUSentTime']]}
        ])
    except Exception as e:
        print(f"⚠️ Sarlavhalarni yangilashda ogohlantirish: {e}")

    account_index = 0

    # 24/7 UZLUKSIZ ISHLASH SIKLI
    while True:
        # Har bir aylanish boshida yangi kelgan javoblarni tekshirish
        check_replies()

        time.sleep(1)
        all_values = sheet.get_all_values()
        if len(all_values) <= 1:
            print("✅ Hozircha yuboriladigan xat yo'q. 3 daqiqa kutib qayta tekshiriladi...")
            time.sleep(180)
            continue

        rows = all_values[1:]

        pending_idx = None
        pending_lead = None
        is_followup = False
        next_stage = 0

        now_uzb = get_uzb_now()

        # 1. BIRINCHI NAVBATDA FOLLOW-UP'LARNI TEKSHIRISH
        for idx, row in enumerate(rows):
            email_val = row[0].strip() if len(row) > 0 else ''
            status_val = row[2].strip().upper() if len(row) > 2 else ''
            reply_val = row[3].strip().upper() if len(row) > 3 else ''
            
            fu_stage_str = row[15].strip() if len(row) > 15 else '0'  # P ustuni
            last_fu_time_str = row[16].strip() if len(row) > 16 else (row[10].strip() if len(row) > 10 else '') # Q yoki K ustuni

            fu_stage = int(fu_stage_str) if fu_stage_str.isdigit() else 0

            if email_val and status_val == 'YES' and reply_val != 'YES!' and fu_stage < 3 and last_fu_time_str:
                try:
                    last_time = datetime.strptime(last_fu_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UZB_TZ)
                    days_diff = (now_uzb - last_time).total_seconds() / 86400

                    if fu_stage == 0 and days_diff >= 2:
                        pending_idx = idx + 2
                        next_stage = 1
                        is_followup = True
                    elif fu_stage == 1 and days_diff >= 3:
                        pending_idx = idx + 2
                        next_stage = 2
                        is_followup = True
                    elif fu_stage == 2 and days_diff >= 2:
                        pending_idx = idx + 2
                        next_stage = 3
                        is_followup = True

                    if is_followup:
                        pending_lead = {
                            'Email': email_val,
                            'Name': row[1].strip() if len(row) > 1 else '',
                            'SenderEmail': row[4].strip() if len(row) > 4 else ''
                        }
                        break
                except Exception:
                    pass

        # 2. AGAR FOLLOW-UP YO'Q BO'LSA, YANGI LEAD QIDIRISH
        if not pending_lead:
            for row in rows:
                e_val = row[0].strip().lower() if len(row) > 0 else ''
                s_val = row[2].strip().upper() if len(row) > 2 else ''
                if e_val and s_val in ['YES', 'FAILED', 'SENDING...']:
                    GLOBAL_SENT_CACHE.add(e_val)

            for idx, row in enumerate(rows):
                email_val = row[0].strip() if len(row) > 0 else ''
                email_lower = email_val.lower()
                status_val = row[2].strip().upper() if len(row) > 2 else ''
                
                if email_val and status_val not in ['YES', 'FAILED', 'SENDING...'] and email_lower not in GLOBAL_SENT_CACHE:
                    pending_idx = idx + 2
                    pending_lead = {
                        'Email': email_val,
                        'Name': row[1].strip() if len(row) > 1 else ''
                    }
                    break

        if not pending_lead:
            print("✅ Hozircha yuboriladigan yangi xat ham, Follow-Up ham yo'q! 3 daqiqadan so'ng qayta tekshiriladi...")
            update_sent_total_and_replies_summary(sheet.get_all_values())
            time.sleep(180)
            continue

        lead_email_clean = pending_lead['Email'].lower()
        if not is_followup:
            GLOBAL_SENT_CACHE.add(lead_email_clean)
            sheet.update_cell(pending_idx, 3, "SENDING...")

        today_uzb = get_uzb_now()
        today_str = today_uzb.strftime("%Y-%m-%d")

        start_date_str = all_values[1][11].strip() if len(all_values) > 1 and len(all_values[1]) > 11 else ''
        if not start_date_str:
            start_date_str = today_str
            sheet.batch_update([
                {'range': 'L1', 'values': [['StartDate']]},
                {'range': 'L2', 'values': [[start_date_str]]}
            ])
            days_passed = 0
        else:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                days_passed = (today_uzb.replace(tzinfo=None) - start_date).days
                if days_passed < 0: days_passed = 0
            except Exception:
                days_passed = 0

        last_sent_date = all_values[1][12].strip() if len(all_values) > 1 and len(all_values[1]) > 12 else ''
        is_new_day = (last_sent_date != today_str)

        if is_new_day:
            sheet.batch_update([
                {'range': 'M1', 'values': [['LastDate']]},
                {'range': 'M2', 'values': [[today_str]]}
            ])

        sheet.update_cell(1, 9, "TodaySent") 

        sender_stats = {}
        for idx, row in enumerate(rows):
            g_val = row[6].strip() if len(row) > 6 else '' 
            h_val = row[7].strip() if len(row) > 7 else '0' 
            i_val = row[8].strip() if len(row) > 8 else '0' 

            if g_val:
                today_cnt = 0 if is_new_day else (int(i_val) if i_val.isdigit() else 0)
                if is_new_day:
                    sheet.update_cell(idx + 2, 9, 0)

                sender_stats[g_val] = {
                    'row': idx + 2,
                    'count': int(h_val) if h_val.isdigit() else 0,
                    'today_count': today_cnt
                }

        selected_acc = None
        if is_followup and pending_lead.get('SenderEmail'):
            for acc in ACCOUNTS:
                if acc['email'].lower() == pending_lead['SenderEmail'].lower():
                    selected_acc = acc
                    break

        if not selected_acc:
            num_accounts = len(ACCOUNTS)
            for _ in range(num_accounts):
                acc = ACCOUNTS[account_index % num_accounts]
                account_index += 1
                
                stats = sender_stats.get(acc['email'], {'count': 0, 'today_count': 0})
                max_daily = calculate_daily_limit(acc, days_passed)

                if stats['today_count'] < max_daily:
                    selected_acc = acc
                    break

        if not selected_acc:
            print("🛑 Barcha pochtalar bugungi limitga yetdi. 10 daqiqa kutilmoqda...")
            if not is_followup:
                sheet.update_cell(pending_idx, 3, "")
            time.sleep(600)
            continue

        lead_email = pending_lead['Email']
        lead_name = pending_lead['Name']

        if is_followup:
            fu_tmpl = FOLLOWUP_TEMPLATES[next_stage]
            subject = fu_tmpl['subject'].format(original_subject="Quick question")
            body = fu_tmpl['body']
            print(f"🔄 Follow-Up #{next_stage} yuborilmoqda: {selected_acc['email']} -> {lead_email}")
        else:
            if lead_name:
                all_templates = TEMPLATE_WITH_NAME + TEMPLATES_WITHOUT_NAME
                selected = random.choice(all_templates)
                subject = selected['subject'].format(name=lead_name)
                body = selected['body'].format(name=lead_name)
            else:
                selected = random.choice(TEMPLATES_WITHOUT_NAME)
                subject = selected['subject']
                body = selected['body']
            print(f"📧 Birinchi Xat yuborilmoqda: {selected_acc['email']} -> {lead_email}")

        is_sent = send_email_real(selected_acc, lead_email, subject, body)

        if is_sent:
            uzb_time_str = get_uzb_now().strftime("%Y-%m-%d %H:%M:%S")
            
            if is_followup:
                sheet.batch_update([
                    {'range': f'P{pending_idx}', 'values': [[next_stage]]},
                    {'range': f'Q{pending_idx}', 'values': [[uzb_time_str]]}
                ])
            else:
                row_updates = [
                    {'range': f'C{pending_idx}', 'values': [['YES']]},                     
                    {'range': f'E{pending_idx}', 'values': [[selected_acc['email']]]},     
                    {'range': 'K1', 'values': [['Time sent']]},                            
                    {'range': f'K{pending_idx}', 'values': [[uzb_time_str]]},
                    {'range': f'P{pending_idx}', 'values': [[0]]},
                    {'range': f'Q{pending_idx}', 'values': [[uzb_time_str]]}
                ]
                if len(row) <= 3 or not row[3].strip():
                    row_updates.append({'range': f'D{pending_idx}', 'values': [['NO']]})   

                sheet.batch_update(row_updates)

            if selected_acc['email'] in sender_stats:
                r = sender_stats[selected_acc['email']]['row']
                new_total = sender_stats[selected_acc['email']]['count'] + 1
                new_today = sender_stats[selected_acc['email']]['today_count'] + 1
                sheet.batch_update([
                    {'range': f'H{r}:I{r}', 'values': [[new_total, new_today]]}
                ])

            curr_vals = sheet.get_all_values()
            update_sent_total_and_replies_summary(curr_vals)
        else:
            if not is_followup:
                sheet.update_cell(pending_idx, 3, "FAILED")

        delay = random.randint(15, 25)
        print(f"⏳ {delay} sekund kutilmoqda...\n")
        time.sleep(delay)

if __name__ == "__main__":
    main()
