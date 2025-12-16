import os
import joblib
import sys

# Add Django project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def predict_adhd(user_data):
    """
    Predict ADHD based on user data.
    user_data should contain 10 features from mentor's document.
    Returns: "Has ADHD" or "Doesn't have ADHD"
    """
    try:
        # Get base directory (backend folder)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ml_models_path = os.path.join(base_dir, 'ml_models')
        
        # Load models
        scaler = joblib.load(os.path.join(ml_models_path, 'scaler1.pkl'))
        model = joblib.load(os.path.join(ml_models_path, 'adhd_model1.pkl'))
        gender_encoder = joblib.load(os.path.join(ml_models_path, 'gender_encoder1.pkl'))
        
        # Encode gender
        gender_encoded = gender_encoder.transform([user_data['gender']])[0]
        
        # Prepare all 12 features (add defaults for age and sleep_hours_avg)
        features = [
            user_data.get('age', 25),                     # age (default 25 if not provided)
            gender_encoded,                               # gender encoded
            user_data.get('sleep_hours_avg', 6.5),        # sleep_hours_avg (default 6.5)
            user_data['easily_distracted'],
            user_data['forgetful_daily_tasks'],
            user_data['poor_organization'],
            user_data['difficulty_sustaining_attention'],
            user_data['restlessness'],
            user_data['impulsivity_score'],
            user_data['screen_time_daily'],
            user_data['phone_unlocks_per_day'],
            user_data['working_memory_score']
        ]
        
        # Scale and predict
        features_scaled = scaler.transform([features])
        prediction = model.predict(features_scaled)
        
        # Return result
        if prediction[0] == 1:
            return "Has ADHD"
        else:
            return "Doesn't have ADHD"
            
    except Exception as e:
        return f"Error: {str(e)}"


# Test function
if __name__ == "__main__":
    # Test with sample data
    test_data = {
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
    
    result = predict_adhd(test_data)
    print(f"Test prediction: {result}")