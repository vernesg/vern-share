#!/usr/bin/env python3
import requests, os, re, sys, json, time, random
from datetime import datetime

# Session object
ses = requests.Session()

# Config (admin-only use)
ADMIN_UID = "100010099516674"  

# Random user agents
ua_list = [
    "Mozilla/5.0 (Linux; Android 10; Wildfire E Lite...)",
    "Mozilla/5.0 (Linux; Android 11; KINGKONG 5 Pro...)",
    "Mozilla/5.0 (Linux; Android 11; G91 Pro...)"
]
ua = random.choice(ua_list)

# Helper
def color(text, code): return f"\033[{code}m{text}\033[0m"
def banner():
    os.system("clear")
    print(color("SPAMSHARE - ACEBOOK AUTO SHARE ", '94'))
    print(color("Author  : VERN", '96'))
    print(color("Warning : THIS TOOL IS PREMIUM!", '91'))
    print("-" * 50)

# Simple XOR encoding for cookie/token
def xor_encrypt(text, key='mykey'):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))

def login():
    banner()
    print(color("Enter your Facebook cookie (Admin only)", '93'))
    cookie_input = input(color("Cookie: ", '92'))
    cookies = {i.split("=")[0]: i.split("=")[1] for i in cookie_input.split("; ") if "=" in i}

    try:
        res = ses.get("https://business.facebook.com/business_locations", headers={
            "user-agent": ua,
            "referer": "https://www.facebook.com/",
            "origin": "https://business.facebook.com",
            "accept-language": "en-US",
            "accept": "text/html"
        }, cookies=cookies)

        token_match = re.search(r"(EAAG\w+)", res.text)
        if not token_match:
            print(color("❌ Token extraction failed. Check your cookie.", '91'))
            return login()

        token = token_match.group(1)

        # Verify admin UID
        me = ses.get(f"https://graph.facebook.com/me?access_token={token}").json()
        if me.get("id") != ADMIN_UID:
            print(color("❌ Unauthorized user. Access denied.", '91'))
            return

        # Save encrypted (for personal reuse)
        with open("data.secure", "w") as f:
            f.write(json.dumps({
                "token": xor_encrypt(token),
                "cookie": xor_encrypt(cookie_input)
            }))

        print(color(f"✅ Token extracted and saved securely.", '92'))
        bot()

    except Exception as e:
        print(color("Login error. Please retry.", '91'))
        login()

def bot():
    os.system("clear")
    banner()
    try:
        # Load encrypted token and cookie
        with open("data.secure") as f:
            data = json.loads(f.read())
            token = xor_encrypt(data['token'])
            raw_cookie = xor_encrypt(data['cookie'])
            cookie = {i.split("=")[0]: i.split("=")[1] for i in raw_cookie.split("; ") if "=" in i}
    except:
        print(color("No valid session found. Please login again.", '91'))
        return login()

    link = input(color("Enter the Facebook post link: ", '96'))
    try:
        limit = int(input(color("How many times to share?: ", '96')))
    except ValueError:
        print(color("Limit must be a number.", '91'))
        return bot()

    print(color("Processing your request. Please wait...", '93'))
    start_time = datetime.now()

    for n in range(1, limit + 1):
        try:
            res = ses.post(
                f"https://graph.facebook.com/v13.0/me/feed?link={link}&published=0&access_token={token}",
                headers={"user-agent": ua},
                cookies=cookie
            ).text

            data = json.loads(res)
            if "id" in data:
                elapsed = str(datetime.now() - start_time).split('.')[0]
                print(color(f"✅ Share #{n} completed ({elapsed})", '92'))
            else:
                print(color("⚠️ Possible token or cookie expired.", '91'))
                break

        except requests.exceptions.ConnectionError:
            print(color("❌ Network issue. Please check your connection.", '91'))
            break

if __name__ == "__main__":
    login()
