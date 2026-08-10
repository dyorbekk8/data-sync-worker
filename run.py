import os
import time
import random
import json
import smtplib
import imaplib
import email
import socket
import traceback
import sys
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor
import gspread

# --- RAILWAY / CLOUD SERVERLARDA IPv6 UNREACHABLE XATOSINI TUBDAN TUZATISH ---
orig_create_connection = socket.create_connection

def create_connection_ipv4(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
    host, port = address
    err = None
    for res in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sa)
            return sock
        except socket.error as _:
            err = _
            if sock is not None:
                sock.close()
    if err is not None:
        raise err
    else:
        raise socket.error("getaddrinfo returns empty list")

socket.create_connection = create_connection_ipv4
# --------------------------------------------------------------------------

from sender import ACCOUNTS
from templates import TEMPLATE_WITH_NAME, TEMPLATES_WITHOUT_NAME, FOLLOWUP_TEMPLATES

# --- GOOGLE SHEETS SETUP ---
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# --- CREDENTIALS YUKLASH ---
CREDS_FILE = "creds.json"
creds_dict = None

if os.path.exists(CREDS_FILE):
    try:
        with open(CREDS_FILE, "r") as f:
            creds_dict = json.load(f)
    except Exception as e:
        print(f"⚠️ creds.json faylini o'qishda xatolik: {e}", flush=True)

if not creds_dict:
    creds_json = os.environ.get("GOOGLE_CREDENTIALS") or os.environ.get("GOOGLE_OAUTH_JSON")
    if creds_json:
        try:
            creds_dict = json.loads(creds_json, strict=False)
        except Exception as e:
            print(f"⚠️ Environment Variable'dan JSON parsing xatoligi: {e}", flush=True)

if not creds_dict:
    raise ValueError("❌ Na 'creds.json' fayli va na 'GOOGLE_CREDENTIALS' environment variable topildi!")

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
MY_SENDER_EMAILS = set(acc['email'].lower().strip() for acc in ACCOUNTS)

def get_uzb_now():
    return datetime.now(UZB_TZ)

