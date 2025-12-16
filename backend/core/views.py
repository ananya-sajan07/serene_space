from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .adhd_prediction import predict_adhd
from .models import User, Doctor, MoodLog
from .serializers import UserSerializer, DoctorSerializer, MoodLogSerializer


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
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

class DoctorViewSet(viewsets.ModelViewSet):
    queryset =Doctor.objects.all()
    serializer_class = DoctorSerializer

@api_view(['POST'])
def doctor_register(request):
    serializer = DoctorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Doctor registration successful. Waiting for admin approval."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def predict_adhd_api(request):
    """
    API endpoint for ADHD prediction
    Expects JSON with 10 features from mentor's document
    """
    try:
        # Get data from request
        data = request.data
        
        # Validate required fields
        required_fields = [
            'gender', 'easily_distracted', 'forgetful_daily_tasks',
            'poor_organization', 'difficulty_sustaining_attention',
            'restlessness', 'impulsivity_score', 'screen_time_daily',
            'phone_unlocks_per_day', 'working_memory_score'
        ]
        
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"Missing required field: {field}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Make prediction
        result = predict_adhd(data)
        
        # Return response
        return Response({
            "prediction": result,
            "message": "ADHD prediction completed successfully"
        })
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
class MoodLogViewSet(viewsets.ModelViewSet):
    queryset = MoodLog.objects.all()
    serializer_class = MoodLogSerializer




