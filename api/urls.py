from django.urls import path
from .views import (ChatUsersListView, FollowGroupView, GetMessagesView, LeadersView, LogoutUser, NotificationList, ProductCreateView, ProductDeleteView, ProductMarkAsSoldView, ProductUpdateView,RegisterUser, LoginUser, RequestPasswordReset, ResetPassword, SendDirectMessageView, SendMessageView, UniversityList, CampusList, CourseList, 
                    AddMaterial, MaterialList, EventList, BlogList, UserListView, UserProfileUpdateView, UserProfileView,CreateMessageView,
    MessageListView,
    CreateCommunityView,
    CommunityListView,
    CreateGroupView,
    GroupListView,
    JoinGroupView,
    LeaveGroupView,
    PromoteUserView,MarkMessageAsReadView, VerifyOTP)

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('user-profile/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('update-profile/<int:user_id>/', UserProfileUpdateView.as_view(), name='update-profile'),
    path('universities/', UniversityList.as_view(), name='universities'),
    path('campuses/', CampusList.as_view(), name='campuses'),
    path('courses/', CourseList.as_view(), name='courses'),
    path('universities/<int:university_id>/campuses/', CampusList.as_view(), name='campuses'),
    path('campuses/<int:campus_id>/courses/', CourseList.as_view(), name='courses'),
    path('materials/add/', AddMaterial.as_view(), name='add_material'),
    
    path('password-reset/request-otp/', RequestPasswordReset.as_view(), name='request_password_reset'),
    path('password-reset/verify-otp/', VerifyOTP.as_view(), name='verify_otp'),
    path('password-reset/reset-password/', ResetPassword.as_view(), name='reset_password'),
    
    # Updated materials URL to include optional material type
    path('materials/<int:university_id>/<int:campus_id>/<int:course_id>/', MaterialList.as_view(), name='materials'),
    path('materials/<int:university_id>/<int:campus_id>/<int:course_id>/<str:material_type>/', MaterialList.as_view(), name='materials_with_type'),

    path('events/<int:university_id>', EventList.as_view(), name='events'),
    path('blogs/<int:university_id>', BlogList.as_view(), name='blogs'),
    
     # Messaging
    path('groups/<int:group_id>/messages/send/', SendMessageView.as_view(), name='send_message'),
    path('messages/get-sms/<int:recipient>/', GetMessagesView.as_view(), name='get_sms'),
    path('messages/send-direct/<int:user_id>/', SendDirectMessageView.as_view(), name='send_direct_message'),
    path('groups/<int:group_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('messages/chat-users/<int:user_id>/', ChatUsersListView.as_view(), name='chat_users_list'),

    # Community
    path('communities/create/', CreateCommunityView.as_view(), name='create-community'),
    path('communities/', CommunityListView.as_view(), name='community-list'),

    # Groups
    path('groups/create/', CreateGroupView.as_view(), name='create-group'),
    path('communities/<community_id>/groups/', GroupListView.as_view(), name='group-list'),
    path('groups/<int:group_id>/follow/', FollowGroupView.as_view(), name='toggle_follow'),
    
    # Group management
    path('groups/join/<int:group_id>/', JoinGroupView.as_view(), name='join-group'),
    path('groups/leave/<int:group_id>/', LeaveGroupView.as_view(), name='leave-group'),
    path('groups/promote/<int:user_id>/<int:group_id>/', PromoteUserView.as_view(), name='promote-user'),
    
    path('messages/mark-as-read/<int:message_id>/', MarkMessageAsReadView.as_view(), name='mark-message-as-read'),
    
    # List leaders
     path('leaders/<int:university_id>/<int:campus_id>/', LeadersView.as_view(), name='leaders'),
     
    # e-commerce
    path('products/add/', ProductCreateView.as_view(), name='product-add'),
    path('products/', ProductCreateView.as_view(), name='list_product'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/mark-as-sold/', ProductMarkAsSoldView.as_view(), name='product_mark_as_sold'),
    
    # Notification
    path('notification/', NotificationList.as_view(), name='list-notifications'),
    path('users/', UserListView.as_view(), name='user-list'),
]
