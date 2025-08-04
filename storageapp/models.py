from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os
import uuid
from django.conf import settings
from django.urls import reverse

def user_media_path(instance, filename):
    """Generate file path for user media files"""
    return f'users/{instance.user.username}/{instance.__class__.__name__.lower()}s/{filename}'

class Album(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='albums')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='album_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user})"

class AlbumPhoto(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='album_photos')
    photo = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='album_photos')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['album', 'photo']

class AlbumVideo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='album_videos')
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='album_videos')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['album', 'video']

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=user_media_path)
    uploaded_at = models.DateTimeField(default=timezone.now)
    file_size = models.BigIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if self.image:
            self.file_size = self.image.size
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.title or self.image.name}"
    
    class Meta:
        ordering = ['order', '-uploaded_at']

class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to=user_media_path)
    thumbnail = models.ImageField(upload_to=user_media_path, blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    file_size = models.BigIntegerField(default=0)
    duration = models.DurationField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if self.video_file:
            self.file_size = self.video_file.size
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.title or self.video_file.name}"
    
    class Meta:
        ordering = ['order', '-uploaded_at']

class SharedPhoto(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='shares')
    share_token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Shared: {self.photo.title} ({self.share_token})"
    
    def get_share_url(self):
        return f"/shared/photo/{self.share_token}/"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class SharedVideo(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='shares')
    share_token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Shared: {self.video.title} ({self.share_token})"
    
    def get_share_url(self):
        return f"/shared/video/{self.share_token}/"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class SharedAlbum(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='shares')
    share_token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Shared: {self.album.name} ({self.share_token})"
    
    def get_share_url(self):
        return reverse('shared_album', args=[str(self.share_token)])
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    storage_used = models.BigIntegerField(default=0)  # in bytes
    storage_limit = models.BigIntegerField(default=5368709120)  # 5GB default limit
    has_paid_for_extra_storage = models.BooleanField(default=False)
    upgrade_requested = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    gmail = models.EmailField(max_length=254, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_storage_used_mb(self):
        return round(self.storage_used / (1024 * 1024), 2)
    
    def get_storage_limit_mb(self):
        return round(self.storage_limit / (1024 * 1024), 2)
    
    def get_storage_percentage(self):
        return round((self.storage_used / self.storage_limit) * 100, 2)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}..."

class StorageUpgradeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage_upgrade_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='processed_upgrade_requests')
    admin_comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} ({self.created_at:%Y-%m-%d %H:%M})"

class StorageHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage_history')
    date = models.DateField()
    storage_used = models.BigIntegerField()

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['date']
