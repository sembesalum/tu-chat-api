from django.urls import path
from .views import (LogoutUser, RegisterUser, LoginUser, SendMessageView, UniversityList, CampusList, CourseList, 
                    AddMaterial, MaterialList, EventList, BlogList, UserProfileView,CreateMessageView,
    MessageListView,
    CreateCommunityView,
    CommunityListView,
    CreateGroupView,
    GroupListView,
    JoinGroupView,
    LeaveGroupView,
    PromoteUserView,MarkMessageAsReadView)

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('universities/', UniversityList.as_view(), name='universities'),
    path('campuses/', CampusList.as_view(), name='campuses'),
    path('courses/', CourseList.as_view(), name='courses'),
    path('universities/<int:university_id>/campuses/', CampusList.as_view(), name='campuses'),
    path('campuses/<int:campus_id>/courses/', CourseList.as_view(), name='courses'),
    path('materials/add/', AddMaterial.as_view(), name='add_material'),
    
    # Updated materials URL to include optional material type
    path('materials/<int:university_id>/<int:campus_id>/<int:course_id>/', MaterialList.as_view(), name='materials'),
    path('materials/<int:university_id>/<int:campus_id>/<int:course_id>/<str:material_type>/', MaterialList.as_view(), name='materials_with_type'),

    path('events/<int:university_id>', EventList.as_view(), name='events'),
    path('blogs/<int:university_id>', BlogList.as_view(), name='blogs'),
    
     # Messaging
    path('groups/<int:group_id>/messages/send/', SendMessageView.as_view(), name='send_message'),
    path('groups/<int:group_id>/messages/', MessageListView.as_view(), name='message-list'),

    # Community
    path('communities/create/', CreateCommunityView.as_view(), name='create-community'),
    path('communities/', CommunityListView.as_view(), name='community-list'),

    # Groups
    path('groups/create/', CreateGroupView.as_view(), name='create-group'),
    path('communities/<community_id>/groups/', GroupListView.as_view(), name='group-list'),
    
    # Group management
    path('groups/join/<int:group_id>/', JoinGroupView.as_view(), name='join-group'),
    path('groups/leave/<int:group_id>/', LeaveGroupView.as_view(), name='leave-group'),
    path('groups/promote/<int:user_id>/<int:group_id>/', PromoteUserView.as_view(), name='promote-user'),
    
    path('messages/mark-as-read/<int:message_id>/', MarkMessageAsReadView.as_view(), name='mark-message-as-read'),
]
