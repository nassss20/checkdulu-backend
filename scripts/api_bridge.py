import sys
import json
import warnings
import os
import re
from urllib.parse import urlparse
import joblib
import pandas as pd

warnings.filterwarnings("ignore")

def extract_proven_features(raw_url):
    """
    Replicates the exact feature extraction logic from the original dataset prep
    to guarantee 100% mathematical alignment with the trained model.
    """
    url = raw_url
    parsed = urlparse(url)
    if not parsed.scheme:
        url = 'http://' + url
        parsed = urlparse(url)
        
    domain = parsed.netloc
    url_lower = url.lower()
    domain_lower = domain.lower()

    letters = sum(c.isalpha() for c in url)
    digits = sum(c.isdigit() for c in url)
    special_chars = len(url) - letters - digits
    
    # Identify the Top Level Domain (TLD)
    tld = domain_lower.split('.')[-1] if '.' in domain_lower else ''
    suspicious_tlds = ['cc', 'app', 'xyz', 'top', 'lol', 'shop', 'online', 'site', 'vip', 'ru', 'tk', 'ml']

    heuristics = {
        # --- ORIGINAL 14 ML FEATURES ---
        'URLLength': len(url),
        'DomainLength': len(domain),
        'IsDomainIP': 1 if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain) else 0,
        'NoOfSubDomain': max(0, len(domain.split('.')) - 2),
        'NoOfLettersInURL': letters,
        'LetterRatioInURL': round(letters / len(url), 3) if len(url) > 0 else 0,
        'NoOfDegitsInURL': digits,
        'DegitRatioInURL': round(digits / len(url), 3) if len(url) > 0 else 0,
        'NoOfEqualsInURL': url.count('='),
        'NoOfQMarkInURL': url.count('?'),
        'NoOfAmpersandInURL': url.count('&'),
        'NoOfOtherSpecialCharsInURL': special_chars,
        'SpacialCharRatioInURL': round(special_chars / len(url), 3) if len(url) > 0 else 0,
        'IsHTTPS': 1 if parsed.scheme == 'https' else 0,
        
        # --- NEW 18 ML FEATURES ---
        'NoOfHyphensInDomain': domain_lower.count('-'),
        'Bank': 1 if 'bank' in url_lower else 0,
        'Pay': 1 if any(keyword in url_lower for keyword in ['pay', 'payment', 'paypal']) else 0,
        'Crypto': 1 if any(keyword in url_lower for keyword in ['crypto', 'wallet', 'coin']) else 0,
        
        # --- EXTRA STAGE-1 ONLY FEATURES (Ignored by ML) ---
        'SuspiciousTLD': 1 if tld in suspicious_tlds else 0,
        'BrandSpoof': 1 if any(b in url_lower for b in ['steam', 'microsoft', 'google', 'apple', 'netflix', 'facebook', 'instagram', 'amazon']) else 0,
        'AuthSpoof': 1 if any(w in url_lower for w in ['login', 'verify', 'auth', 'secure', 'account', 'update', 'support']) else 0,
    }
    return heuristics

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No URL provided to the AI Engine."}))
        sys.exit(1)
        
    target_url = sys.argv[1]
    
    try:
        features = extract_proven_features(target_url)
        
        stage_1_score = 0
        
        # 1. Missing HTTPS
        if features['IsHTTPS'] == 0:
            stage_1_score += 40
            
        # 2. High Special Characters
        if features['NoOfOtherSpecialCharsInURL'] > 5:
            stage_1_score += 15
            
        # 3. Excessive Subdomains
        if features['NoOfSubDomain'] > 2:
            stage_1_score += 10
            
        # 4. Long URL Length
        if features['URLLength'] > 75:
            stage_1_score += 10
            
        # 5. IP Address Override
        if features['IsDomainIP'] == 1:
            stage_1_score += 25 
            
        # 6. Financial Keyword Spoofing 
        if features['Bank'] == 1 or features['Pay'] == 1 or features['Crypto'] == 1:
            stage_1_score += 20
            
        # 7. Domain Hyphen Obfuscation 
        if features['NoOfHyphensInDomain'] >= 1:
            stage_1_score += 15
            
        # 8. Suspicious TLD Override (NEW)
        # Hits domains like .cc, .app, .xyz which are heavily abused by phishers
        if features.get('SuspiciousTLD', 0) == 1:
            stage_1_score += 25
            
        # 9. Brand & Auth Spoofing (NEW)
        # Hits URLs attempting to fake tech brands or login portals
        if features.get('BrandSpoof', 0) == 1 or features.get('AuthSpoof', 0) == 1:
            stage_1_score += 25

        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "..", "storage", "app", "url_phishing_rf_model.joblib")
        
        try:
            model = joblib.load(model_path)
        except FileNotFoundError:
            print(json.dumps({"error": f"AI Model (.joblib) not found at: {model_path}"}))
            sys.exit(1)
            
        # Strictly define the original 18 features so the ML model doesn't crash 
        # when we pass the expanded Stage 1 dictionary.
        feature_order = [
            'URLLength', 'DomainLength', 'IsDomainIP', 'NoOfSubDomain', 
            'NoOfLettersInURL', 'LetterRatioInURL', 'NoOfDegitsInURL', 
            'DegitRatioInURL', 'NoOfEqualsInURL', 'NoOfQMarkInURL', 
            'NoOfAmpersandInURL', 'NoOfOtherSpecialCharsInURL', 
            'SpacialCharRatioInURL', 'IsHTTPS',
            'NoOfHyphensInDomain', 'Bank', 'Pay', 'Crypto'
        ]
        
        df_features = pd.DataFrame([features])
        df_features = df_features[feature_order]
        
        ai_prediction = model.predict(df_features)[0]
        
        if stage_1_score >= 50 and ai_prediction == 1:
            final_verdict = "PHISHING"
            reason = "Both the Security Rules and the AI Detective flagged this link as highly dangerous."
        elif stage_1_score >= 50 and ai_prediction == 0:
            final_verdict = "PHISHING"
            reason = "The Security Rules caught obvious threat indicators (like keyword spoofing or suspicious TLDs)" \
            "that bypassed the AI."
        elif stage_1_score < 50 and ai_prediction == 1:
            final_verdict = "PHISHING"
            reason = "The AI Detective found hidden malicious patterns that looked normal on the surface."
        else:
            final_verdict = "SAFE"
            reason = "Both the Security Rules and the AI verified this link as safe to visit."
            
        output = {
            "url": target_url,
            "verdict": final_verdict,
            "reason": reason,
            "stage_1_score": stage_1_score,
            "heuristics_extracted": features
        }
        
        print(json.dumps(output))
        
    except Exception as e:
        print(json.dumps({"error": f"CheckDulu Engine Error: {str(e)}"}))

if __name__ == "__main__":
    main()