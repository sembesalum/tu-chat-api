from django.contrib import admin
from .models import University, Campus, Course, Material, Event, Blog, UserProfile

# Customize how University is displayed in admin
@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Show university name in list view
    search_fields = ('name',)  # Add search bar for university name

# Customize how Campus is displayed in admin
@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ('name', 'university')  # Show campus name and its university
    search_fields = ('name', 'university__name')  # Search by campus name and university name
    list_filter = ('university',)  # Filter campuses by university

# Customize how Course is displayed in admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'campus', 'university')  # Show course name, campus, and university
    search_fields = ('name', 'campus__name', 'university__name')  # Add search by course, campus, university
    list_filter = ('campus', 'university')  # Filter by campus and university

    def university(self, obj):
        return obj.campus.university.name  # Get the related university name from the campus
    university.short_description = 'University'

# Customize how Material is displayed in admin
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('material_type', 'university', 'campus', 'course', 'file')  # Show material type and associated fields
    search_fields = ('material_type', 'university__name', 'campus__name', 'course__name')  # Search for materials
    list_filter = ('material_type', 'university', 'campus', 'course')  # Filters

# Customize how Event is displayed in admin
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'university', 'campus', 'date', 'time', 'is_breaking_news')  # Show event fields
    search_fields = ('title', 'university__name', 'campus__name')  # Add search
    list_filter = ('is_breaking_news', 'university', 'campus')  # Add filters

# Customize how Blog is displayed in admin
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')  # Show title and author
    search_fields = ('title', 'author__username')  # Add search by title and author
    list_filter = ('author',)  # Filter by author

# Customize how UserProfile is displayed in admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'campus', 'course', 'phone_number')  # Show user profile fields
    search_fields = ('user__username', 'university__name', 'campus__name', 'course__name')  # Add search
    list_filter = ('university', 'campus', 'course')  # Add filters