def save_to_sent_folder(acc, msg):
    if acc.get('type') == 'gmail':
        return
    try:
        mail = imaplib.IMAP4_SSL(acc['imap_host'], timeout=30)
        mail.login(acc['email'], acc['password'])
        mail.append('Sent', '\\Seen', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        mail.logout()
    except Exception as e:
        print(f"⚠️ Sent papkasiga saqlashda IMAP xatolik ({acc['email']}): {e}", flush=True)

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
            print(f"❌ XAT RAD ETILDI (Refused Recipients): {refused}", flush=True)
            return False

        save_to_sent_folder(acc, msg)
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP AUTHENTICATION ERROR ({acc['email']}): Login yoki Parol noto'g'ri! Detal: {e}", flush=True)
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP CONNECT ERROR ({acc['email']}): Serverga ulanib bo'lmadi! Host: {smtp_host}:{smtp_port}. Detal: {e}", flush=True)
        return False
    except socket.timeout as e:
        print(f"❌ SMTP TIMEOUT ERROR ({acc['email']}): Server javob berish vaqti tugadi (20s). Detal: {e}", flush=True)
        return False
    except Exception as e:
        print(f"❌ UMUMIY SMTP XATOLIK ({acc['email']} -> {to_email}): {e}", flush=True)
        traceback.print_exc()
        return False

def update_sent_total_and_replies_summary(all_values):
    try:
        if len(all_values) <= 1:
            return

        rows = all_values[1:]
        sent_yes_count = 0
        my_replied_senders = []
        reply_times = []

        for row in rows:
            status_val = row[2].strip().upper() if len(row) > 2 else ''
            if status_val == 'YES':
                sent_yes_count += 1

            replied_status = row[3].strip().upper() if len(row) > 3 else ''
            replied_to_my_email = row[5].strip() if len(row) > 5 else ''
            reply_time_val = row[14].strip() if len(row) > 14 else ''

            if replied_status == 'YES!' and replied_to_my_email:
                my_replied_senders.append(replied_to_my_email)
                reply_times.append(reply_time_val)

        updates = [
            {'range': 'J1', 'values': [['Sent total']]},
            {'range': 'J2', 'values': [[sent_yes_count]]},
            {'range': 'N1', 'values': [['All replies']]},
            {'range': 'N2', 'values': [[len(my_replied_senders)]]},
            {'range': 'O1', 'values': [['Reply Time']]},
            {'range': 'N3:N200', 'values': [[""]] * 198},
            {'range': 'O3:O200', 'values': [[""]] * 198}
        ]

        if my_replied_senders:
            sender_cells = [[s] for s in my_replied_senders]
            time_cells = [[t] for t in reply_times]
            end_row = 2 + len(my_replied_senders)
            updates.append({
                'range': f'N3:N{end_row}',
                'values': sender_cells
            })
            updates.append({
                'range': f'O3:O{end_row}',
                'values': time_cells
            })

        sheet.batch_update(updates)
        print(f"📊 Statistika yangilandi: Sent Total = {sent_yes_count}, Replies = {len(my_replied_senders)}", flush=True)

    except Exception as e:
        print(f"⚠️ Totals va Replies yangilashda xatolik: {e}", flush=True)

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
            print("📭 Hozircha tekshirish uchun yangi yuborilgan xatlar yo'q.", flush=True)
            return

        print("🔍 IMAP: Javoblar qidirilmoqda...", flush=True)
        batch_updates_for_replies = []
        
        IGNORE_PATTERNS = [
            'delivery status', 'undeliverable', 'automatic reply', 'auto-reply',
            'out of office', 'postmaster', 'mailer-daemon', 'failure notice',
            'noreply', 'no-reply', 'bounce', 'vacation', 'away'
        ]

        for acc in ACCOUNTS:
            try:
                mail = imaplib.IMAP4_SSL(acc['imap_host'], timeout=30)
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
                                    uzb_reply_time = get_uzb_now().strftime("%Y-%m-%d %H:%M:%S")
                                    batch_updates_for_replies.append({'range': f'D{row_num}', 'values': [['YES!']]})
                                    batch_updates_for_replies.append({'range': f'F{row_num}', 'values': [[acc['email']]]})
                                    batch_updates_for_replies.append({'range': f'O{row_num}', 'values': [[uzb_reply_time]]})
                                    
                                    print(f"🎉 HAQIQIY JAVOB TOPILDI! Lead: {from_addr} | Qabul qildi: {acc['email']} | Vaqt: {uzb_reply_time}", flush=True)
                                    del lead_map[from_addr]

                mail.logout()
            except Exception as e:
                print(f"⚠️ IMAP Xatolik ({acc['email']}): {e}", flush=True)

        if batch_updates_for_replies:
            sheet.batch_update(batch_updates_for_replies)
            latest_vals = sheet.get_all_values()
            update_sent_total_and_replies_summary(latest_vals)
        else:
            print("📭 Yangi javoblar topilmadi.", flush=True)

    except Exception as e:
        print(f"⚠️ IMAP umumiy tekshiruvida xato: {e}", flush=True)

def calculate_daily_limit(acc, days_passed):
    return 30

def process_single_lead(task_info):
    pending_lead = task_info['pending_lead']
    pending_idx = task_info['pending_idx']
    is_followup = task_info['is_followup']
    next_stage = task_info['next_stage']
    selected_acc = task_info['selected_acc']
    
    lead_email = pending_lead['Email']
    lead_name = pending_lead['Name']
    lead_company = pending_lead['Company']

    if is_followup:
        fu_tmpl = FOLLOWUP_TEMPLATES[0]  # Faqat 1 ta follow-up shabloni
        subject = fu_tmpl['subject']
        body = fu_tmpl['body']
        print(f"🔄 Follow-Up yuborilmoqda (PARALLEL): {selected_acc['email']} -> {lead_email}", flush=True)
    else:
        if lead_name and lead_company:
            all_templates = TEMPLATE_WITH_NAME + TEMPLATES_WITHOUT_NAME
            selected = random.choice(all_templates)
            subject = selected['subject'].format(name=lead_name, company=lead_company)
            body = selected['body'].format(name=lead_name, company=lead_company)
        elif not lead_name and lead_company:
            selected = random.choice(TEMPLATES_WITHOUT_NAME[:3])
            subject = selected['subject'].format(company=lead_company)
            body = selected['body'].format(company=lead_company)
        else:
            selected = random.choice(TEMPLATES_WITHOUT_NAME[3:])
            subject = selected['subject']
            body = selected['body']
        print(f"📧 Birinchi Xat yuborilmoqda (PARALLEL): {selected_acc['email']} -> {lead_email}", flush=True)

    is_sent = send_email_real(selected_acc, lead_email, subject, body)

    return {
        'is_sent': is_sent,
        'pending_idx': pending_idx,
        'is_followup': is_followup,
        'next_stage': next_stage,
        'selected_acc': selected_acc,
        'lead_email': lead_email
    }

def main():
    print(f"🚀 Uzluksiz va Parallel yuborish tizimi ishga tushdi... (Jamlangan akkauntlar soni: {len(ACCOUNTS)})", flush=True)

    try:
        sheet.batch_update([
            {'range': 'F1', 'values': [['MaxLimit']]},
            {'range': 'O1', 'values': [['Reply Time']]},
            {'range': 'P1', 'values': [['FollowupStage']]},
            {'range': 'Q1', 'values': [['LastFUSentTime']]}
        ])
    except Exception as e:
        print(f"⚠️ Sarlavhalarni yangilashda ogohlantirish: {e}", flush=True)

    cycle_count = 0

    while True:
        cycle_count += 1
        if cycle_count % 5 == 1:
            check_replies()

        time.sleep(1)
        all_values = sheet.get_all_values()
        if len(all_values) <= 1:
            print("✅ Sheet bo'sh. 3 daqiqa kutib qayta tekshiriladi...", flush=True)
            time.sleep(180)
            continue

        rows = all_values[1:]
        now_uzb = get_uzb_now()

        tasks_to_run = []
        used_lead_indices = set()
        sending_status_updates = []

        # 1. BIRINCHI SLOT: FAQAT 1 TA FOLLOW-UP OLADI
        for idx, row in enumerate(rows):
            email_val = row[0].strip() if len(row) > 0 else ''
            status_val = row[2].strip().upper() if len(row) > 2 else ''
            reply_val = row[3].strip().upper() if len(row) > 3 else ''
            
            fu_stage_str = row[15].strip() if len(row) > 15 else '0'  
            last_fu_time_str = row[16].strip() if len(row) > 16 else (row[10].strip() if len(row) > 10 else '') 

            fu_stage = int(fu_stage_str) if fu_stage_str.isdigit() else 0

            # 1 ta follow-up bo'lgani uchun fu_stage < 1 tekshiriladi
            if email_val and status_val == 'YES' and reply_val != 'YES!' and fu_stage < 1 and last_fu_time_str:
                try:
                    last_time = datetime.strptime(last_fu_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UZB_TZ)
                    days_diff = (now_uzb - last_time).total_seconds() / 86400

                    is_fu = False
                    next_s = 0

                    if fu_stage == 0 and days_diff >= 2:
                        next_s = 1; is_fu = True

                    if is_fu:
                        p_idx = idx + 2
                        used_lead_indices.add(p_idx)
                        tasks_to_run.append({
                            'pending_idx': p_idx,
                            'pending_lead': {
                                'Email': email_val,
                                'Name': row[1].strip() if len(row) > 1 else '',
                                'Company': row[17].strip() if len(row) > 17 else '',
                                'SenderEmail': row[4].strip() if len(row) > 4 else ''
                            },
                            'is_followup': True,
                            'next_stage': next_s
                        })
                        break
                except Exception as ex:
                    print(f"⚠️ Sana parsing xatosi (Qator {idx+2}): {ex}", flush=True)

        # 2. IKKINCHI SLOT: FAQAT YANGI LEAD OLADI
        for row in rows:
            e_val = row[0].strip().lower() if len(row) > 0 else ''
            s_val = row[2].strip().upper() if len(row) > 2 else ''
            if e_val and s_val in ['YES', 'FAILED', 'SENDING...']:
                GLOBAL_SENT_CACHE.add(e_val)

        for idx, row in enumerate(rows):
            if len(tasks_to_run) >= 2:
                break

            p_idx = idx + 2
            if p_idx in used_lead_indices:
                continue

            email_val = row[0].strip() if len(row) > 0 else ''
            email_lower = email_val.lower()
            status_val = row[2].strip().upper() if len(row) > 2 else ''
            
            if email_val and status_val not in ['YES', 'FAILED', 'SENDING...'] and email_lower not in GLOBAL_SENT_CACHE:
                GLOBAL_SENT_CACHE.add(email_lower)
                used_lead_indices.add(p_idx)
                
                sending_status_updates.append({'range': f'C{p_idx}', 'values': [['SENDING...']]})
                
                tasks_to_run.append({
                    'pending_idx': p_idx,
                    'pending_lead': {
                        'Email': email_val,
                        'Name': row[1].strip() if len(row) > 1 else '',
                        'Company': row[17].strip() if len(row) > 17 else ''
                    },
                    'is_followup': False,
                    'next_stage': 0
                })

        # 3. AGAR BIRORTA HAM YANGI LEAD BO'LMASA, 2-SLOTGA HAM FOLLOW-UP OLADI
        if len(tasks_to_run) == 1 and tasks_to_run[0]['is_followup']:
            for idx, row in enumerate(rows):
                p_idx = idx + 2
                if p_idx in used_lead_indices:
                    continue

                email_val = row[0].strip() if len(row) > 0 else ''
                status_val = row[2].strip().upper() if len(row) > 2 else ''
                reply_val = row[3].strip().upper() if len(row) > 3 else ''
                fu_stage_str = row[15].strip() if len(row) > 15 else '0'  
                last_fu_time_str = row[16].strip() if len(row) > 16 else (row[10].strip() if len(row) > 10 else '') 
                fu_stage = int(fu_stage_str) if fu_stage_str.isdigit() else 0

                if email_val and status_val == 'YES' and reply_val != 'YES!' and fu_stage < 1 and last_fu_time_str:
                    try:
                        last_time = datetime.strptime(last_fu_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UZB_TZ)
                        days_diff = (now_uzb - last_time).total_seconds() / 86400

                        is_fu = False
                        next_s = 0
                        if fu_stage == 0 and days_diff >= 2: next_s = 1; is_fu = True

                        if is_fu:
                            used_lead_indices.add(p_idx)
                            tasks_to_run.append({
                                'pending_idx': p_idx,
                                'pending_lead': {
                                    'Email': email_val,
                                    'Name': row[1].strip() if len(row) > 1 else '',
                                    'Company': row[17].strip() if len(row) > 17 else '',
                                    'SenderEmail': row[4].strip() if len(row) > 4 else ''
                                },
                                'is_followup': True,
                                'next_stage': next_s
                            })
                            break
                    except Exception:
                        pass

        if not tasks_to_run:
            print("✅ Hozircha yuboriladigan yangi xat ham, Follow-Up ham yo'q! 3 daqiqadan so'ng qayta tekshiriladi...", flush=True)
            update_sent_total_and_replies_summary(sheet.get_all_values())
            time.sleep(180)
            continue

        if sending_status_updates:
            try:
                sheet.batch_update(sending_status_updates)
            except Exception as e:
                print(f"⚠️ SENDING... statuslarini yangilashda xatolik: {e}", flush=True)

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

        # --- SENDER STATS O'QISH ---
        sender_stats = {}
        limit_updates = []

        for idx, row in enumerate(rows):
            g_val = row[6].strip().lower() if len(row) > 6 else '' 
            h_val = row[7].strip() if len(row) > 7 else '0' 
            i_val = row[8].strip() if len(row) > 8 else '0' 

            if g_val and "@" in g_val:
                today_cnt = 0 if is_new_day else (int(i_val) if i_val.isdigit() else 0)
                if is_new_day:
                    sheet.update_cell(idx + 2, 9, 0)

                acc_obj = next((acc for acc in ACCOUNTS if acc['email'].lower().strip() == g_val), {'type': 'domain'})
                max_daily = calculate_daily_limit(acc_obj, days_passed)

                limit_updates.append({'range': f'F{idx + 2}', 'values': [[max_daily]]})

                sender_stats[g_val] = {
                    'row': idx + 2,
                    'count': int(h_val) if h_val.isdigit() else 0,
                    'today_count': today_cnt,
                    'max_daily': max_daily
                }

        if limit_updates:
            try:
                sheet.batch_update(limit_updates)
            except Exception as e:
                print(f"⚠️ F ustuniga limitlarni yozishda xatolik: {e}", flush=True)

        used_acc_emails = set()
        final_executable_tasks = []

        for task in tasks_to_run:
            selected_acc = None
            if task['is_followup'] and task['pending_lead'].get('SenderEmail'):
                s_email = task['pending_lead']['SenderEmail'].lower().strip()
                for acc in ACCOUNTS:
                    if acc['email'].lower().strip() == s_email:
                        selected_acc = acc
                        break

            if not selected_acc:
                available_accounts = []
                for acc in ACCOUNTS:
                    clean_acc_email = acc['email'].lower().strip()
                    if clean_acc_email in used_acc_emails:
                        continue

                    st = sender_stats.get(clean_acc_email, {'count': 0, 'today_count': 0, 'max_daily': 30})
                    t_count = int(st['today_count']) if str(st['today_count']).isdigit() else 0
                    m_limit = int(st['max_daily']) if str(st['max_daily']).isdigit() else 30

                    if t_count < m_limit:
                        available_accounts.append((acc, t_count))
                
                if available_accounts:
                    available_accounts.sort(key=lambda x: x[1])
                    selected_acc = available_accounts[0][0]

            if selected_acc:
                used_acc_emails.add(selected_acc['email'].lower().strip())
                task['selected_acc'] = selected_acc
                final_executable_tasks.append(task)
            else:
                if not task['is_followup']:
                    sheet.update_cell(task['pending_idx'], 3, "")

        if not final_executable_tasks:
            print("🛑 SABAB: Barcha akkauntlar bugungi limitga (30 ta) yetgan! 10 daqiqa kutilmoqda...", flush=True)
            time.sleep(600)
            continue

        # --- PARALLEL YUBORISH ---
        print(f"⚡ {len(final_executable_tasks)} ta xat PARALLEL ravishda yuborilmoqda...", flush=True)
        results = []
        with ThreadPoolExecutor(max_workers=len(final_executable_tasks)) as executor:
            futures = [executor.submit(process_single_lead, task) for task in final_executable_tasks]
            for future in futures:
                try:
                    results.append(future.result())
                except Exception as ex:
                    print(f"⚠️ Thread xatoligi: {ex}", flush=True)

        sheet_updates = []
        for res in results:
            p_idx = res['pending_idx']
            is_sent = res['is_sent']
            is_fu = res['is_followup']
            n_stage = res['next_stage']
            sel_acc = res['selected_acc']
            lead_e = res['lead_email']

            if is_sent:
                uzb_time_str = get_uzb_now().strftime("%Y-%m-%d %H:%M:%S")
                if is_fu:
                    sheet_updates.extend([
                        {'range': f'P{p_idx}', 'values': [[n_stage]]},
                        {'range': f'Q{p_idx}', 'values': [[uzb_time_str]]}
                    ])
                else:
                    sheet_updates.extend([
                        {'range': f'C{p_idx}', 'values': [['YES']]},                     
                        {'range': f'E{p_idx}', 'values': [[sel_acc['email']]]},     
                        {'range': 'K1', 'values': [['Time sent']]},                             
                        {'range': f'K{p_idx}', 'values': [[uzb_time_str]]},
                        {'range': f'P{p_idx}', 'values': [[0]]},
                        {'range': f'Q{p_idx}', 'values': [[uzb_time_str]]},
                        {'range': f'D{p_idx}', 'values': [['NO']]}
                    ])

                clean_sel_email = sel_acc['email'].lower().strip()
                if clean_sel_email in sender_stats:
                    r = sender_stats[clean_sel_email]['row']
                    new_total = sender_stats[clean_sel_email]['count'] + 1
                    new_today = sender_stats[clean_sel_email]['today_count'] + 1
                    sender_stats[clean_sel_email]['today_count'] = new_today
                    sender_stats[clean_sel_email]['count'] = new_total
                    sheet_updates.append({'range': f'H{r}:I{r}', 'values': [[new_total, new_today]]})
            else:
                print(f"❌ XAT YUBORILMADI: {sel_acc['email']} -> {lead_e}", flush=True)
                if not is_fu:
                    sheet_updates.append({'range': f'C{p_idx}', 'values': [['FAILED']]})

        if sheet_updates:
            try:
                sheet.batch_update(sheet_updates)
                update_sent_total_and_replies_summary(sheet.get_all_values())
            except Exception as e:
                print(f"⚠️ Batch update xatoligi: {e}", flush=True)

        delay = random.randint(120, 160)
        print(f"⏳ Sikl yakunlandi. {delay} sekund kutilmoqda...\n", flush=True)
        time.sleep(delay)

if __name__ == "__main__":
    main()
