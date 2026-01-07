#It converts database information to JSON for the web, and JSON back to database information.

from rest_framework import serializers
from .models import User, Doctor, DoctorFeedback, Booking, Book, TimeSlot, MoodLog


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

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


