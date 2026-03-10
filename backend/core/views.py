#User fills form → Browser sends POST request → views.py function runs (Validates data, saves to database, returns success/error response) → Saves to database → Returns JSON response → Browser shows success message
#It takes customer orders (requests), prepares food (processes data), and serves meals (responses).

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .adhd_prediction import predict_adhd
from .models import *
from .serializers import *

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from rest_framework.views import APIView

# -----------------------------------------------------------
# Load Gemini API Key
# -----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Debug print (masked)
print("Loaded GOOGLE_API_KEY:", "FOUND" if GOOGLE_API_KEY else "NOT FOUND")
print("ENV_PATH:", ENV_PATH)
print("File exists:", os.path.exists(ENV_PATH))

# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("WARNING: GOOGLE_API_KEY not found. Chatbot will not work.")

# -----------------------------------------------------------
# Mental Health Keywords Filter
# -----------------------------------------------------------
MENTAL_HEALTH_KEYWORDS = [
    # General mental health
    "mental health", "wellness", "well-being", "counseling", "therapy",
    "psychologist", "psychiatrist", "therapist", "counselor",
    
    # Conditions
    "depression", "depressed", "sadness", "hopeless", "worthless",
    "anxiety", "anxious", "worry", "panic", "fear", "nervous",
    "stress", "stressed", "overwhelmed", "burnout", "pressure",
    "adhd", "attention deficit", "hyperactivity", "focus", "distracted",
    "bipolar", "mood swings", "mania", "hypomania",
    "ocd", "obsessive", "compulsive", "intrusive thoughts",
    "ptsd", "trauma", "flashbacks", "nightmares",
    "eating disorder", "anorexia", "bulimia", "body image",
    "insomnia", "sleep", "tired", "exhausted", "fatigue",
    
    # Symptoms
    "lonely", "loneliness", "isolated", "alone",
    "anger", "irritable", "frustrated", "rage",
    "grief", "loss", "bereavement", "mourning",
    "guilt", "shame", "regret",
    "hopeless", "helpless", "worthless",
    "suicidal", "self-harm", "hurt myself", "end it all",
    
    # Emotions
    "happy", "sad", "angry", "scared", "confused",
    "emotional", "feelings", "mood", "feeling",
    
    # Relationships
    "relationship", "family", "friends", "social",
    "breakup", "divorce", "conflict", "argument",
    
    # Self-care
    "self-care", "mindfulness", "meditation", "relaxation",
    "breathing", "coping", "strategies", "tips",
    
    # Help
    "help", "advice", "suggestion", "recommend", "guide",
    "support", "resources", "hotline", "crisis",
    
    # Common questions
    "what is", "how to", "why do", "can you", "tell me",
    "hello", "hi", "hey", "thanks", "thank you"
]

