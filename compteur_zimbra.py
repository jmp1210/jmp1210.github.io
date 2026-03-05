#!/usr/bin/env python3
"""
Compteur 2026 - incrémente de 1 pour chaque nouveau mail UL-DN-INFRA sur Zimbra.
Stocke le dernier message_id vu pour éviter les doublons.
Usage: python3 compteur_zimbra.py [check|get]
  check = vérifie Zimbra et incrémente si nouveau UL-DN-INFRA
  get   = affiche le compteur actuel (JSON)
"""
import imaplib, json, sys, os, email
from datetime import datetime, timedelta

DIR = os.path.dirname(os.path.abspath(__file__))
COMPTEUR_FILE = os.path.join(DIR, 'compteur_2026.json')
STATE_FILE = os.path.join(DIR, 'compteur_state.json')
CRED_FILE = os.path.join(DIR, '.zimbra_credentials')

def load_creds():
    creds = {}
    with open(CRED_FILE) as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k.strip()] = v.strip()
    return creds

def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def check():
    creds = load_creds()
    state = load_json(STATE_FILE, {"seen_uids": []})
    compteur = load_json(COMPTEUR_FILE, {"count": 170})

    mail_conn = imaplib.IMAP4_SSL('mail.univ-lorraine.fr')
    mail_conn.login(creds.get('login', creds.get('user', '')),
                    creds.get('password', ''))
    mail_conn.select('INBOX', readonly=True)

    # Chercher les mails UL-DN-INFRA des dernières 24h
    since = (datetime.utcnow() - timedelta(hours=24)).strftime('%d-%b-%Y')
    _, data = mail_conn.search(None, f'(SINCE {since} FROM "UL-DN-INFRA")')

    new_count = 0
    seen = set(state.get("seen_uids", []))

    if data[0]:
        uids = data[0].split()
        for uid in uids:
            uid_str = uid.decode()
            if uid_str not in seen:
                seen.add(uid_str)
                new_count += 1

    mail_conn.logout()

    if new_count > 0:
        compteur["count"] += new_count
        compteur["updated"] = datetime.utcnow().isoformat() + "Z"
        save_json(COMPTEUR_FILE, compteur)

    # Garder seulement les 200 derniers UIDs
    state["seen_uids"] = list(seen)[-200:]
    state["last_check"] = datetime.utcnow().isoformat() + "Z"
    save_json(STATE_FILE, state)

    print(f"+{new_count} → total {compteur['count']}")

def get():
    compteur = load_json(COMPTEUR_FILE, {"count": 170})
    print(json.dumps(compteur))

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'get'
    if cmd == 'check':
        check()
    else:
        get()
