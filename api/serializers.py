from rest_framework import serializers
from django.contrib.auth.models import User
from .models import University, Campus, Course, Material, Event, Blog, UserProfile

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'

class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    university = serializers.StringRelatedField()
    campus = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'university', 'campus']


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']  # Only include email and password
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        
        # Generate a username based on the email if needed
        username = email.split('@')[0]  # Generate username from email

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    university = serializers.CharField(source='university.name', read_only=True)
    university_id = serializers.IntegerField(source='university.id', read_only=True)
    campus = serializers.CharField(source='campus.name', read_only=True)
    campus_id = serializers.IntegerField(source='campus.id', read_only=True)
    course = serializers.CharField(source='course.name', read_only=True)
    course_id = serializers.IntegerField(source='course.id', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'phone_number', 'university', 'university_id', 
            'campus', 'campus_id', 'course', 'course_id'
        ]
