#It tells Django, which function to call when someone visits a specific web address.

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'moodlogs', MoodLogViewSet)
router.register(r'doctors', DoctorViewSet)


urlpatterns = [
    path('doctors/nearby/', find_nearby_doctors_api, name = 'nearby_doctors'),
    path('users/<int:user_id>/nearby-doctors/', find_nearby_doctors_by_user_api, name='user_nearby_doctors'),
    path('doctors/<int:doctor_id>/feedback/', doctor_feedback_api, name='doctor_feedback'),
    path('users/<int:user_id>/bookings/', booking_api, name= 'user_bookings'),
    path('doctors/<int:doctor_id>/bookings/', booking_api, name='doctor_bookings'),
    path('bookings/<int:booking_id>/status/', update_booking_status_api, name='update_booking_status'),
    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('doctor_register/', doctor_register, name = 'doctor_register'),
    path('predict_adhd/', predict_adhd_api, name = 'predict_adhd'),
    path('predict_anxiety/', predict_anxiety_api, name='predict_anxiety'),
    path('doctors/<int:doctor_id>/availability/', update_doctor_availability, name = 'update_doctor_availability'),
    path('books/', add_book_api, name = 'add_book'),
    path('books/<int:book_id>/', book_detail_api, name='book_detail'),
    path('user/books/', get_books_api, name='user_books'),
    path('user/books/<int:book_id>/', get_book_detail_api, name='user_book_detail'),
    path('doctors/<int:doctor_id>/time_slots/', doctor_time_slots_api, name='doctor_time_slots'),
    path('time_slots/<int:time_slot_id>/', time_slot_detail_api, name='time_slot_detail'),   
    path('chat/', MentalHealthChatAPIView.as_view(), name='mental_health_chat'),
    path('chat/test/', ChatbotTestAPIView.as_view(), name='chatbot_test'),
    path('users/<int:user_id>/assessments/', get_user_assessments_api, name='user_assessments'),
    path('assessments/<int:assessment_id>/', assessment_detail_api, name='assessment_detail'), 
    path('save-assessment/', save_assessment_result, name='save_assessment'),
    # Prescription URLs
    path('prescriptions/create/', create_prescription, name='create_prescription'),
    path('users/<int:user_id>/prescriptions/', get_prescriptions, name='user_prescriptions'),
    path('doctors/<int:doctor_id>/prescriptions/', get_prescriptions, name='doctor_prescriptions'),
    path('prescriptions/<int:prescription_id>/', prescription_detail_api, name='prescription_detail'),
    # Prescription PDF download
    path('prescriptions/<int:prescription_id>/download/', download_prescription_pdf, name='download_prescription_pdf'),
]


