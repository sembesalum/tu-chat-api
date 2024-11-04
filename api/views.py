from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import status
from .models import University, Campus, Course, Material, Event, Blog, UserProfile, Message, Community, Group, UserGroup
from .serializers import (UniversitySerializer, CampusSerializer, CourseSerializer, 
                          MaterialSerializer, EventSerializer, BlogSerializer, 
                          UserSerializer, UserProfileSerializer,MessageSerializer, CommunitySerializer, GroupSerializer, UserGroupSerializer)

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
    permission_classes = [AllowAny]

    def get(self, request, university_id, campus_id, course_id, material_type=None):
        # Filter materials based on university, campus, course, and optionally material type
        materials = Material.objects.filter(
            university_id=university_id,
            campus_id=campus_id,
            course_id=course_id
        )

        if material_type:
            materials = materials.filter(material_type=material_type)

        # Create a list to store the serialized materials with URLs
        materials_with_urls = []
        
        for material in materials:
            # Check if material.file is not None
            if material.file:
                material.file_url = request.build_absolute_uri(material.file.url)
            else:
                material.file_url = None  # Handle cases where file is not present

            # Append the serialized data to the new list
            materials_with_urls.append({
                'id': material.id,
                'title': material.title,  # Add any other fields you want
                'subtitle': material.subtitle,
                'file_url': material.file_url,
                'material_type': material.material_type,
                # Add other fields from Material model as necessary
            })

        return Response(materials_with_urls)




# Add and list events
class EventList(APIView):
    permission_classes = [AllowAny]

    def get(self, request, university_id=None):
        # Check if university_id is provided; if not, return all events
        if university_id:
            events = Event.objects.filter(university_id=university_id)
        else:
            events = Event.objects.all()

        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add blogs and fetch blog posts
class BlogList(APIView):
    permission_classes = [AllowAny]

    def get(self, request, university_id=None):
        # Check if university_id is provided; if not, return all events
        if university_id:
            blogs = Blog.objects.filter(university_id=university_id)
        else:
            blogs = Blog.objects.all()

        serializer = EventSerializer(blogs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = BlogSerializer(data=request.data, context={'request': request})
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
        
# Messaging
class CreateMessageView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return Message.objects.filter(group_id=group_id)

# Community
class CreateCommunityView(generics.CreateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

class CommunityListView(generics.ListAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.AllowAny]

# Groups
class CreateGroupView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupListView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        community_id = self.kwargs.get('community_id')
        if community_id:
            return Group.objects.filter(community_id=community_id)
        return Group.objects.all()

    def get(self, request, *args, **kwargs):
        groups = self.get_queryset()
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# User Group Management
class JoinGroupView(generics.CreateAPIView):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LeaveGroupView(generics.DestroyAPIView):
    queryset = UserGroup.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        group_id = self.kwargs['group_id']
        return UserGroup.objects.get(user=user, group__id=group_id)

class PromoteUserView(generics.UpdateAPIView):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(is_admin=True)
        
class MarkMessageAsReadView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(read=True)
        
class SendMessageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, group_id):
        # Check if the group exists
        group = get_object_or_404(Group, id=group_id)

        # Prepare the message data
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Use None if user is anonymous or the actual user if authenticated
        sender = request.user if request.user.is_authenticated else None

        # Create the message
        message = Message(sender=sender, group=group, content=content)
        message.save()

        # Serialize the response
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

