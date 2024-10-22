from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import status
from .models import University, Campus, Course, Material, Event, Blog, UserProfile
from .serializers import (UniversitySerializer, CampusSerializer, CourseSerializer, 
                          MaterialSerializer, EventSerializer, BlogSerializer, 
                          UserSerializer, UserProfileSerializer)

# User registration view
class RegisterUser(APIView):
    permission_classes = [AllowAny]  # Allow public access for registration
    def post(self, request):
        # Extract the university, campus, and course from the request data
        university_id = request.data.get('university_id')
        campus_id = request.data.get('campus_id')
        course_id = request.data.get('course_id')

        # Validate if the university, campus, and course exist
        try:
            university = University.objects.get(id=university_id)
            campus = Campus.objects.get(id=campus_id)
            course = Course.objects.get(id=course_id)
        except (University.DoesNotExist, Campus.DoesNotExist, Course.DoesNotExist):
            return Response({'error': 'Invalid university, campus, or course selection'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create the token for the user
            token, created = Token.objects.get_or_create(user=user)

            # Create a UserProfile and associate it with the user
            UserProfile.objects.create(
                user=user,
                university=university,
                campus=campus,
                course=course,
                phone_number=request.data.get('phone_number')
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login view
class LoginUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)

            
            user_info = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
            }
            
            return Response(user_info, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


# Fetch university data (public access)
class UniversityList(APIView):
    permission_classes = [AllowAny]  # Public access allowed

    def get(self, request):
        universities = University.objects.all()
        serializer = UniversitySerializer(universities, many=True)
        return Response(serializer.data)

# Fetch campus data based on university (public access)
class CampusList(APIView):
    permission_classes = [AllowAny]  # Public access allowed

    def get(self, request, university_id):
        campuses = Campus.objects.filter(university_id=university_id)
        serializer = CampusSerializer(campuses, many=True)
        return Response(serializer.data)

# Fetch course data based on campus (public access)
class CourseList(APIView):
    permission_classes = [AllowAny]  # Public access allowed

    def get(self, request, university_id, campus_id):
        courses = Course.objects.filter(university_id=university_id, campus_id=campus_id)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
# Add materials (admin only)
class AddMaterial(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = MaterialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Fetch materials based on university, campus, and course
class MaterialList(APIView):
    def get(self, request, university_id, campus_id, course_id):
        materials = Material.objects.filter(university_id=university_id, campus_id=campus_id, course_id=course_id)
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data)

# Add and list events
class EventList(APIView):
    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add blogs and fetch blog posts
class BlogList(APIView):
    def get(self, request):
        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
