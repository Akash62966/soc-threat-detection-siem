import csv
import os
import random

# Reliable domains for Legitimate URLs
LEGITIMATE_DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "wikipedia.org", "yahoo.com",
    "amazon.com", "github.com", "microsoft.com", "apple.com", "twitter.com",
    "linkedin.com", "instagram.com", "netflix.com", "stackoverflow.com",
    "reddit.com", "adobe.com", "wordpress.org", "mozilla.org", "dropbox.com",
    "cloudflare.com", "medium.com", "spotify.com", "zoom.us", "paypal.com",
    "bankofamerica.com", "chase.com", "wellsford.com", "slack.com", "trello.com"
]

LEGITIMATE_PATHS = [
    "", "/", "/about", "/contact", "/help/center", "/login", "/user/profile",
    "/docs/v2/api", "/search?q=cybersecurity", "/settings/security",
    "/dashboard/main", "/products/category/item?id=4920", "/blog/post/2026/09"
]

# Suspicious keywords for Phishing URLs
PHISHING_KEYWORDS = [
    "secure-login", "account-verify", "banking-update", "paypal-security-alert",
    "apple-id-recovery", "microsoft-online-auth", "confirm-identity",
    "free-gift-claim", "wallet-validation", "support-ticket-update",
    "webmail-login-portal", "unusual-activity-flag", "ssn-verification-required"
]

PHISHING_DOMAINS = [
    "secure-auth-login-check.com", "paypal-account-update-alert.net",
    "appleid-verify-service.org", "microsoft365-online-portal.info",
    "bankofamerica-secure-login.xyz", "chase-account-validation.top",
    "192.168.1.105", "10.0.4.12", "login-banking-security-update.club",
    "account-recovery-portal-2026.online", "verify-your-credentials-now.tech"
]

PHISHING_PATHS = [
    "/login.php?user=admin&token=89234892", "/verify/@account/update",
    "/secure/auth.php?id=9201940&session=active", "/claim/free-tokens/@user",
    "/webmail/login?redirect=external", "/banking/validate-ssn.html",
    "/auth/checkpoint?usr=victim@example.com"
]

def generate_dataset():
    data = []
    
    # 1. Legitimate URLs (Label 0)
    for i in range(600):
        domain = random.choice(LEGITIMATE_DOMAINS)
        sub = random.choice(["", "www.", "m.", "blog.", "support.", "api."])
        path = random.choice(LEGITIMATE_PATHS)
        url = f"https://{sub}{domain}{path}"
        data.append({"url": url, "label": 0})

    # 2. Phishing URLs (Label 1)
    for i in range(600):
        protocol = random.choice(["http://", "https://", "http://"])
        if random.random() < 0.25:
            # IP-based URL
            ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
            path = random.choice(PHISHING_PATHS)
            url = f"{protocol}{ip}{path}"
        else:
            domain = random.choice(PHISHING_DOMAINS)
            kw = random.choice(PHISHING_KEYWORDS)
            sub = random.choice(["login.", "secure.", "update.", "auth.", "verify.", "account."])
            path = random.choice(PHISHING_PATHS)
            url = f"{protocol}{sub}{kw}-{domain}{path}"
        data.append({"url": url, "label": 1})

    random.shuffle(data)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "phishing_urls.csv")

    with open(out_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "label"])
        writer.writeheader()
        writer.writerows(data)

    print(f"Dataset generated with {len(data)} rows at {out_path}")

if __name__ == "__main__":
    generate_dataset()
