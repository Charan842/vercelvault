from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Photo, Video, UserProfile, Notification, StorageUpgradeRequest, Album, AlbumPhoto, AlbumVideo
from django.utils import timezone

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'uploaded_at', 'file_size', 'get_file_size_mb')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('uploaded_at', 'file_size')
    
    def get_file_size_mb(self, obj):
        return f"{round(obj.file_size / (1024 * 1024), 2)} MB"
    get_file_size_mb.short_description = 'File Size (MB)'

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'uploaded_at', 'file_size', 'get_file_size_mb', 'duration')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('uploaded_at', 'file_size')
    
    def get_file_size_mb(self, obj):
        return f"{round(obj.file_size / (1024 * 1024), 2)} MB"
    get_file_size_mb.short_description = 'File Size (MB)'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gmail', 'storage_used', 'storage_limit', 'get_storage_percentage', 'has_paid_for_extra_storage', 'upgrade_requested')
    readonly_fields = ('storage_used',)
    list_filter = ('has_paid_for_extra_storage', 'upgrade_requested')
    actions = ['approve_upgrade', 'disapprove_upgrade']
    search_fields = ('user__username', 'phone_number', 'gmail')
    
    def get_storage_percentage(self, obj):
        return f"{obj.get_storage_percentage()}%"
    get_storage_percentage.short_description = 'Storage Used (%)'

    def approve_upgrade(self, request, queryset):
        updated = queryset.update(has_paid_for_extra_storage=True, upgrade_requested=False)
        self.message_user(request, f"{updated} user(s) have been approved for extra storage.")
    approve_upgrade.short_description = 'Approve selected upgrade requests'

    def disapprove_upgrade(self, request, queryset):
        updated = queryset.update(upgrade_requested=False)
        for profile in queryset:
            Notification.objects.create(
                user=profile.user,
                message='Your request to expand storage to 5GB was disapproved by the admin.'
            )
        self.message_user(request, f"{updated} user(s) have been disapproved for extra storage.")
    disapprove_upgrade.short_description = 'Disapprove selected upgrade requests'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']

@admin.register(StorageUpgradeRequest)
class StorageUpgradeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'processed_at', 'processed_by', 'admin_comment')
    list_filter = ('status',)
    search_fields = ('user__username',)
    actions = ['approve_request', 'deny_request']

    def approve_request(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.status = 'approved'
            req.processed_at = timezone.now()
            req.processed_by = request.user
            req.save()
            # Grant storage
            profile = UserProfile.objects.get(user=req.user)
            profile.has_paid_for_extra_storage = True
            profile.upgrade_requested = False
            profile.save()
            Notification.objects.create(user=req.user, message='Your storage upgrade request was approved!')
        self.message_user(request, f"{queryset.filter(status='pending').count()} request(s) approved.")
    approve_request.short_description = 'Approve selected storage upgrade requests'

    def deny_request(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.status = 'denied'
            req.processed_at = timezone.now()
            req.processed_by = request.user
            req.save()
            Notification.objects.create(user=req.user, message='Your storage upgrade request was denied.')
        self.message_user(request, f"{queryset.filter(status='pending').count()} request(s) denied.")
    deny_request.short_description = 'Deny selected storage upgrade requests'

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'photo_count', 'video_count']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username']
    
    def photo_count(self, obj):
        return obj.album_photos.count()
    photo_count.short_description = 'Photos'
    
    def video_count(self, obj):
        return obj.album_videos.count()
    video_count.short_description = 'Videos'

@admin.register(AlbumPhoto)
class AlbumPhotoAdmin(admin.ModelAdmin):
    list_display = ['album', 'photo', 'order']
    list_filter = ['album', 'order']
    search_fields = ['album__name', 'photo__title']

@admin.register(AlbumVideo)
class AlbumVideoAdmin(admin.ModelAdmin):
    list_display = ['album', 'video', 'order']
    list_filter = ['album', 'order']
    search_fields = ['album__name', 'video__title']
