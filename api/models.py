from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class University(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Campus(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Course(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, null=True)  # Add University ForeignKey
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.university.name} - {self.campus.name}"


class Material(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('past_paper', 'Past Paper'),
        ('notes', 'Notes'),
        ('research', 'Research'),
        ('timetable', 'Timetable'),
        ('report', 'Report'),
    ]
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    material_type = models.CharField(max_length=50, choices=MATERIAL_TYPE_CHOICES)
    title = models.CharField(max_length=255, null=True)
    subtitle = models.CharField(max_length=255, null=True)
    file = models.FileField(upload_to='materials/')

class Event(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    is_breaking_news = models.BooleanField(default=False)
    university = models.ForeignKey(
        'University', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.title or "Unnamed Event"

    # campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    # course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/')
    is_breaking_news = models.BooleanField(default=False)
    # created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)  # Fixed typo

    def __str__(self):
        return self.user.username
    
class Community(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    profile_picture = models.ImageField(upload_to='groups/', null=True, blank=True)
    community = models.ForeignKey(Community, related_name='groups', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, related_name='group_admins', on_delete=models.CASCADE)

    # Determines if the group allows interaction of all users or only admins
    ALLOW_INTERACTION_CHOICES = [
        ('all', 'All Users'),
        ('admins', 'Admins Only'),
    ]
    interaction_permission = models.CharField(max_length=20, choices=ALLOW_INTERACTION_CHOICES, default='all')

    def __str__(self):
        return self.name


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages", null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Add this line

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.content}"



class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"
