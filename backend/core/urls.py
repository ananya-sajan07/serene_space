from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, MoodLogViewSet, login, register

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'moodlogs', MoodLogViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
]


