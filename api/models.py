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
    title = models.CharField(max_length=255)
    time = models.TimeField()
    date = models.DateField()
    image = models.ImageField(upload_to='events/')
    is_breaking_news = models.BooleanField(default=False)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/')
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
