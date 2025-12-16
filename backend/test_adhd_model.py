import os
import joblib

# Get paths
current_dir = os.path.dirname(os.path.abspath(__file__))
ml_models_path = os.path.join(current_dir, 'ml_models')

try:
    # Load models
    scaler = joblib.load(os.path.join(ml_models_path, 'scaler1.pkl'))
    model = joblib.load(os.path.join(ml_models_path, 'adhd_model1.pkl'))
    gender_encoder = joblib.load(os.path.join(ml_models_path, 'gender_encoder1.pkl'))
    
    # Sample data
    sample_data = {
        'gender': 'Male',
        'easily_distracted': 2,
        'forgetful_daily_tasks': 1,
        'poor_organization': 2,
        'difficulty_sustaining_attention': 3,
        'restlessness': 2,
        'impulsivity_score': 1,
        'screen_time_daily': 7.8,
        'phone_unlocks_per_day': 120,
        'working_memory_score': 45
    }
    
    # Encode gender
    gender_encoded = gender_encoder.transform([sample_data['gender']])[0]
    
    # Prepare all 12 features (add defaults for missing 2)
    features = [
        25,                     # age (default)
        gender_encoded,         # gender
        6.5,                    # sleep_hours_avg (default)
        sample_data['easily_distracted'],
        sample_data['forgetful_daily_tasks'],
        sample_data['poor_organization'],
        sample_data['difficulty_sustaining_attention'],
        sample_data['restlessness'],
        sample_data['impulsivity_score'],
        sample_data['screen_time_daily'],
        sample_data['phone_unlocks_per_day'],
        sample_data['working_memory_score']
    ]
    
    # Scale and predict
    features_scaled = scaler.transform([features])
    prediction = model.predict(features_scaled)
    
    # Show ONLY required output
    if prediction[0] == 1:
        print("Has ADHD")
    else:
        print("Doesn't have ADHD")
        
except Exception as e:
    print(f"Error: {e}")