#It tells Django which function to call when someone visits a specific web address.

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import login, register, doctor_register, predict_adhd_api, update_doctor_availability, add_book_api, book_detail_api, get_books_api, get_book_detail_api, UserViewSet, DoctorViewSet, MoodLogViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'moodlogs', MoodLogViewSet)
router.register(r'doctors', DoctorViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('doctor_register/', doctor_register, name = 'doctor_register'),
    path('predict_adhd/', predict_adhd_api, name = 'predict_adhd'),
    path('doctors/<int:doctor_id>/availability/', update_doctor_availability, name = 'update_doctor_availability'),
    path('books/', add_book_api, name = 'add_book'),
    path('books/<int:book_id>/', book_detail_api, name='book_detail'),
    path('user/books/', get_books_api, name='user_books'),
    path('user/books/<int:book_id>/', get_book_detail_api, name='user_book_detail'),
]


