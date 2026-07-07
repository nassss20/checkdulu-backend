import joblib
import os
import pandas as pd

print("=============================================")
print(" CHECKDULU: EXTRACTING AI FEATURE IMPORTANCE ")
print("=============================================\n")

script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "..", "storage", "app", "url_phishing_rf_model.joblib")

try:
    model = joblib.load(model_path)
    print("Success! AI Model loaded.\n")
except FileNotFoundError:
    print(f"ERROR: Could not find model at {model_path}")
    exit()

feature_order = [
    'URLLength', 'DomainLength', 'IsDomainIP', 'NoOfSubDomain', 
    'NoOfLettersInURL', 'LetterRatioInURL', 'NoOfDegitsInURL', 
    'DegitRatioInURL', 'NoOfEqualsInURL', 'NoOfQMarkInURL', 
    'NoOfAmpersandInURL', 'NoOfOtherSpecialCharsInURL', 
    'SpacialCharRatioInURL', 'IsHTTPS',
    'NoOfHyphensInDomain', 'Bank', 'Pay', 'Crypto'
]

importances = model.feature_importances_
feature_weights = pd.DataFrame({
    'Feature': feature_order,
    'Importance (%)': importances * 100
})

feature_weights = feature_weights.sort_values(by='Importance (%)', ascending=False)

print("--- HOW THE AI WEIGHS EACH FEATURE ---")
for index, row in feature_weights.iterrows():
    print(f"{row['Feature']:<30} : {row['Importance (%)']:.2f}%")

print("\n(Use these top percentages to mathematically justify your Stage 1 rule scores in your thesis!)")