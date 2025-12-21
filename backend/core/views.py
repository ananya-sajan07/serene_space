#User fills form → Browser sends POST request → views.py function runs (Validates data, saves to database, returns success/error response) → Saves to database → Returns JSON response → Browser shows success message
#It takes customer orders (requests), prepares food (processes data), and serves meals (responses).

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .adhd_prediction import predict_adhd
from .models import User, Doctor, Book, MoodLog
from .serializers import UserSerializer, DoctorSerializer, BookSerializer, MoodLogSerializer


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




