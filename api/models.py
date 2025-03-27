from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import uuid

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
        ('test', 'Test'),
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    # image = models.URLField(max_length=200, null=True, blank=True)
    is_breaking_news = models.BooleanField(default=False)
    university = models.ForeignKey(
        'University', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    def get_username(self):
        try:
            return self.user.userprofile.username
        except UserProfile.DoesNotExist:
            return "No username"

    def __str__(self):
        return self.title or "Unnamed Event"

    # campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    # course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
class RequestEvent(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    image1 = models.ImageField(upload_to='events/', null=True, blank=True)
    image2 = models.ImageField(upload_to='events/', null=True, blank=True)

    def __str__(self):
        return self.title or "Unnamed Event"

    def image1_link(self):
        if self.image1:
            return f"<a href='{self.image1.url}' download>Download Image 1</a>"
        return "No Image"

    def image2_link(self):
        if self.image2:
            return f"<a href='{self.image2.url}' download>Download Image 2</a>"
        return "No Image"

    image1_link.allow_tags = True
    image1_link.short_description = "Image 1"
    image2_link.allow_tags = True
    image2_link.short_description = "Image 2"

class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/', null=True, blank=True)
    # image = models.URLField(max_length=200, null=True, blank=True)
    is_breaking_news = models.BooleanField(default=False)
    university = models.ForeignKey(
        'University', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    # created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, null=True, blank=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)  # Fixed typo

    def __str__(self):
        return self.user.email


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

    # ManyToManyField to track followers
    followers = models.ManyToManyField(User, related_name='followed_groups', blank=True)

    def __str__(self):
        return self.name

    @property
    def follower_count(self):
        return self.followers.count()  # Calculate number of followers

    @property
    def admin_username(self):
        return self.admin.username  # Return only the admin's username
    
    @property
    def formatted_created_at(self):
        # Format the created_at datetime field to day/month/year
        return self.created_at.strftime('%d/%m/%Y') if self.created_at else ''



class Message(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, default="Unknown")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages", null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Automatically fetch the username from the related UserProfile
        if not self.username:
            user_profile = UserProfile.objects.get(user=self.userID)
            self.username = user_profile.username or self.userID.username  # Fallback to User's username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.username} in {self.group.name if self.group else 'No Group'}"


class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class Leaders(models.Model):
    names = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='leaders/', null=True, blank=True)
    # image = models.URLField(max_length=200, null=True, blank=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)

    def __str__(self):
        return self.names or "Unnamed Leader"
    
class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'), 
        ('fashion', 'Fashion'),
        ('beauty', 'Beauty'),
        ('health', 'Health'),
        ('cosmetics', 'Cosmetics'),
        ('vehicles', 'Vehicles'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    material_type = models.CharField(max_length=50, choices=PRODUCT_TYPE_CHOICES)
    title = models.CharField(max_length=255, null=True)
    feature1 = models.CharField(max_length=255, null=True, blank=True)
    feature2 = models.CharField(max_length=255, null=True, blank=True)
    feature3 = models.CharField(max_length=255, null=True, blank=True)
    feature4 = models.CharField(max_length=255, null=True, blank=True)
    warranty = models.CharField(max_length=255, null=True, blank=True)
    price = models.CharField(max_length=255, null=True, blank=True)
    is_sold = models.BooleanField(default=False)
    image1 = models.ImageField(upload_to='e-commerce/', null=True, blank=True)
    image2 = models.ImageField(upload_to='e-commerce/', null=True, blank=True)
    image3 = models.ImageField(upload_to='e-commerce/', null=True, blank=True)
    image4 = models.ImageField(upload_to='e-commerce/', null=True, blank=True)

    def get_username(self):
        try:
            return self.user.userprofile.username
        except UserProfile.DoesNotExist:
            return "No username"

    def __str__(self):
        return self.title or "Unnamed Material"

    
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')  # Ensures a user can only follow a group once

    def __str__(self):
        return f'{self.user} follows {self.group}'


class PersonalMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        # Ensure that a message is unique per sender, recipient, and timestamp
        ordering = ['-timestamp']  # Messages ordered by newest first

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

    def save(self, *args, **kwargs):
        # Any additional logic during save (if needed)
        super().save(*args, **kwargs)

class Notification(models.Model):
    title = models.CharField(max_length=255, null=True)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_code}"
    