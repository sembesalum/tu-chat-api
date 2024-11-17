from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Leaders, University, Campus, Course, Material, Event, Blog, UserProfile, Message, Community, Group, UserGroup

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
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = ['id', 'title', 'subtitle', 'material_type', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url)


class EventSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'time', 'date', 'image_url', 'is_breaking_news', 'university_id']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class BlogSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'date', 'image_url', 'is_breaking_news', 'university_id']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    
# class BlogSerializer(serializers.ModelSerializer):
#     image_url = serializers.SerializerMethodField()

#     class Meta:
#         model = Blog
#         fields = ['id', 'title', 'author', 'description', 'date', 'image_url', 'is_breaking_news', 'university_id']

#     def get_image_url(self, obj):
#         return obj.image  # Simply return the URL since it's already a string
        
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
    email = serializers.EmailField(source='user.email', read_only=True)  # Maps email from User model
    university = serializers.CharField(source='university.name', read_only=True)  # Maps university name
    university_id = serializers.IntegerField(source='university.id', read_only=True)  # Maps university ID
    campus = serializers.CharField(source='campus.name', read_only=True)  # Maps campus name
    campus_id = serializers.IntegerField(source='campus.id', read_only=True)  # Maps campus ID
    course = serializers.CharField(source='course.name', read_only=True)  # Maps course name
    course_id = serializers.IntegerField(source='course.id', read_only=True)  # Maps course ID

    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'phone_number', 'university', 'university_id', 
            'campus', 'campus_id', 'course', 'course_id'
        ]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'group', 'content', 'timestamp', 'read']
        read_only_fields = ['id', 'sender', 'timestamp', 'read', 'content']  # sender is set in the view


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'admin']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'profile_picture', 'community', 'admin', 'interaction_permission']


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ['id', 'user', 'group', 'is_admin']
        
class LeadersSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Leaders
        fields = ['names', 'title', 'image']
        
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None