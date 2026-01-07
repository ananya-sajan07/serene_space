import joblib
import os
import numpy as np

def inspect_pkl(filepath):
    print(f"\n=== Inspecting: {os.path.basename(filepath)} ===")
    try:
        obj = joblib.load(filepath)
        print(f"Type: {type(obj)}")
        
        if hasattr(obj, '__dict__'):
            print("Attributes:", list(obj.__dict__.keys())[:10])
        
        # For scikit-learn objects
        if hasattr(obj, 'feature_names_in_'):
            print(f"Feature names: {obj.feature_names_in_}")
        
        if hasattr(obj, 'classes_'):
            print(f"Classes: {obj.classes_}")
            
        if hasattr(obj, 'scale_'):
            print(f"Scale: {obj.scale_[:5]}...")
            
        if hasattr(obj, 'n_features_in_'):
            print(f"Number of features: {obj.n_features_in_}")
            
        # Show first few items for arrays/lists
        if isinstance(obj, (list, tuple)):
            print(f"Length: {len(obj)}")
            print(f"First 5 items: {obj[:5]}")
            
        elif isinstance(obj, dict):
            print(f"Keys: {list(obj.keys())}")
            
    except Exception as e:
        print(f"Error loading: {e}")

# Test both models
models_dir = "E:\\serene_space\\backend\\core\\ml_models"

# ADHD models
print("=== ADHD MODELS ===")
inspect_pkl(os.path.join(models_dir, "adhd", "gender_encoder1.pkl"))
inspect_pkl(os.path.join(models_dir, "adhd", "scaler1.pkl"))
inspect_pkl(os.path.join(models_dir, "adhd", "adhd_model1.pkl"))

print("\n=== ANXIETY MODELS ===")
inspect_pkl(os.path.join(models_dir, "anxiety", "label_encoder.joblib"))
inspect_pkl(os.path.join(models_dir, "anxiety", "scaler.joblib"))
inspect_pkl(os.path.join(models_dir, "anxiety", "rf_model.joblib"))

print("\n\nCHECKING ANXIETY MODEL MORE CAREFULLY")
models_dir = "E:\\serene_space\\backend\\core\\ml_models\\anxiety"

model = joblib.load(os.path.join(models_dir, 'rf_model.joblib'))
label_encoder = joblib.load(os.path.join(models_dir, 'label_encoder.joblib'))

print("Model classes:", model.classes_)
print("Label encoder classes:", label_encoder.classes_)
print("Number of model classes:", len(model.classes_))
print("Number of encoder classes:", len(label_encoder.classes_))

# Test with sample data
sample_data = np.array([[3.0, 2.0, 5.0, 1.0, 2.0, 1.0, 1.0, 2.0, 3.0, 2.0, 1.0, 1.0, 2.0, 3.0]])

scaler = joblib.load(os.path.join(models_dir, 'scaler.joblib'))
scaled = scaler.transform(sample_data)

prediction = model.predict(scaled)[0]
print(f"\nSample prediction (encoded): {prediction}")

try:
    prediction_label = label_encoder.inverse_transform([prediction])[0]
    print(f"Sample prediction (decoded): {prediction_label}")
except Exception as e:
    print(f"Cannot decode: {e}")