from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import login, register, doctor_register, predict_adhd_api, UserViewSet, DoctorViewSet, MoodLogViewSet

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
]


