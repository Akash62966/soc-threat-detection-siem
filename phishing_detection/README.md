# Phishing URL Detection Using Machine Learning

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Scikit-Learn](https://img.shields.io/badge/ML-Random%20Forest-orange)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![OLED Dark](https://img.shields.io/badge/UI-OLED%20Jet%20Black-black)

A defensive cybersecurity machine learning web application that extracts lexical, structural, and security indicators from URL strings to classify them as **Legitimate** or **Potential Phishing** without making external network connections.

---

## 📌 Problem Statement

Phishing remains one of the primary vectors for initial access and credential harvesting. Attackers use brand spoofing, typosquatting, subdomains, IP-host masking, and obfuscated paths to trick users.

This project implements a defensive machine-learning detector that parses submitted URLs as un-executed text strings, extracts 12 quantitative structural features, and runs a trained **Random Forest** classifier model to calculate phishing risk probability and provide automated explainability.

---

## 🛠️ Tech Stack & Key Technologies

- **Language**: Python 3.10+
- **Machine Learning**: Scikit-learn (Random Forest, Logistic Regression, Decision Tree, Support Vector Machine)
- **Data Engineering**: Pandas, NumPy
- **Model Serialization**: Joblib
- **Web Backend**: Flask
- **Frontend & UI**: HTML5, CSS3 (Pure OLED Jet Black Theme), JavaScript, Bootstrap 5, Chart.js
- **Testing**: Unittest

---

## 🏗️ Architecture Overview

```
phishing_detection/
├── app.py                      # Flask Backend API & Routing (Port 5051)
├── train_model.py              # ML Classifier Training & Evaluation script
├── feature_extraction.py       # 12-Indicator URL Lexical Feature Extractor
├── requirements.txt            # Python dependencies
├── model/
│   ├── phishing_model.joblib   # Serialized Random Forest model
│   ├── scaler.joblib           # Serialized StandardScaler
│   └── model_metrics.json      # Evaluation metrics (Accuracy, Precision, Recall, F1)
├── dataset/
│   ├── generate_dataset.py     # Dataset generator script
│   └── phishing_urls.csv       # 1,200 sample balanced URL dataset
├── database.py                 # SQLite scan history storage
├── static/
│   ├── css/style.css           # Pure OLED Jet Black Theme
│   └── js/app.js               # AJAX prediction handler & UI controls
├── templates/
│   ├── base.html               # Core layout
│   ├── index.html              # Scanner & URL Input view
│   ├── dashboard.html          # Scan Analytics & History view
│   ├── evaluate.html           # Model Comparison & Confusion Matrix view
│   └── dataset_view.html       # Dataset Browser & Feature Importances
├── tests/
│   ├── test_features.py        # Feature extraction unit tests
│   ├── test_model.py           # Model inference unit tests
│   └── test_api.py            # API integration unit tests
└── README.md                   # Comprehensive Documentation
```

---

## 🔍 Feature Engineering (12 Indicators Extracted)

1. `url_length`: Total character count of the URL.
2. `hostname_length`: Character length of the domain/hostname.
3. `dot_count`: Count of `.` characters in string.
4. `hyphen_count`: Count of `-` hyphens (typosquatting indicator).
5. `at_symbol_count`: Count of `@` symbols (obscuring true destination).
6. `slash_count`: Count of `/` slashes.
7. `double_slash_count`: Presence of `//` in URL path.
8. `has_ip`: `1` if hostname is an IPv4 address (e.g. `192.168.1.1`), `0` otherwise.
9. `has_https`: `1` if protocol is `https://`, `0` if `http://`.
10. `num_subdomains`: Subdomain count (e.g., `login.secure.paypal.com` $\rightarrow$ 3).
11. `digit_ratio`: Ratio of numerical digits to total URL length.
12. `suspicious_keyword_count`: Count of target authentication keywords (`login`, `verify`, `account`, `banking`, `secure`, `update`, `signin`, `paypal`, `token`, `claim`, `wallet`).

---

## 📊 Machine Learning Model Evaluation

We trained and benchmarked 4 classification algorithms on a 20% holdout test split:

| Model Algorithm | Accuracy | Precision | Recall | F1-Score | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest Classifier** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | **SELECTED TOP MODEL** |
| **Logistic Regression** | 100.0% | 100.0% | 100.0% | 100.0% | Evaluated |
| **Decision Tree Classifier** | 100.0% | 100.0% | 100.0% | 100.0% | Evaluated |
| **Support Vector Machine (SVM)**| 100.0% | 100.0% | 100.0% | 100.0% | Evaluated |

### 💡 Why Precision & Recall Matter in Phishing Detection:
- **Precision (Positive Predictive Value)**: High precision ensures legitimate corporate websites are not false-alarmed or blocked, preventing operational disruption.
- **Recall (Sensitivity)**: High recall ensures malicious phishing links are caught, preventing credential leakage.

---

## 🚀 Installation & Quick Start

```bash
# 1. Navigate to directory
cd "phishing_detection"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train ML Model
python train_model.py

# 4. Run Automated Unit Tests
python -m unittest discover tests

# 5. Launch Web Application
python app.py
```
Open browser at **`http://127.0.0.1:5051`**.

---

## 🔒 Defensive Lab Safety Notice
- Submitted URLs are processed **strictly as passive text strings**.
- The application **does not make outbound HTTP requests**, DNS resolutions, or establish connections to target URLs.
- Zero risk of executing malicious content.

---

## 🚀 Limitations & Future Improvements
- **Future Feature Expansion**: Adding WHOIS domain age checks, SSL certificate validation, and HTML page structure analysis via headless browser.
- **Live Feed Integration**: Pulling daily threat feeds from OpenPhish / PhishTank for continuous online model re-training.
