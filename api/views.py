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
    permission_classes = [AllowAny]

    def post(self, request):
        university_name = request.data.get('university_name')
        campus_name = request.data.get('campus_name')
        course_name = request.data.get('course_name')

        try:
            university = University.objects.get(name=university_name)
            campus = Campus.objects.get(name=campus_name, university=university)
            course = Course.objects.get(name=course_name, campus=campus, university=university)
        except University.DoesNotExist:
            return Response({'error': 'Invalid university selection'}, status=status.HTTP_400_BAD_REQUEST)
        except Campus.DoesNotExist:
            return Response({'error': 'Invalid campus selection'}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({'error': 'Invalid course selection'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user using the serializer
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            UserProfile.objects.create(
                user=user,
                university=university,
                campus=campus,
                course=course,
                phone_number=request.data.get('phone_number')
            )
            return Response({'token': token.key, 'email': user.email}, status=status.HTTP_201_CREATED)
        
        # Return validation errors for debugging
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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

            try:
                # Get the user's profile and serialize it
                profile = UserProfile.objects.get(user=user)
                profile_serializer = UserProfileSerializer(profile)
            except UserProfile.DoesNotExist:
                return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

            # Combine the user info and profile info
            response_data = {
                'token': token.key,
                'profile': profile_serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# Logout view
class LogoutUser(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can log out

    def post(self, request):
        try:
            # Get the user's token
            request.user.auth_token.delete()  # Delete the user's token
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


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

    def get(self, request):
        campuses = Campus.objects.all()
        serializer = CampusSerializer(campuses, many=True)
        return Response(serializer.data)

# Fetch course data based on campus (public access)
class CourseList(APIView):
    permission_classes = [AllowAny]  # Public access allowed

    def get(self, request):
        courses = Course.objects.all()
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

class MaterialList(APIView):
    permission_classes= [AllowAny]
    def get(self, request, university_id, campus_id, course_id, material_type=None):
        # Filter materials based on university, campus, course, and optionally material type
        materials = Material.objects.filter(
            university_id=university_id,
            campus_id=campus_id,
            course_id=course_id
        )
        if material_type:
            materials = materials.filter(material_type=material_type)

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

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Retrieve the user profile for the authenticated user
            profile = UserProfile.objects.all()
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)