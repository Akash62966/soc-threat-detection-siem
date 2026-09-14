import re
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "account", "banking", "secure", "update",
    "signin", "paypal", "free", "token", "claim", "webmail",
    "checkpoint", "ssn", "recovery", "confirm", "wallet"
]

FEATURE_NAMES = [
    "url_length",
    "hostname_length",
    "dot_count",
    "hyphen_count",
    "at_symbol_count",
    "slash_count",
    "double_slash_count",
    "has_ip",
    "has_https",
    "num_subdomains",
    "digit_ratio",
    "suspicious_keyword_count"
]

def extract_features_from_url(url_str):
    """
    Extracts numerical feature vector from a URL string.
    Returns dict of feature_name -> value.
    """
    url = str(url_str).strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url_with_proto = "http://" + url
    else:
        url_with_proto = url

    try:
        parsed = urlparse(url_with_proto)
        hostname = parsed.hostname or ""
        path = parsed.path or ""
    except Exception:
        hostname = ""
        path = ""

    url_len = len(url)
    host_len = len(hostname)
    dot_cnt = url.count(".")
    hyphen_cnt = url.count("-")
    at_cnt = url.count("@")
    slash_cnt = url.count("/")
    
    # Check double slash in path (excluding protocol)
    path_and_query = url_with_proto[url_with_proto.find("://")+3:]
    double_slash = 1 if "//" in path_and_query else 0

    # IP address check
    ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    has_ip = 1 if re.match(ip_pattern, hostname) else 0

    # HTTPS check
    has_https = 1 if url.lower().startswith("https://") else 0

    # Subdomains count
    parts = hostname.split(".")
    if len(parts) > 2:
        num_subdomains = len(parts) - 2
    else:
        num_subdomains = 0

    # Digit ratio
    digits_cnt = sum(c.isdigit() for c in url)
    digit_ratio = (digits_cnt / url_len) if url_len > 0 else 0.0

    # Suspicious keyword count
    url_lower = url.lower()
    kw_cnt = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)

    return {
        "url_length": url_len,
        "hostname_length": host_len,
        "dot_count": dot_cnt,
        "hyphen_count": hyphen_cnt,
        "at_symbol_count": at_cnt,
        "slash_count": slash_cnt,
        "double_slash_count": double_slash,
        "has_ip": has_ip,
        "has_https": has_https,
        "num_subdomains": num_subdomains,
        "digit_ratio": round(digit_ratio, 4),
        "suspicious_keyword_count": kw_cnt
    }

def get_feature_vector(url_str):
    feat_dict = extract_features_from_url(url_str)
    return [feat_dict[name] for name in FEATURE_NAMES]

def explain_features(url_str):
    feats = extract_features_from_url(url_str)
    reasons = []

    if feats["has_ip"] == 1:
        reasons.append("URL uses an raw IP address instead of a domain name (common in phishing).")
    if feats["has_https"] == 0:
        reasons.append("URL uses insecure HTTP protocol instead of encrypted HTTPS.")
    if feats["at_symbol_count"] > 0:
        reasons.append(f"URL contains '@' symbol ({feats['at_symbol_count']} times), which can obscure the real destination host.")
    if feats["suspicious_keyword_count"] >= 2:
        reasons.append(f"Contains multiple high-risk authentication keywords ({feats['suspicious_keyword_count']} detected).")
    if feats["hyphen_count"] >= 3:
        reasons.append(f"High hyphen density ({feats['hyphen_count']} hyphens) often used in typosquatting / domain spoofing.")
    if feats["num_subdomains"] >= 2:
        reasons.append(f"Excessive subdomains ({feats['num_subdomains']} subdomains) attempting to mimic legitimate brand hierarchies.")
    if feats["url_length"] > 75:
        reasons.append(f"Excessively long URL length ({feats['url_length']} characters) hiding suspicious tokens.")

    if not reasons:
        reasons.append("URL exhibits standard structural characteristics with no obvious lexical anomalies detected.")

    return reasons
