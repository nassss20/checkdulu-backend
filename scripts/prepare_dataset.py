import pandas as pd
import re
from urllib.parse import urlparse
import os

# Dynamically find the Laravel root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, 'storage', 'app')

# Input is your raw, massive dataset
INPUT_CSV = os.path.join(STORAGE_DIR, 'Phishing_URL_Dataset.csv') 
# Output is your clean, balanced, 18-feature dataset
OUTPUT_CSV = os.path.join(STORAGE_DIR, 'urls_v2.csv')

def extract_static_features(url):
    """
    Extracts the 18 structural and lexical features from a URL.
    Includes deliberate typos (Degit, Spacial) to ensure dataset compatibility.
    """
    url = str(url)
    parsed = urlparse(url if "://" in url else "http://" + url)
    domain = parsed.netloc
    
    url_lower = url.lower()
    domain_lower = domain.lower()

    # Calculate raw character types
    letters = sum(c.isalpha() for c in url)
    digits = sum(c.isdigit() for c in url)
    special_chars = len(url) - letters - digits

    return {
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
        
        # --- NEW LEXICAL HEURISTICS ---
        'NoOfHyphensInDomain': domain_lower.count('-'),
        'Bank': 1 if 'bank' in url_lower else 0,
        'Pay': 1 if any(keyword in url_lower for keyword in ['pay', 'payment', 'paypal']) else 0,
        'Crypto': 1 if any(keyword in url_lower for keyword in ['crypto', 'wallet', 'coin']) else 0,
    }

def prepare_data():
    print("=============================================")
    print(" CHECKDULU: DATA CLEANING & PREPROCESSING    ")
    print("=============================================\n")
    
    print(f"Loading raw dataset: {INPUT_CSV}...")
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"ERROR: Could not find raw dataset at {INPUT_CSV}")
        print("Please make sure Phishing_URL_Dataset.csv is in the storage/app/ folder.")
        return

    print(f"Original dataset size: {len(df):,} rows")

    # --- STEP 1: DATA CLEANING ---
    print("\n[1/3] Cleaning Data (Removing errors and duplicates)...")
    df = df.dropna(subset=['URL', 'label'])
    df = df.drop_duplicates(subset=['URL'])
    print(f"Size after removing duplicates and errors: {len(df):,} rows")

    # --- STEP 2: CLASS BALANCING ---
    print("\n[2/3] Balancing Classes (Ensuring a fair test for the AI)...")
    safe_count = len(df[df['label'] == 0])
    phishing_count = len(df[df['label'] == 1])
    print(f"Current Balance -> Safe: {safe_count:,}, Phishing: {phishing_count:,}")
    
    minimum_class_size = min(safe_count, phishing_count)
    safe_df = df[df['label'] == 0].sample(n=minimum_class_size, random_state=42)
    phish_df = df[df['label'] == 1].sample(n=minimum_class_size, random_state=42)
    balanced_df = pd.concat([safe_df, phish_df]).sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"New Perfect Balance -> Safe: {minimum_class_size:,}, Phishing: {minimum_class_size:,}")

    # --- STEP 3: FEATURE EXTRACTION ---
    print(f"\n[3/3] Extracting 18 static features for {len(balanced_df):,} URLs...")
    print("(This might take a minute depending on your computer's speed...)")
    
    extracted_df = balanced_df['URL'].apply(lambda x: pd.Series(extract_static_features(x)))
    extracted_df['target'] = balanced_df['label']
    
    extracted_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSUCCESS! Cleaned, balanced, and extracted dataset saved to:")
    print(f"-> {OUTPUT_CSV}")
    print("\nYou are now ready to run 'python scripts/train_url_model.py'!")

if __name__ == "__main__":
    prepare_data()