from django.db import IntegrityError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models import Max, F, Q
from django.db import models
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import random
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import OTP, BlockedUser, BlogComment, Follow, Leaders, Notification, PersonalMessage, Product, University, Campus, Course, Material, Event, Blog, UserProfile, Message, Community, Group, UserGroup
from .serializers import (BlogCommentSerializer, ChatUserSerializer, NotificationSerializer, PersonalMessageSerializer, ProductSerializer, UniversitySerializer, CampusSerializer, CourseSerializer, 
                          MaterialSerializer, EventSerializer, BlogSerializer, 
                          UserSerializer, UserProfileSerializer,MessageSerializer, CommunitySerializer, GroupSerializer, UserGroupSerializer, LeadersSerializer)




# User registration view
class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        university_name = request.data.get('university_name')
        campus_name = request.data.get('campus_name')
        course_name = request.data.get('course_name')

        # Retrieve university, campus, and course
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

        # Check for existing username and email
        if User.objects.filter(username=request.data.get('username')).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=request.data.get('email')).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user using the serializer
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                UserProfile.objects.create(
                    user=user,
                    university=university,
                    campus=campus,
                    course=course,
                    phone_number=request.data.get('phone_number'),
                    username = request.data.get('username')
                )
                return Response({'token': token.key, 'email': user.email}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'error': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Return validation errors
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

        # Verify password
        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            try:
                # Get the user's profile and serialize it
                profile = UserProfile.objects.get(user=user)
                profile_serializer = UserProfileSerializer(profile)
            except UserProfile.DoesNotExist:
                return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

            # Combine user and profile info in response
            response_data = {
                'user_id': user.id,  # Add user ID here
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
        
class ValidateToken(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # If the request reaches here, the token is valid, and the user exists
        return Response({
            'user_id': request.user.id,
            'email': request.user.email,
            'username': request.user.username
        }, status=status.HTTP_200_OK)


class RequestPasswordReset(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a 6-digit OTP
        otp_code = f"{random.randint(100000, 999999)}"

        # Create or update the OTP entry for the user
        OTP.objects.update_or_create(user=user, defaults={'otp_code': otp_code, 'is_verified': False})

        # Send the OTP to the user's email
        send_mail(
            subject="Password Reset OTP",
            message=f"Your OTP code for password reset is {otp_code}",
            from_email="noreply@yourdomain.com",
            recipient_list=[email],
        )

        return Response({'message': 'OTP has been sent to your email'}, status=status.HTTP_200_OK)
    
class VerifyOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        try:
            user = User.objects.get(email=email)
            otp_entry = OTP.objects.get(user=user, otp_code=otp_code)

            if otp_entry.is_verified:
                return Response({'error': 'OTP has already been used'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark the OTP as verified
            otp_entry.is_verified = True
            otp_entry.save()

            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({'error': 'Invalid email or OTP'}, status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email=email)
            otp_entry = OTP.objects.get(user=user)

            if not otp_entry.is_verified:
                return Response({'error': 'OTP has not been verified'}, status=status.HTTP_400_BAD_REQUEST)

            # Set the new password
            user.set_password(new_password)
            user.save()

            # Optionally delete the OTP entry after successful password reset
            otp_entry.delete()

            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

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
            blogs = Blog.objects.filter(university_id=university_id, is_breaking_news=False)
        else:
            blogs = Blog.objects.all()

        serializer = BlogSerializer(blogs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = BlogSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            # Retrieve the user profile by user ID
            profile = UserProfile.objects.get(user__id=user_id)
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
    permission_classes = [AllowAny]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)

        # Ensure the user is a follower
        user_id = request.data.get('userID')
        user = get_object_or_404(User, id=user_id)
        if user not in group.followers.all():
            return Response({'error': 'You must follow this group to send messages.'}, 
                            status=status.HTTP_403_FORBIDDEN)

        # Proceed with your existing logic
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required.'}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)

        message = Message(userID=user, group=group, content=content, username=username)
        message.save()

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FollowGroupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, group_id):
        userID = request.data.get('userID')  # Get userID from request data

        # Check if userID is provided
        if not userID:
            return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user object using the userID
        try:
            user = User.objects.get(id=userID)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get the group object using the group_id
        group = get_object_or_404(Group, id=group_id)

        # Check if the user is already following the group
        follow_exists = Follow.objects.filter(user=user, group=group).exists()

        if follow_exists:
            # If user is already following, unfollow the group
            Follow.objects.filter(user=user, group=group).delete()  # Unfollow the group
            return Response({
                'message': 'You have unfollowed the group.',
                'follower_count': group.followers.count(),
                'is_following': False
            }, status=status.HTTP_200_OK)
        else:
            # If user is not following, follow the group
            Follow.objects.create(user=user, group=group)  # Follow the group
            return Response({
                'message': 'You are now following the group.',
                'follower_count': group.followers.count(),
                'is_following': True
            }, status=status.HTTP_200_OK)

            
    
class LeadersView(APIView):
    def get(self, request, university_id, campus_id):
        try:
            # Filter leaders by university_id and campus_id
            leaders = Leaders.objects.filter(university_id=university_id, campus_id=campus_id)
            if leaders.exists():
                leaders_data = [
                    {
                        "names": leader.names,
                        "title": leader.title,
                        "image": request.build_absolute_uri(leader.image.url) if leader.image else '',
                    }
                    for leader in leaders
                ]
                return JsonResponse(leaders_data, safe=False, status=200)
            else:
                return JsonResponse({"message": "No leaders found for the specified university and campus."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class ProductCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Create a mutable copy of request data
        data = request.data.copy()

        # Associate user if provided in the request
        user_id = data.get('user')
        if user_id:
            data['user'] = user_id
        elif request.user and not request.user.is_anonymous:
            data['user'] = request.user.id
        else:
            return Response({"error": "User is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle images separately
        images = {
            'image1': request.FILES.get('image1'),
            'image2': request.FILES.get('image2'),
            'image3': request.FILES.get('image3'),
            'image4': request.FILES.get('image4'),
        }

        # Add images to the data dictionary if they exist
        for key, file in images.items():
            if file:
                data[key] = file

        # Print the received data for debugging
        print("Received data:", data)

        # Serialize data and include the request in the context
        serializer = ProductSerializer(data=data, context={'request': request})  # Pass request to context
        if serializer.is_valid():
            # Save the validated data
            product = serializer.save()

            # Check if images are uploaded and associate them with the product instance
            for key, file in images.items():
                if file:
                    # Assuming that you are using a FileField in your Product model for image fields
                    setattr(product, key, file)
                    product.save()  # Save the image field to the product

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Log errors for debugging
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        
    def get(self, request, *args, **kwargs):
        product_type = request.GET.get('type')  # Retrieve the 'type' query parameter
        products = Product.objects.all()
        if product_type:
            products = products.filter(material_type=product_type)

        # Pass request to serializer context
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

class ProductListByCategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category):
        # Validate the category against Product's material_type choices
        valid_categories = [choice[0] for choice in Product.PRODUCT_TYPE_CHOICES]
        if category not in valid_categories:
            return Response(
                {"error": "Invalid product category"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Filter products by the validated category
        products = Product.objects.filter(material_type=category)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
        
class ProductMarkAsSoldView(APIView):
    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        user_id = request.data.get('user_id')  # Extract user_id from the request
        if product.user.id != user_id:
            return Response({"error": "You are not authorized to mark this product as sold."}, status=status.HTTP_403_FORBIDDEN)

        product.is_sold = True
        product.save()
        return Response({"detail": "Product marked as sold successfully."}, status=status.HTTP_200_OK)


class ProductUpdateView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, pk, format=None):
        """
        Handle PUT requests to update a product while maintaining existing images
        """
        try:
            # Get existing product
            product = Product.objects.get(pk=pk)
            
            # Create mutable copy of request data
            data = request.data.dict() if hasattr(request.data, 'dict') else request.data.copy()
            
            # Ensure required fields are maintained
            if 'user' not in data:
                data['user'] = product.user.id
            
            # Maintain all existing image fields - ignore any image updates in request
            image_fields = ['image1', 'image2', 'image3', 'image4']
            for field in image_fields:
                existing_image = getattr(product, field)
                if existing_image:
                    data[field] = existing_image
                elif field in data:
                    del data[field]  # Remove image field if it was provided but product has no existing image
            
            # Serialize with existing product instance for update
            serializer = ProductSerializer(product, data=data, partial=False, context={'request': request})
            if serializer.is_valid():
                updated_product = serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductDeleteView(APIView):
    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        user_id = request.data.get('user_id')  # Extract user_id from the request
        if product.user.id != user_id:
            return Response({"error": "You are not authorized to delete this product."}, status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response({"detail": "Product deleted successfully."}, status=status.HTTP_200_OK)
    

# class SendDirectMessageView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, user_id):
#         """
#         Send a direct message to another user.
#         """
#         print(f"Request data: {request.data}")

#         # The user_id in the URL will be the sender's ID
#         sender_user_id = user_id

#         try:
#             sender = User.objects.get(id=sender_user_id)
#         except User.DoesNotExist:
#             return Response({'error': 'Sender user not found.'}, status=status.HTTP_404_NOT_FOUND)

#         recipient_id = request.data.get('recipient')
#         if not recipient_id:
#             return Response({'error': 'Recipient userID is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             recipient_user = User.objects.get(id=recipient_id)
#         except User.DoesNotExist:
#             return Response({'error': 'Recipient not found.'}, status=status.HTTP_404_NOT_FOUND)

#         if sender.id == recipient_user.id:
#             return Response({'error': 'Sender and recipient cannot be the same.'}, status=status.HTTP_400_BAD_REQUEST)

#         content = request.data.get('content')
#         if not content:
#             return Response({'error': 'Message content is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         message = PersonalMessage(sender=sender, recipient=recipient_user, content=content)
#         message.save()

#         serializer = PersonalMessageSerializer(message)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

class SendDirectMessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, user_id):
        """
        Send a direct message to another user with block user checks.
        """
        # The user_id in the URL will be the sender's ID
        sender_user_id = user_id

        try:
            sender = User.objects.get(id=sender_user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Sender user not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        recipient_id = request.data.get('recipient')
        if not recipient_id:
            return Response(
                {'error': 'Recipient userID is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            recipient_user = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if sender and recipient are the same
        if sender.id == recipient_user.id:
            return Response(
                {'error': 'Sender and recipient cannot be the same.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if recipient has blocked the sender
        if BlockedUser.objects.filter(
            blocker=recipient_user, 
            blocked=sender
        ).exists():
            return Response(
                {
                    'error': 'You cannot send messages to this user as they have blocked you.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if sender has blocked the recipient
        if BlockedUser.objects.filter(
            blocker=sender, 
            blocked=recipient_user
        ).exists():
            return Response(
                {
                    'error': 'You have blocked this user. Unblock them to send messages.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        content = request.data.get('content')
        if not content:
            return Response(
                {'error': 'Message content is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create and save the message
        message = PersonalMessage(
            sender=sender, 
            recipient=recipient_user, 
            content=content
        )
        message.save()

        serializer = PersonalMessageSerializer(message)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED
        )


class BlockUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Block a user to prevent messaging
        """
        blocked_id = request.data.get('user_id')
        if not blocked_id:
            return Response(
                {'error': 'User ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            blocked_user = User.objects.get(pk=blocked_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.user.id == blocked_user.id:
            return Response(
                {'error': 'You cannot block yourself'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or get existing block
        block, created = BlockedUser.objects.get_or_create(
            blocker=request.user,
            blocked=blocked_user
        )
        
        if created:
            # Delete any existing messages between these users
            PersonalMessage.objects.filter(
                models.Q(sender=request.user, recipient=blocked_user) |
                models.Q(sender=blocked_user, recipient=request.user)
            ).delete()
            
            return Response(
                {'message': f'You have blocked {blocked_user.username}'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': f'You have already blocked {blocked_user.username}'},
                status=status.HTTP_200_OK
            )

class UnblockUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Unblock a user to allow messaging again
        """
        blocked_id = request.data.get('user_id')
        if not blocked_id:
            return Response(
                {'error': 'User ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            blocked_user = User.objects.get(pk=blocked_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            block = BlockedUser.objects.get(
                blocker=request.user, 
                blocked=blocked_user
            )
            block.delete()
            return Response(
                {'message': f'You have unblocked {blocked_user.username}'},
                status=status.HTTP_200_OK
            )
        except BlockedUser.DoesNotExist:
            return Response(
                {'error': 'This user is not blocked'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class CheckBlockStatusView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Check if a user is blocked
        """
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'User ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        is_blocked = BlockedUser.objects.filter(
            blocker=request.user, blocked=target_user
        ).exists()

        return Response(
            {'blocked': is_blocked},
            status=status.HTTP_200_OK
        )


class GetMessagesView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this endpoint

    def get(self, request, recipient):
        """
        Get all messages between a specific sender and recipient.
        """
        # Log the request data for debugging
        print(f"Request data: {request.query_params}")

        sender_id = request.query_params.get('sender_id')  # Expecting sender_id to be passed in query params

        if not sender_id:
            return Response({'error': 'Sender ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the recipient user by recipient ID (from the URL parameter)
        try:
            recipient_user = User.objects.get(id=recipient)
        except User.DoesNotExist:
            return Response({'error': 'Recipient not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch the sender user by sender ID (from the query parameter)
        try:
            sender_user = User.objects.get(id=sender_id)
        except User.DoesNotExist:
            return Response({'error': 'Sender not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get all messages between the sender and recipient (both directions)
        messages = PersonalMessage.objects.filter(
            (Q(sender=sender_user, recipient=recipient_user) | 
             Q(sender=recipient_user, recipient=sender_user))
        ).order_by('timestamp')  # Order by timestamp to maintain conversation flow

        # If no messages are found
        if not messages.exists():
            return Response({'message': 'No messages found for this sender and recipient.'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize and return the messages
        serializer = PersonalMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

class ChatUsersListView(APIView):
    permission_classes = [AllowAny]  # or your desired permission class

    def get(self, request, user_id):
        try:
            # Get the user object from the user_id
            user = User.objects.get(id=user_id)

            # Get all unique users the specified user has chatted with
            users_chatted_with = PersonalMessage.objects.filter(
                Q(sender=user) | Q(recipient=user)
            ).values('sender', 'recipient').distinct()

            # Collect the unique users (sender or recipient)
            chat_users = set()
            for chat in users_chatted_with:
                if chat['sender'] != user.id:
                    chat_users.add(chat['sender'])
                if chat['recipient'] != user.id:
                    chat_users.add(chat['recipient'])

            # Fetch usernames for the list of user ids
            users = User.objects.filter(id__in=chat_users)
            
            # Prepare the data to send back
            chat_users_data = []
            for user in users:
                chat_users_data.append({
                    'recipient': user.id,
                    'username': user.username
                })

            # Serialize the data
            serializer = ChatUserSerializer(chat_users_data, many=True)

            return Response({"users": serializer.data})

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
class DeleteMessageView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this endpoint, but we will check permissions within the method

    def delete(self, request, message_id):
        """
        Delete a specific message by its ID.
        """
        # Get the message from the database
        message = get_object_or_404(PersonalMessage, id=message_id)

        # Check if the requesting user is either the sender or the recipient
        user_id = request.query_params.get('user_id')  # Expecting user_id to be passed in query params
        if not user_id:
            return Response({'error': 'User ID is required to delete the message.'}, status=status.HTTP_400_BAD_REQUEST)

        if message.sender.id != int(user_id) and message.recipient.id != int(user_id):
            return Response({'error': 'You do not have permission to delete this message.'}, status=status.HTTP_403_FORBIDDEN)

        # Delete the message
        message.delete()

        return Response({'message': 'Message deleted successfully.'}, status=status.HTTP_200_OK)
    
class NotificationList(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        notification = Notification.objects.all()
        serializer = NotificationSerializer(notification, many=True)
        return Response(serializer.data)
    

class UserListView(View):
    def get(self, request):
        # Debug the query
        profiles = User.objects.all().values('id', 'username')
        print(f"Fetched Profiles: {list(profiles)}")
        
        # Return the response as JSON
        return JsonResponse(list(profiles), safe=False, status=200)

class UserProfileUpdateView(APIView):
    permission_classes = [AllowAny]  # No authentication required
    
    def get_object(self, user_id):
        """Get user profile or return 404 if not found"""
        try:
            return UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            raise Http404

    def put(self, request, user_id, *args, **kwargs):
        try:
            profile = self.get_object(user_id)
            serializer = UserProfileSerializer(
                profile, 
                data=request.data, 
                partial=True
            )
            
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK
            )
            
        except Http404:
            return Response(
                {"status": "error", "message": "User profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
class BlogCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = BlogCommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        blog_id = self.kwargs['blog_id']
        return BlogComment.objects.filter(blog_id=blog_id, parent_comment__isnull=True)

    def perform_create(self, serializer):
        blog_id = self.kwargs['blog_id']
        try:
            blog = get_object_or_404(Blog, id=blog_id)
            serializer.save(
                blog=blog,
                user=self.request.user if self.request.user.is_authenticated else None
            )
        except Http404:
            return Response(
                {'error': 'Blog not found'},
                status=status.HTTP_400_BAD_REQUEST
            )


class BlogCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class BlogCommentReplyCreateView(generics.CreateAPIView):
    serializer_class = BlogCommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return BlogComment.objects.all()

    def perform_create(self, serializer):
        comment_id = self.kwargs['comment_id']
        parent_comment = BlogComment.objects.get(id=comment_id)
        serializer.save(
            blog=parent_comment.blog,
            user=self.request.user,
            parent_comment=parent_comment
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class BlogCommentLikeToggleView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        comment_id = kwargs.get('comment_id')
        comment = BlogComment.objects.get(id=comment_id)
        user = request.user

        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            action = 'unliked'
        else:
            comment.likes.add(user)
            action = 'liked'

        return Response({
            'status': 'success',
            'action': action,
            'total_likes': comment.total_likes
        }, status=status.HTTP_200_OK)


class BlogCommentRepliesListView(generics.ListAPIView):
    serializer_class = BlogCommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        comment_id = self.kwargs['comment_id']
        return BlogComment.objects.filter(parent_comment_id=comment_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context