def is_mental_health_related(text):
    """Check if message is related to mental health."""
    text = text.lower()
    return any(keyword in text for keyword in MENTAL_HEALTH_KEYWORDS)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    #First Check - User Model
    try:
        user = User.objects.get(email=email, password=password)
        return Response({
            "message": "Login successful",
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "role": "user",
            "is_admin": user.is_admin
        })
    except User.DoesNotExist:
        pass #Not a User, Check if Doctor

    #Check - Doctor Model
    try:
        doctor = Doctor.objects.get(email=email, password=password, status = 'approved')
        return Response({
            "message": "Login Successful",
            "user_id": doctor.id,
            "name": doctor.name,
            "email":doctor.email,
            "role": "doctor"
        })
    
    except Doctor.DoesNotExist:
        #Check if Doctor exists but not "approved"
        try:
            doctor = Doctor.objects.get(email = email, password = password)
            #Doctor exists but status is not 'approved'
            return Response({
                "error": "Your account is not Approved yet. Please wait for Admin Approval."
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Doctor.DoesNotExist:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] 
    authentication_classes = [SessionAuthentication]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = instance.id
            self.perform_destroy(instance)
            return Response({
                "message": f"User {user_id} deleted successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"Failed to delete user: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

class DoctorViewSet(viewsets.ModelViewSet):
    queryset =Doctor.objects.all()
    serializer_class = DoctorSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def doctor_register(request):
    serializer = DoctorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Doctor registration successful. Waiting for admin approval."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def predict_adhd_api(request):
    """
    API endpoint for ADHD prediction using trained ML model
    Expects JSON with 12 features from ADHD.docx
    """
    try:
        # Get data from request
        data = request.data
        
        # Load ML components (lazy loading to avoid loading on startup)
        import joblib
        import os
        import numpy as np
        
        # Get base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, 'core', 'ml_models', 'adhd')
        
        # Load models
        gender_encoder = joblib.load(os.path.join(models_dir, 'gender_encoder1.pkl'))
        scaler = joblib.load(os.path.join(models_dir, 'scaler1.pkl'))
        model = joblib.load(os.path.join(models_dir, 'adhd_model1.pkl'))
        
        # Validate required fields - 12 features from ADHD.docx
        required_fields = [
            'age', 'gender', 'sleep_hours_avg', 'easily_distracted',
            'forgetful_daily_tasks', 'poor_organization', 'difficulty_sustaining_attention',
            'restlessness', 'impulsivity_score', 'screen_time_daily',
            'phone_unlocks_per_day', 'working_memory_score'
        ]
                
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"Missing required field: {field}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        # Encode gender
        try:
            gender_encoded = gender_encoder.transform([data['gender']])[0]
        except ValueError:
            return Response(
                {"error": f"Invalid gender value. Use: {list(gender_encoder.classes_)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create feature array in correct order
        features = np.array([[
            float(data['age']),
            gender_encoded,
            float(data['sleep_hours_avg']),
            int(data['easily_distracted']),
            int(data['forgetful_daily_tasks']),
            int(data['poor_organization']),
            int(data['difficulty_sustaining_attention']),
            int(data['restlessness']),
            int(data['impulsivity_score']),
            float(data['screen_time_daily']),
            int(data['phone_unlocks_per_day']),
            int(data['working_memory_score'])
        ]])
        
        #Scale features
        scaled_features = scaler.transform(features)
        
        #Make Prediction
        prediction = model.predict(scaled_features)[0]
        prediction_proba = model.predict_proba(scaled_features)[0]
        
        # Prepare response
        result = {
            "prediction": int(prediction),
            "prediction_label": "ADHD" if prediction == 1 else "No ADHD",
            "confidence": float(prediction_proba[prediction]),
            "probabilities": {
                "no_adhd": float(prediction_proba[0]),
                "adhd": float(prediction_proba[1])
            },
            "features_used": {field: data[field] for field in required_fields}
        }
        
        return Response(result)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def predict_anxiety_api(request):
    '''
    API endpoint for Anxiety prediction using trained ML model
    Expects JSON with 14 features from anxiety model
    '''
    
    try:
        #Get data from request
        data = request.data

        # Load ML components
        import joblib
        import os
        import numpy as np
        
        # Get base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, 'core', 'ml_models', 'anxiety')
        
        # Load models
        label_encoder = joblib.load(os.path.join(models_dir, 'label_encoder.joblib'))
        scaler = joblib.load(os.path.join(models_dir, 'scaler.joblib'))
        model = joblib.load(os.path.join(models_dir, 'rf_model.joblib'))
        
        # 14 features from the scaler
        required_fields = [
            'Sadness', 'Euphoric', 'Exhausted', 'Sleep dissorder', 'Mood Swing',
            'Suicidal thoughts', 'Anorxia', 'Authority Respect', 'Try-Explanation',
            'Aggressive Response', 'Ignore & Move-On', 'Nervous Break-down',
            'Admit Mistakes', 'Overthinking'
        ]
        
        # Check all required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {missing_fields}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create feature array in correct order
        features = []
        for field in required_fields:
            try:
                # Convert to float
                features.append(float(data[field]))
            except (ValueError, TypeError):
                return Response(
                    {"error": f"Field '{field}' must be a number"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        features_array = np.array([features])
        
        # Scale features
        scaled_features = scaler.transform(features_array)
        
        # Make prediction
        prediction_encoded = model.predict(scaled_features)[0]
        
        # Define anxiety levels based on model output
        anxiety_levels = {
            0: "NO (No Anxiety)",
            1: "YES (Has Anxiety)", 
            2: "Bipolar Type 1",
            3: "Bipolar Type 2"
        }
        
        # Get prediction label
        prediction_label = anxiety_levels.get(prediction_encoded, f"Level_{prediction_encoded}")
        

        # Also get the simple YES/NO from encoder if available
        simple_label = "NO"
        
        if prediction_encoded < len(label_encoder.classes_):
            simple_label = label_encoder.inverse_transform([prediction_encoded])[0]
        
        # Get prediction probabilities
        prediction_proba = model.predict_proba(scaled_features)[0]
        
        # Prepare probabilities dictionary
        probabilities = {}
        for i, prob in enumerate(prediction_proba):
            if i < len(label_encoder.classes_):
                label = label_encoder.inverse_transform([i])[0]
            else:
                label = f"Level_{i}"
            probabilities[label] = float(prob)
        
        # Preparing response
        result = {
            "prediction_encoded": int(prediction_encoded),
            "prediction_label": prediction_label,
            "simple_label": simple_label,
            "confidence": float(prediction_proba[prediction_encoded]),
            "probabilities": probabilities,
            "features_used": {field: data[field] for field in required_fields},
            "anxiety_scale": anxiety_levels
        }
        
        return Response(result)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
       
@api_view(['GET', 'PUT', 'DELETE'])
def book_detail_api(request, book_id):
    """
    API to update or delete a book
    PUT: Update book
    DELETE: Delete book
    """
    try:
        book = Book.objects.get(id=book_id)

        if request.method == 'GET':
            serializer = BookSerializer(book)
            return Response(serializer.data)
        
        if request.method == 'PUT':
            serializer = BookSerializer(book, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Book updated successfully",
                    "book": serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            book.delete()
            return Response({
                "message": f"Book '{book.title}' deleted successfully"
            })
            
    except Book.DoesNotExist:
        return Response(
            {"error": f"Book with ID {book_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
    
@api_view(['GET'])
def get_books_api(request):
    """
    API for users to view books
    Can filter by category: ?category=adhd
    """
    try:
        category = request.GET.get('category')
        
        if category:
            books = Book.objects.filter(category=category, is_active=True)
        else:
            books = Book.objects.filter(is_active=True)
        
        serializer = BookSerializer(books, many=True)
        return Response({
            "count": len(books),
            "books": serializer.data
        })
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_book_detail_api(request, book_id):
    """
    API for users to view a single book
    """
    try:
        book = Book.objects.get(id=book_id, is_active=True)
        serializer = BookSerializer(book)
        return Response(serializer.data)
        
    except Book.DoesNotExist:
        return Response(
            {"error": f"Book with ID {book_id} not found or not active"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
def update_doctor_availability(request, doctor_id):
    #Update Doctor's availability status
    #Expects {"available": true/false}

    try:
        #Get Doctor
        doctor = Doctor.objects.get(id=doctor_id)

        #Get new availablity value
        available = request.data.get('available')

        if available is None:
            return Response(
                {"error": "Missing 'available' field in request"},
                status = status.HTTP_400_BAD_REQUEST
            )

        #update availability
        doctor.available = available
        doctor.save()

        return Response(
            {
                "message": f"Doctor {doctor.name} availability updated",
                "doctor_id": doctor.id,
                "name": doctor.name,
                "available": doctor.available
            }
        )
    
    except Doctor.DoesNotExist:
        return Response(
            {"error": f"Doctor with ID {doctor_id} not found"},
            status = status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status = status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST', 'GET'])
def doctor_time_slots_api(request, doctor_id=None):
    # API for doctors to manage time doctor_time_slots_api
    # POST: create new time slot
    # GET: get doctor's time slots(filter by date if provided)
    try:
        if request.method == 'POST':
            #Create new time slot
            doctor = Doctor.objects.get(id=doctor_id)

            #Validate required fields
            required_fields = ['date', 'slots']
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {"error":f"Missing required field: {field}"},
                        status = status.HTTP_400_BAD_REQUEST
                    )
            
            # Validate slots array
            if 'slots' not in request.data or not isinstance(request.data['slots'], list):
                return Response(
                    {"error": "Please provide 'slots' as an array of times (e.g., ['9.00', '10.00', '11.00'])"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create slot_data JSON with slots array
            slot_data = {
                "slots": request.data['slots']
            }

            #Create time slot
            time_slot = TimeSlot.objects.create(
                doctor=doctor,
                date=request.data['date'],
                slot_data=slot_data,
                is_booked=False
            )

            serializer = TimeSlotSerializer(time_slot)
            return Response({
                "message": "Time slot created Successfully",
                "time_slot": serializer.data
            }, status= status.HTTP_201_CREATED)
        
        elif request.method == 'GET':
            #Get doctor's time slots
            doctor = Doctor.objects.get(id=doctor_id)
            date = request.GET.get('date')

            if date:
                time_slots = TimeSlot.objects.filter(doctor=doctor, date=date)
            else:
                time_slots = TimeSlot.objects.filter(doctor=doctor)

            serializer = TimeSlotSerializer(time_slots, many= True)
            return Response({
                "count": len(time_slots),
                "time_slots": serializer.data
            })
    
    except Doctor.DoesNotExist:
        return Response(
            {"error": f"Doctor with ID {doctor_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['PUT', 'DELETE'])
def time_slot_detail_api(request, time_slot_id):
    # API to update or delete a time slot
    # PUT: Update time slot(e.g., mark as booked)
    # DELETE: delete time slot 

    try:
        time_slot = TimeSlot.objects.get(id=time_slot_id)

        if request.method == 'PUT':
            #Update time slot
            serializer=TimeSlotSerializer(time_slot, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Time slot updated successfully",
                    "time_slot": serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            time_slot.delete()
            return Response({
                "message": "Time slot deleted successfully"
            })
        
    except TimeSlot.DoesNotExist:
        return Response(
            {"error":f"Time slot with ID {time_slot_id} not found"},
            status=status.HTTP_400_NOT_FOUND
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def find_nearby_doctors_api(request):
    #Find Doctors in the same location as User
    #Query params: place (or get from user profile)

    try:
        #Get place from query params or user profile
        place = request.GET.get('place')

        if not place:
            return Response(
                {"error": "Please provide 'place' parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        #Find doctors in same place who are approved and available
        doctors= Doctor.objects.filter(
            place__iexact = place,
            status='approved',
            available= True
        )

        serializer = DoctorSerializer(doctors, many=True)
        return Response({
            "place": place,
            "count": len(doctors),
            "doctors": serializer.data
        })
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status = status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def find_nearby_doctors_by_user_api(request, user_id):
    """
    API to find doctors near a user based on user's place
    Uses user_id to get user's place, then finds doctors in same location
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        if not user.place:
            return Response(
                {"error": "User doesn't have a place/location set in profile"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find doctors in same place who are approved and available
        doctors = Doctor.objects.filter(
            place__iexact=user.place,
            status='approved',
            available=True
        )
        
        serializer = DoctorSerializer(doctors, many=True)
        
        return Response({
            "user_id": user.id,
            "user_name": user.name,
            "user_place": user.place,
            "count": len(doctors),
            "doctors": serializer.data
        })
        
    except User.DoesNotExist:
        return Response(
            {"error": f"User with ID {user_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['POST', 'GET'])
def doctor_feedback_api(request, doctor_id=None):
    """
    API for doctor feedback/reviews
    POST: User submits feedback for doctor
    GET: Get all feedback for a doctor
    """
    try:
        if request.method == 'POST':
            # User submits feedback
            doctor = Doctor.objects.get(id=doctor_id)
            user_id = request.data.get('user_id')
            
            if not user_id:
                return Response(
                    {"error": "User ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = User.objects.get(id=user_id)
            
            # Check if user already gave feedback to this doctor
            existing_feedback = DoctorFeedback.objects.filter(doctor=doctor, user=user).first()
            if existing_feedback:
                return Response(
                    {"error": "You have already submitted feedback for this doctor"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create feedback
            serializer = DoctorFeedbackSerializer(data=request.data)
            if serializer.is_valid():
                # Set doctor and user (not from request data)
                feedback = serializer.save(doctor=doctor, user=user)
                return Response({
                    "message": "Feedback submitted successfully",
                    "feedback": DoctorFeedbackSerializer(feedback).data
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'GET':
            # Get all feedback for doctor
            doctor = Doctor.objects.get(id=doctor_id)
            feedbacks = DoctorFeedback.objects.filter(doctor=doctor).order_by('-created_at')
            
            # Calculate average rating
            total_rating = sum(f.rating for f in feedbacks)
            average_rating = total_rating / len(feedbacks) if feedbacks else 0
            
            serializer = DoctorFeedbackSerializer(feedbacks, many=True)
            return Response({
                "doctor_id": doctor.id,
                "doctor_name": doctor.name,
                "average_rating": round(average_rating, 1),
                "total_feedbacks": len(feedbacks),
                "feedbacks": serializer.data
            })
            
    except Doctor.DoesNotExist:
        return Response(
            {"error": f"Doctor with ID {doctor_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except User.DoesNotExist:
        return Response(
            {"error": f"User with ID {request.data.get('user_id')} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )   

@api_view(['POST', 'GET'])
def booking_api(request, user_id = None, doctor_id = None): 
    # API for booking appointmetns
    # POST - Create new Booking (user books time slot)
    # GET - Get bookings (user's or doctor's depending on parameters) 

    try:
        if request.method == 'POST':
            #User creates booking
            user = User.objects.get(id=user_id)
            time_slot_id = request.data.get('time_slot_id')
            booked_time = request.data.get('booked_time')
            symptoms = request.data.get('symptoms', '')
            notes = request.data.get('notes', '')

            if not time_slot_id:
                return Response(
                    {"error": "Time slot ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            time_slot = TimeSlot.objects.get(id=time_slot_id)

            if not booked_time:
                return Response(
                    {"error": "Please specify which time slot to book (e.g., '10.00')"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the requested time is available in the time slot's slots
            available_slots = time_slot.slot_data.get('slots', [])
            if booked_time not in available_slots:
                return Response(
                    {"error": f"Time {booked_time} is not available. Available slots: {available_slots}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #To check if time slot is already booked
            if time_slot.is_booked:
                return Response(
                    {"error": "This time slot is already booked"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Doctor ID is required
            requested_doctor_id = request.data.get('doctor_id')
            if not requested_doctor_id:
                return Response(
                    {"error": "Doctor ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if Time slot belongs to requested Doctor
            if int(requested_doctor_id) != time_slot.doctor.id:
                return Response(
                    {"error": "Time slot does not belong to the specified doctor"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            #To Create booking
            booking = Booking.objects.create(
                user=user,
                doctor=time_slot.doctor,
                time_slot=time_slot,
                booked_time= booked_time,
                symptoms= symptoms,
                notes=notes,
                status='pending'
            )

            #To mark time slot as booked
            time_slot.is_booked = True
            time_slot.save()

            serializer = BookingSerializer(booking)
            return Response({
                "message": "Booking created successfully",
                "booking": serializer.data
            },status=status.HTTP_201_CREATED)

        
        elif request.method == 'GET':
            if user_id:
                #To GET user's bookings
                user = User.objects.get(id=user_id)
                bookings = Booking.objects.filter(user=user).order_by('-created_at')
                serializer = BookingSerializer(bookings, many=True)
                return Response({
                    "user_id":user.id,
                    "user_name": user.name,
                    "total_bookings": len(bookings),
                    "bookings": serializer.data
                })
            
            elif doctor_id:
                #To GET doctor's bookings
                doctor = Doctor.objects.get(id=doctor_id)
                bookings = Booking.objects.filter(doctor=doctor).order_by('-created_at')
                serializer = BookingSerializer(bookings, many = True)
                return Response({
                    "doctor_id": doctor.id,
                    "doctor_name": doctor.name,
                    "total_bookings": len(bookings),
                    "bookings": serializer.data
                })
            
            else:
                return Response(
                    {"error": "Please provide either user_id or doctor_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
    except User.DoesNotExist:
        return Response(
            {"error": f"User with ID {user_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Doctor.DoesNotExist:
        return Response(
            {"error": f"Doctor with ID {doctor_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except TimeSlot.DoesNotExist:
        return Response(
            {"error": f"Time Slot with ID {request.data.get('time_slot_id')} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
def update_booking_status_api(request, booking_id):
    #API to update booking status (doctor confirms/cancels)

    try:
        booking = Booking.objects.get(id=booking_id)
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {"error": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in ['confirmed', 'cancelled', 'completed']:
            return Response(
                {"error": "Invalid status. Use: confirmed, cancelled or completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        #To Update Status
        booking.status = new_status
        booking.save()

        #If cancelled, free up the time slot
        if new_status == 'cancelled':
            booking.time_slot.is_booked = False
            booking.time_slot.save()

        serializer = BookingSerializer(booking)
        return Response ({
            "message": f"Booking status updated to '{new_status}'",
            "booking": serializer.data
        })
    
    except Booking.DoesNotExist:
        return Response(
            {"error": f"Booking with ID {booking_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def add_book_api(request):
    """
    API to add a new book
    Only accessible to admin
    Accepts multipart/form-data for file uploads
    """
    try:
        from .serializers import BookSerializer
        
        # Handle file uploads - request.FILES contains uploaded files
        data = request.data.copy()
        
        # Convert checkbox value to boolean
        if 'is_active' in data:
            data['is_active'] = data['is_active'] in ['true', 'on', True, 'True', 1, '1']
        
        serializer = BookSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Book added successfully",
                "book": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MoodLogViewSet(viewsets.ModelViewSet):
    queryset = MoodLog.objects.all()
    serializer_class = MoodLogSerializer

@api_view(['POST'])
def save_assessment_result(request):
    """
    API to save assessment result after ADHD/Anxiety prediction
    """
    try:
        print("="*50)
        print("SAVE ASSESSMENT REQUEST RECEIVED")
        print("Request data:", request.data)
        
        user_id = request.data.get('user_id')
        if not user_id:
            print("ERROR: No user_id provided")
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"User ID: {user_id}")
        user = User.objects.get(id=user_id)
        print(f"User found: {user.name}")
        
        # Create assessment result
        data = {
            'user': user.id,
            'assessment_type': request.data.get('assessment_type'),
            'result': request.data.get('result'),
            'confidence': request.data.get('confidence'),
            'details': request.data.get('details', {})
        }
        print("Data to save:", data)
        
        serializer = AssessmentResultSerializer(data=data)
        if serializer.is_valid():
            print("Serializer is valid")
            serializer.save()
            print("Assessment saved successfully")
            return Response({
                "message": "Assessment result saved successfully",
                "assessment": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except User.DoesNotExist:
        print(f"ERROR: User with ID {user_id} not found")
        return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_user_assessments_api(request, user_id):
    """
    API to get all assessments for a user
    """
    try:
        user = User.objects.get(id=user_id)
        assessments = AssessmentResult.objects.filter(user=user).order_by('-created_at')
        serializer = AssessmentResultSerializer(assessments, many=True)
        return Response({
            "user_id": user.id,
            "user_name": user.name,
            "count": len(assessments),
            "assessments": serializer.data
        })
    except User.DoesNotExist:
        return Response({"error": f"User with ID {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'DELETE'])
def assessment_detail_api(request, assessment_id):
    """
    API to get or delete a specific assessment
    """
    try:
        assessment = AssessmentResult.objects.get(id=assessment_id)
        
        if request.method == 'GET':
            serializer = AssessmentResultSerializer(assessment)
            return Response(serializer.data)
            
        elif request.method == 'DELETE':
            assessment.delete()
            return Response({"message": "Assessment deleted successfully"})
            
    except AssessmentResult.DoesNotExist:
        return Response({"error": f"Assessment with ID {assessment_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------------------------------------------
# Mental Health Chatbot API
# -----------------------------------------------------------

class MentalHealthChatAPIView(APIView):
    """
    API endpoint for mental health chatbot using Gemini
    """
    
    def post(self, request):
        user_message = request.data.get("message")
        
        if not user_message:
            return Response({"error": "Message is required"}, status=400)
        
        # Check if API key is configured
        if not GOOGLE_API_KEY:
            return Response({
                "error": "Chatbot service not configured"
            }, status=500)
        
        # Filter unrelated topics
        if not is_mental_health_related(user_message):
            return Response({
                "reply": "I'm a mental health assistant and can only answer questions related to mental wellness, emotions, psychological conditions, and self-care. How can I support your mental health today?"
            })
        
        try:
            prompt = f"""
            You are SereneBot, a compassionate mental health assistant. You provide supportive, 
            empathetic, and helpful responses about mental wellness, emotions, psychological conditions,
            and self-care strategies. You are not a replacement for professional medical help.

            Important guidelines:
            - Be empathetic and non-judgmental
            - Provide practical coping strategies when appropriate
            - If someone mentions self-harm or suicidal thoughts, encourage them to seek immediate professional help
            - Suggest resources like therapists, hotlines, or support groups
            - Keep responses concise and helpful (under 150 words)
            - Only answer questions related to mental health and wellness

            User: {user_message}
            
            SereneBot:"""
            
            # Use Gemini model
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            
            return Response({"reply": response.text})
            
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return Response({
                "error": f"Chatbot service error: {str(e)}"
            }, status=500)


# Simple test endpoint
class ChatbotTestAPIView(APIView):
    """
    Simple test endpoint to verify chatbot is working
    """
    
    def get(self, request):
        return Response({
            "message": "Chatbot API is working. Send a POST request with {'message': 'your question'}"
        })