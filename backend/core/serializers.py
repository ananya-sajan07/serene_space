#It converts database information to JSON for the web, and JSON back to database information.

from rest_framework import serializers
from .models import *


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False}
        }
    
    def update(self, instance, validated_data):
        # Remove password if not provided (keep existing)
        if 'password' not in validated_data or not validated_data['password']:
            validated_data.pop('password', None)
        
        # If email not provided, keep existing
        if 'email' not in validated_data:
            validated_data['email'] = instance.email
            
        return super().update(instance, validated_data)

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False}
        }
    
    def update(self, instance, validated_data):
        # Remove password if not provided (keep existing)
        if 'password' not in validated_data or not validated_data['password']:
            validated_data.pop('password', None)
        
        # If email not provided, keep existing
        if 'email' not in validated_data:
            validated_data['email'] = instance.email
            
        return super().update(instance, validated_data)

class DoctorFeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)

    class Meta:
        model = DoctorFeedback
        fields = '__all__'
        read_only_fields = ['user', 'doctor'] #User and doctor set by API, not user input

class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only = True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    time_slot_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'doctor', 'time_slot', 'status', 'booked_time']

    def get_time_slot_details(self, obj):
        return{
            'date': obj.time_slot.date,
            'available_slots': obj.time_slot.slot_data.get('slots', [])
        }

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class TimeSlotSerializer(serializers.ModelSerializer):
    slots_list = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = '__all__'
    
    def get_slots_list(self, obj):
        # Return the slots array from slot_data
        return obj.slot_data.get('slots', [])

class MoodLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodLog
        fields = '__all__'

class AssessmentResultSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = AssessmentResult
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def create(self, validated_data):
        # Ensure user is set properly
        return AssessmentResult.objects.create(**validated_data)