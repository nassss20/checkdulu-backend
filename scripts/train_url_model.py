import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import warnings

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, 'storage', 'app')

def train_phishing_model():
    csv_path = os.path.join(STORAGE_DIR, 'urls_v2.csv')
    model_path = os.path.join(STORAGE_DIR, 'url_phishing_rf_model.joblib')
    
    print(f"Loading {csv_path}...")
    df_urls = pd.read_csv(csv_path)
    
    features = [
        'URLLength', 'DomainLength', 'IsDomainIP', 'NoOfSubDomain', 
        'NoOfLettersInURL', 'LetterRatioInURL', 'NoOfDegitsInURL', 
        'DegitRatioInURL', 'NoOfEqualsInURL', 'NoOfQMarkInURL', 
        'NoOfAmpersandInURL', 'NoOfOtherSpecialCharsInURL', 
        'SpacialCharRatioInURL', 'IsHTTPS',
        'NoOfHyphensInDomain', 'Bank', 'Pay', 'Crypto'  # The 4 new features!
    ]
    
    X = df_urls[features].fillna(0)
    y = df_urls['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    rf = RandomForestClassifier(n_estimators=100, max_features='sqrt', random_state=42)
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    print("\n--- PHISHING MODEL SCORES ---")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Safe', 'Phishing']))
    
    joblib.dump(rf, model_path)
    print(f"\nSuccess: Saved {model_path}\n")

if __name__ == "__main__":
    train_phishing_model()