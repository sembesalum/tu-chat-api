from django.urls import path
from .views import (RegisterUser, LoginUser, UniversityList, CampusList, CourseList, 
                    AddMaterial, MaterialList, EventList, BlogList)

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('universities/', UniversityList.as_view(), name='universities'),
    path('universities/<int:university_id>/campuses/', CampusList.as_view(), name='campuses'),
    path('campuses/<int:campus_id>/courses/', CourseList.as_view(), name='courses'),
    path('materials/add/', AddMaterial.as_view(), name='add_material'),
    path('materials/<int:university_id>/<int:campus_id>/<int:course_id>/', MaterialList.as_view(), name='materials'),
    path('events/', EventList.as_view(), name='events'),
    path('blogs/', BlogList.as_view(), name='blogs'),
]
