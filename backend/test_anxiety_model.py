import joblib
import numpy as np
import os

#Load the models
models_dir = "E:\\serene_space\\backend\\core\\ml_models\\anxiety"

label_encoder = joblib.load(os.path.join(models_dir, 'label_encoder.joblib'))
scaler = joblib.load(os.path.join(models_dir, 'scaler.joblib'))
model = joblib.load(os.path.join(models_dir, 'rf_model.joblib'))

print("Label Encoder Classes: ", label_encoder.classes_)
print("\nScaler Feature names(if any): ", getattr(scaler, 'feature_names_in_', 'Not available'))

if hasattr(model, 'feature_names_in_'):
    print("Model feature names:", model.feature_names_in_)

print("\nModel type:", type(model))
print("Model has predict_proba:", hasattr(model, 'predict_proba'))

#Try to get feature names from anxiety.docx or check the example
print("\nFrom anxiety.docx, symptoms mentioned:")
symptoms = [
    "Sadness", "Euphoric", "Exhausted", "Sleep Disorder", "Mood Swings",
    "Suicidal thoughts", "Anorexia", "Authority Respect", "Try-Explanation",
    "Aggressive Response", "Ignore & Move-on", "Nervous Break-down",
    "Admit Mistakes", "Overthinking"
]

print("Total Symptoms: ", len(symptoms))
for i, symptom in enumerate(symptoms):
    print(f"{i+1}. {symptom}")