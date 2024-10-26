from django.urls import path
from .views import (LogoutUser, RegisterUser, LoginUser, UniversityList, CampusList, CourseList, 
                    AddMaterial, MaterialList, EventList, BlogList, UserProfileView)

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

    path('events/', EventList.as_view(), name='events'),
    path('blogs/', BlogList.as_view(), name='blogs'),
]
