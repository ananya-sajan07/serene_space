#It tells Django, which function to call when someone visits a specific web address.

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import login, register, doctor_register, predict_adhd_api, predict_anxiety_api, update_doctor_availability, add_book_api, book_detail_api, get_books_api, get_book_detail_api
from .views import doctor_time_slots_api, time_slot_detail_api, find_nearby_doctors_api, find_nearby_doctors_by_user_api,doctor_feedback_api, booking_api, update_booking_status_api
from .views import UserViewSet, DoctorViewSet, MoodLogViewSet

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
]


