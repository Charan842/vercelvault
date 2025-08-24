from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse,HttpResponseBase
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from .models import Photo, Video, UserProfile, Notification, StorageUpgradeRequest, Album, AlbumPhoto, AlbumVideo, SharedPhoto, SharedVideo, SharedAlbum, StorageHistory
from .forms import PhotoUploadForm, VideoUploadForm, CustomUserCreationForm, MultiPhotoUploadForm, MultiVideoUploadForm
import os
import io
import zipfile
from django.utils import timezone
from datetime import datetime, timedelta
from django import forms
from django.db import models
import json
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def home(request):
    """Home page with login/signup options"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'storageapp/home.html')

def signup(request):
    """User registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile with phone and gmail
            phone_number = form.cleaned_data.get('phone_number')
            gmail = form.cleaned_data.get('gmail')
            UserProfile.objects.create(user=user, phone_number=phone_number, gmail=gmail)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'storageapp/signup.html', {'form': form})

@login_required
def dashboard(request):
    """User dashboard showing media overview"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Set correct storage limit based on payment status
    if profile.has_paid_for_extra_storage:
        profile.storage_limit = 107374182400  # 100GB
    else:
        profile.storage_limit = 5368709120  # 5GB
    profile.save()
    
    # Get user's media counts
    photo_count = user.photos.count()
    video_count = user.videos.count()
    
    # Get recent media
    recent_photos = user.photos.all()[:6]
    recent_videos = user.videos.all()[:6]
    
    # Calculate storage usage
    total_photo_size = user.photos.aggregate(Sum('file_size'))['file_size__sum'] or 0
    total_video_size = user.videos.aggregate(Sum('file_size'))['file_size__sum'] or 0
    total_storage = total_photo_size + total_video_size
    
    # Update profile storage
    profile.storage_used = total_storage
    profile.save()
    
    unread_notifications = user.notifications.filter(is_read=False).count()
    
    context = {
        'profile': profile,
        'photo_count': photo_count,
        'video_count': video_count,
        'recent_photos': recent_photos,
        'recent_videos': recent_videos,
        'total_storage_mb': round(total_storage / (1024 * 1024), 2),
        'unread_notifications': unread_notifications,
    }
    return render(request, 'storageapp/dashboard.html', context)

@login_required
def photos(request):
    """User's photos page"""
    photos_list = request.user.photos.all()
    paginator = Paginator(photos_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'photos': page_obj,
    }
    return render(request, 'storageapp/photos.html', context)

@login_required
def photos_ajax(request):
    """AJAX endpoint for infinite scroll photos"""
    photos_list = request.user.photos.all()
    paginator = Paginator(photos_list, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    photos_data = []
    for photo in page_obj:
        # Format file size
        if photo.file_size < 1024:
            file_size_formatted = f"{photo.file_size} B"
        elif photo.file_size < 1024 * 1024:
            file_size_formatted = f"{photo.file_size / 1024:.1f} KB"
        elif photo.file_size < 1024 * 1024 * 1024:
            file_size_formatted = f"{photo.file_size / (1024 * 1024):.1f} MB"
        else:
            file_size_formatted = f"{photo.file_size / (1024 * 1024 * 1024):.1f} GB"
        
        photos_data.append({
            'id': photo.id,
            'title': photo.title or 'Untitled',
            'image_url': photo.image.url,
            'uploaded_at': photo.uploaded_at.strftime('%b %d, %Y'),
            'file_size': photo.file_size,
            'file_size_formatted': file_size_formatted,
        })
    
    return JsonResponse({
        'photos': photos_data,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'current_page': page_obj.number,
    })

@login_required
def videos(request):
    """User's videos page with sorting and filtering"""
    sort = request.GET.get('sort', 'newest')
    date_filter = request.GET.get('filter', 'all')
    videos_list = request.user.videos.all()
    now = timezone.now()
    if date_filter == 'month':
        videos_list = videos_list.filter(uploaded_at__year=now.year, uploaded_at__month=now.month)
    elif date_filter == 'year':
        videos_list = videos_list.filter(uploaded_at__year=now.year)
    if sort == 'newest':
        videos_list = videos_list.order_by('-uploaded_at')
    elif sort == 'oldest':
        videos_list = videos_list.order_by('uploaded_at')
    elif sort == 'largest':
        videos_list = videos_list.order_by('-file_size')
    elif sort == 'smallest':
        videos_list = videos_list.order_by('file_size')
    elif sort == 'title_az':
        videos_list = videos_list.order_by('title')
    elif sort == 'title_za':
        videos_list = videos_list.order_by('-title')
    paginator = Paginator(videos_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'videos': page_obj,
        'sort': sort,
        'date_filter': date_filter,
    }
    return render(request, 'storageapp/videos.html', context)

@login_required
def videos_ajax(request):
    """AJAX endpoint for infinite scroll videos"""
    sort = request.GET.get('sort', 'newest')
    date_filter = request.GET.get('filter', 'all')
    videos_list = request.user.videos.all()
    now = timezone.now()
    
    if date_filter == 'month':
        videos_list = videos_list.filter(uploaded_at__year=now.year, uploaded_at__month=now.month)
    elif date_filter == 'year':
        videos_list = videos_list.filter(uploaded_at__year=now.year)
    
    if sort == 'newest':
        videos_list = videos_list.order_by('-uploaded_at')
    elif sort == 'oldest':
        videos_list = videos_list.order_by('uploaded_at')
    elif sort == 'largest':
        videos_list = videos_list.order_by('-file_size')
    elif sort == 'smallest':
        videos_list = videos_list.order_by('file_size')
    elif sort == 'title_az':
        videos_list = videos_list.order_by('title')
    elif sort == 'title_za':
        videos_list = videos_list.order_by('-title')
    
    paginator = Paginator(videos_list, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    videos_data = []
    for video in page_obj:
        # Format file size
        if video.file_size < 1024:
            file_size_formatted = f"{video.file_size} B"
        elif video.file_size < 1024 * 1024:
            file_size_formatted = f"{video.file_size / 1024:.1f} KB"
        elif video.file_size < 1024 * 1024 * 1024:
            file_size_formatted = f"{video.file_size / (1024 * 1024):.1f} MB"
        else:
            file_size_formatted = f"{video.file_size / (1024 * 1024 * 1024):.1f} GB"
        
        videos_data.append({
            'id': video.id,
            'title': video.title or 'Untitled',
            'thumbnail_url': video.thumbnail.url if video.thumbnail else None,
            'uploaded_at': video.uploaded_at.strftime('%b %d, %Y'),
            'file_size': video.file_size,
            'file_size_formatted': file_size_formatted,
            'duration': video.duration.strftime('%H:%M:%S') if video.duration else None,
        })
    
    return JsonResponse({
        'videos': videos_data,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'current_page': page_obj.number,
    })

@login_required
def upload_photo(request):
    """Upload photo form with storage restriction and both single/multiple upload support"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.has_paid_for_extra_storage and profile.storage_used >= 1073741824:
        messages.warning(request, 'You have reached your free 1GB storage limit. Please upgrade to upload more.')
        return redirect('pay_for_extra_storage')
    single_form = PhotoUploadForm(user=request.user)
    multi_form = MultiPhotoUploadForm(user=request.user)
    max_photo_size = 100 * 1024 * 1024  # 100MB
    if request.method == 'POST':
        if 'single_upload' in request.POST:
            single_form = PhotoUploadForm(request.POST, request.FILES, user=request.user)
            if single_form.is_valid():
                image = request.FILES.get('image')
                if image:
                    if image.size > max_photo_size:
                        messages.error(request, 'Photo is too large. Maximum allowed size is 100MB.')
                    elif not image.content_type.startswith('image/'):
                        messages.error(request, 'Unsupported file type. Please upload an image file.')
                    else:
                        photo = single_form.save(commit=False)
                        photo.user = request.user
                        photo.save()
                        single_form.save_m2m()  # Save albums
                        messages.success(request, 'Photo uploaded successfully!')
                        return redirect('photos')
        elif 'multi_upload' in request.POST:
            multi_form = MultiPhotoUploadForm(request.POST, user=request.user)
            if multi_form.is_valid():
                images = request.FILES.getlist('images')
                title = multi_form.cleaned_data.get('title')
                description = multi_form.cleaned_data.get('description')
                albums = multi_form.cleaned_data.get('albums')
                if not images:
                    messages.error(request, 'Please select at least one photo to upload.')
                else:
                    errors = 0
                    for image in images:
                        if image.size > max_photo_size:
                            messages.error(request, f'Photo {image.name} is too large. Maximum allowed size is 100MB.')
                            errors += 1
                        elif not image.content_type.startswith('image/'):
                            messages.error(request, f'File {image.name} is not a supported image type.')
                            errors += 1
                        else:
                            photo = Photo.objects.create(user=request.user, image=image, title=title, description=description)
                            if albums:
                                photo.albums.set(albums)
                    if errors == 0:
                        messages.success(request, f'{len(images)} photo(s) uploaded successfully!')
                        return redirect('photos')
    return render(request, 'storageapp/upload_photo.html', {'single_form': single_form, 'multi_form': multi_form})

@login_required
def upload_video(request):
    """Upload video form with storage restriction and both single/multiple upload support"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.has_paid_for_extra_storage and profile.storage_used >= 1073741824:
        messages.warning(request, 'You have reached your free 1GB storage limit. Please upgrade to upload more.')
        return redirect('pay_for_extra_storage')
    single_form = VideoUploadForm(user=request.user)
    multi_form = MultiVideoUploadForm(user=request.user)
    max_video_size = 1000 * 1024 * 1024  # 1000MB
    if request.method == 'POST':
        if 'single_upload' in request.POST:
            single_form = VideoUploadForm(request.POST, request.FILES, user=request.user)
            if single_form.is_valid():
                video_file = request.FILES.get('video_file')
                if video_file:
                    if video_file.size > max_video_size:
                        messages.error(request, 'Video is too large. Maximum allowed size is 1000MB.')
                    elif not video_file.content_type.startswith('video/'):
                        messages.error(request, 'Unsupported file type. Please upload a video file.')
                    else:
                        video = single_form.save(commit=False)
                        video.user = request.user
                        video.save()
                        single_form.save_m2m()  # Save albums
                        messages.success(request, 'Video uploaded successfully!')
                        return redirect('videos')
        elif 'multi_upload' in request.POST:
            multi_form = MultiVideoUploadForm(request.POST, user=request.user)
            if multi_form.is_valid():
                videos = request.FILES.getlist('videos')
                title = multi_form.cleaned_data.get('title')
                description = multi_form.cleaned_data.get('description')
                albums = multi_form.cleaned_data.get('albums')
                if not videos:
                    messages.error(request, 'Please select at least one video to upload.')
                else:
                    errors = 0
                    for video_file in videos:
                        if video_file.size > max_video_size:
                            messages.error(request, f'Video {video_file.name} is too large. Maximum allowed size is 1000MB.')
                            errors += 1
                        elif not video_file.content_type.startswith('video/'):
                            messages.error(request, f'File {video_file.name} is not a supported video type.')
                            errors += 1
                        else:
                            video = Video.objects.create(user=request.user, video_file=video_file, title=title, description=description)
                            if albums:
                                video.albums.set(albums)
                    if errors == 0:
                        messages.success(request, f'{len(videos)} video(s) uploaded successfully!')
                        return redirect('videos')
    return render(request, 'storageapp/upload_video.html', {'single_form': single_form, 'multi_form': multi_form})

@login_required
def photo_detail(request, photo_id):
    """Photo detail page"""
    photo = get_object_or_404(Photo, id=photo_id, user=request.user)
    active_share = photo.shares.filter(is_active=True).first()
    is_shared = active_share is not None
    share_url = request.build_absolute_uri(active_share.get_share_url()) if is_shared else ''
    
    context = {
        'photo': photo,
        'is_shared': is_shared,
        'share_url': share_url,
    }
    return render(request, 'storageapp/photo_detail.html', context)

@login_required
def video_detail(request, video_id):
    """View individual video"""
    video = get_object_or_404(Video, id=video_id, user=request.user)
    active_share = video.shares.filter(is_active=True).first()
    is_shared = active_share is not None
    share_url = request.build_absolute_uri(active_share.get_share_url()) if is_shared else ''

    context = {
        'video': video,
        'is_shared': is_shared,
        'share_url': share_url,
    }
    return render(request, 'storageapp/video_detail.html', context)

@login_required
@require_POST
def delete_photo(request, photo_id):
    """Delete photo"""
    photo = get_object_or_404(Photo, id=photo_id, user=request.user)
    
    # Delete file from storage
    if photo.image:
        if os.path.isfile(photo.image.path):
            os.remove(photo.image.path)
    
    photo.delete()
    messages.success(request, 'Photo deleted successfully!')
    return redirect('photos')

@login_required
def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    try:
        # Delete files from storage
        if video.video_file and hasattr(video.video_file, 'path'):
            os.remove(video.video_file.path)
        if video.thumbnail and hasattr(video.thumbnail, 'path'):
            os.remove(video.thumbnail.path)
        video.delete()
        messages.success(request, 'Video deleted successfully!')
    except PermissionError as e:
        if getattr(e, 'winerror', None) == 32:
            messages.error(request, 'Cannot delete the video file because it is currently in use. Please close any programs using it and try again.')
        else:
            messages.error(request, f'Error deleting video: {e}')
    except Exception as e:
        messages.error(request, f'Error deleting video: {e}')
    return redirect('videos')

@login_required
@require_POST
def delete_notification(request, notification_id):
    notification = Notification.objects.filter(id=notification_id, user=request.user).first()
    if not notification:
        return HttpResponseForbidden()
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'Notification deleted.')
    return redirect('notifications')

@login_required
def search_media(request):
    """Search through user's media"""
    query = request.GET.get('q', '')
    media_type = request.GET.get('type', 'all')
    
    photos = []
    videos = []
    
    if query:
        if media_type in ['all', 'photos']:
            photos = request.user.photos.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        if media_type in ['all', 'videos']:
            videos = request.user.videos.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
    
    context = {
        'query': query,
        'media_type': media_type,
        'photos': photos,
        'videos': videos,
    }
    return render(request, 'storageapp/search.html', context)

@login_required
def pay_for_extra_storage(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    existing_request = StorageUpgradeRequest.objects.filter(user=request.user, status='pending').first()
    if request.method == 'POST' and not existing_request:
        StorageUpgradeRequest.objects.create(user=request.user)
        messages.info(request, 'Your upgrade request has been sent to the admin for approval. You will be notified once approved.')
        return redirect('dashboard')
    # Show the latest request status if exists
    latest_request = StorageUpgradeRequest.objects.filter(user=request.user).order_by('-created_at').first()
    request_history = StorageUpgradeRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'storageapp/payment.html', {'profile': profile, 'upgrade_request': latest_request, 'request_history': request_history})

@login_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'storageapp/profile.html', {'profile': profile})

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark all as read when visiting the page
    user_notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'storageapp/notifications.html', {'notifications': user_notifications})

@login_required
def delete_photos(request):
    if request.method == 'POST':
        photo_ids = request.POST.getlist('photo_ids')
        photos = Photo.objects.filter(id__in=photo_ids, user=request.user)
        deleted_count = 0
        for photo in photos:
            if photo.image and hasattr(photo.image, 'path'):
                try:
                    os.remove(photo.image.path)
                except Exception:
                    pass
            photo.delete()
            deleted_count += 1
        messages.success(request, f'{deleted_count} photo(s) deleted successfully!')
    return redirect('photos')

@login_required
def download_photos(request):
    if request.method == 'POST':
        photo_ids = request.POST.getlist('photo_ids')
        photos = Photo.objects.filter(id__in=photo_ids, user=request.user)
        if not photos:
            messages.error(request, 'No photos selected for download.')
            return redirect('photos')
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for photo in photos:
                if photo.image and hasattr(photo.image, 'path') and photo.image.storage.exists(photo.image.name):
                    with photo.image.open('rb') as f:
                        file_data = f.read()
                        file_name = photo.image.name.split('/')[-1]
                        zip_file.writestr(file_name, file_data)
        zip_buffer.seek(0)
        today_str = datetime.now().strftime('%Y%m%d')
        zip_filename = f"{request.user.username}_photos_{today_str}.zip"
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response
    return redirect('photos')

@login_required
def delete_videos(request):
    if request.method == 'POST':
        video_ids = request.POST.getlist('video_ids')
        videos = Video.objects.filter(id__in=video_ids, user=request.user)
        deleted_count = 0
        failed_count = 0
        for video in videos:
            try:
                if video.video_file and hasattr(video.video_file, 'path'):
                    os.remove(video.video_file.path)
                if video.thumbnail and hasattr(video.thumbnail, 'path'):
                    os.remove(video.thumbnail.path)
                video.delete()
                deleted_count += 1
            except PermissionError as e:
                if getattr(e, 'winerror', None) == 32:
                    failed_count += 1
                else:
                    messages.error(request, f'Error deleting video: {e}')
            except Exception as e:
                messages.error(request, f'Error deleting video: {e}')
        if deleted_count:
            messages.success(request, f'{deleted_count} video(s) deleted successfully!')
        if failed_count:
            messages.error(request, f"{failed_count} video(s) could not be deleted because they are currently in use. Please close any programs using them and try again.")
    return redirect('videos')

@login_required
def download_videos(request):
    if request.method == 'POST':
        video_ids = request.POST.getlist('video_ids')
        videos = Video.objects.filter(id__in=video_ids, user=request.user)
        if not videos:
            messages.error(request, 'No videos selected for download.')
            return redirect('videos')
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for video in videos:
                if video.video_file and hasattr(video.video_file, 'path') and video.video_file.storage.exists(video.video_file.name):
                    with video.video_file.open('rb') as f:
                        file_data = f.read()
                        file_name = video.video_file.name.split('/')[-1]
                        zip_file.writestr(file_name, file_data)
        zip_buffer.seek(0)
        today_str = datetime.now().strftime('%Y%m%d')
        zip_filename = f"{request.user.username}_videos_{today_str}.zip"
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response
    return redirect('videos')

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['name', 'description', 'cover_image']

@login_required
def album_list(request):
    albums = Album.objects.filter(user=request.user)
    return render(request, 'storageapp/album_list.html', {'albums': albums})

@login_required
def album_create(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.save()
            form.save_m2m()
            
            # Handle bulk photo assignment
            photo_ids = request.POST.get('photo_ids')
            if photo_ids:
                ids = [int(pk) for pk in photo_ids.split(',') if pk.isdigit()]
                photos = Photo.objects.filter(id__in=ids, user=request.user)
                for index, photo in enumerate(photos):
                    AlbumPhoto.objects.create(album=album, photo=photo, order=index)
            
            # Handle bulk video assignment
            video_ids = request.POST.get('video_ids')
            if video_ids:
                ids = [int(pk) for pk in video_ids.split(',') if pk.isdigit()]
                videos = Video.objects.filter(id__in=ids, user=request.user)
                for index, video in enumerate(videos):
                    AlbumVideo.objects.create(album=album, video=video, order=index)
            
            return redirect('album_detail', album_id=album.id)
    else:
        form = AlbumForm()
    return render(request, 'storageapp/album_form.html', {'form': form})

@login_required
def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    photos = Photo.objects.filter(album_photos__album=album).order_by('album_photos__order')
    videos = Video.objects.filter(album_videos__album=album).order_by('album_videos__order')
    active_share = album.shares.filter(is_active=True).first()
    is_shared = active_share is not None
    share_url = request.build_absolute_uri(active_share.get_share_url()) if is_shared else ''

    return render(request, 'storageapp/album_detail.html', {
        'album': album, 
        'photos': photos, 
        'videos': videos,
        'is_shared': is_shared,
        'share_url': share_url,
    })

@login_required
def album_edit(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            form.save()
            messages.success(request, 'Album updated successfully!')
            return redirect('album_detail', album_id=album.id)
    else:
        form = AlbumForm(instance=album)
    return render(request, 'storageapp/album_form.html', {'form': form, 'album': album, 'edit_mode': True})

@login_required
def album_delete(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    if request.method == 'POST':
        album.delete()
        messages.success(request, 'Album deleted successfully!')
        return redirect('album_list')
    return render(request, 'storageapp/album_confirm_delete.html', {'album': album})

@login_required
def album_edit_contents(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    user_photos = Photo.objects.filter(user=request.user)
    user_videos = Video.objects.filter(user=request.user)
    
    if request.method == 'POST':
        photo_ids = request.POST.getlist('photo_ids')
        video_ids = request.POST.getlist('video_ids')
        
        # Clear existing relationships
        AlbumPhoto.objects.filter(album=album).delete()
        AlbumVideo.objects.filter(album=album).delete()
        
        # Add photos with order
        for index, photo_id in enumerate(photo_ids):
            try:
                photo = Photo.objects.get(id=photo_id, user=request.user)
                AlbumPhoto.objects.create(album=album, photo=photo, order=index)
            except Photo.DoesNotExist:
                pass
        
        # Add videos with order
        for index, video_id in enumerate(video_ids):
            try:
                video = Video.objects.get(id=video_id, user=request.user)
                AlbumVideo.objects.create(album=album, video=video, order=index)
            except Video.DoesNotExist:
                pass
        
        messages.success(request, 'Album contents updated!')
        return redirect('album_detail', album_id=album.id)
    else:
        selected_photo_ids = album.album_photos.values_list('photo_id', flat=True)
        selected_video_ids = album.album_videos.values_list('video_id', flat=True)
    
    return render(request, 'storageapp/album_edit_contents.html', {
        'album': album,
        'photos': user_photos,
        'videos': user_videos,
        'selected_photo_ids': selected_photo_ids,
        'selected_video_ids': selected_video_ids,
    })

@login_required
@require_POST
def reorder_album_media(request, album_id):
    """Handle drag-and-drop reordering of photos and videos in albums"""
    album = get_object_or_404(Album, id=album_id, user=request.user)
    
    try:
        data = request.POST
        media_type = data.get('type')  # 'photo' or 'video'
        media_id = data.get('id')
        new_order = int(data.get('order', 0))
        
        if media_type == 'photo':
            # Update photo order
            album_photo = AlbumPhoto.objects.get(album=album, photo_id=media_id)
            old_order = album_photo.order
            
            if new_order > old_order:
                # Moving down - shift others up
                AlbumPhoto.objects.filter(
                    album=album, 
                    order__gt=old_order, 
                    order__lte=new_order
                ).update(order=models.F('order') - 1)
            else:
                # Moving up - shift others down
                AlbumPhoto.objects.filter(
                    album=album, 
                    order__gte=new_order, 
                    order__lt=old_order
                ).update(order=models.F('order') + 1)
            
            album_photo.order = new_order
            album_photo.save()
            
        elif media_type == 'video':
            # Update video order
            album_video = AlbumVideo.objects.get(album=album, video_id=media_id)
            old_order = album_video.order
            
            if new_order > old_order:
                # Moving down - shift others up
                AlbumVideo.objects.filter(
                    album=album, 
                    order__gt=old_order, 
                    order__lte=new_order
                ).update(order=models.F('order') - 1)
            else:
                # Moving up - shift others down
                AlbumVideo.objects.filter(
                    album=album, 
                    order__gte=new_order, 
                    order__lt=old_order
                ).update(order=models.F('order') + 1)
            
            album_video.order = new_order
            album_video.save()
        
        return JsonResponse({'success': True})
        
    except (AlbumPhoto.DoesNotExist, AlbumVideo.DoesNotExist, ValueError, KeyError) as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def reorder_photos(request):
    """Handle drag-and-drop reordering of photos"""
    try:
        data = request.POST
        photo_id = data.get('id')
        new_order = int(data.get('order', 0))
        
        photo = Photo.objects.get(id=photo_id, user=request.user)
        old_order = photo.order
        
        if new_order > old_order:
            # Moving down - shift others up
            Photo.objects.filter(
                user=request.user,
                order__gt=old_order, 
                order__lte=new_order
            ).update(order=models.F('order') - 1)
        else:
            # Moving up - shift others down
            Photo.objects.filter(
                user=request.user,
                order__gte=new_order, 
                order__lt=old_order
            ).update(order=models.F('order') + 1)
        
        photo.order = new_order
        photo.save()
        
        return JsonResponse({'success': True})
        
    except (Photo.DoesNotExist, ValueError, KeyError) as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def reorder_videos(request):
    """Handle drag-and-drop reordering of videos"""
    try:
        data = request.POST
        video_id = data.get('id')
        new_order = int(data.get('order', 0))
        
        video = Video.objects.get(id=video_id, user=request.user)
        old_order = video.order
        
        if new_order > old_order:
            # Moving down - shift others up
            Video.objects.filter(
                user=request.user,
                order__gt=old_order, 
                order__lte=new_order
            ).update(order=models.F('order') - 1)
        else:
            # Moving up - shift others down
            Video.objects.filter(
                user=request.user,
                order__gte=new_order, 
                order__lt=old_order
            ).update(order=models.F('order') + 1)
        
        video.order = new_order
        video.save()
        
        return JsonResponse({'success': True})
        
    except (Video.DoesNotExist, ValueError, KeyError) as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def share_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id, user=request.user)
    shared, created = SharedPhoto.objects.get_or_create(photo=photo, is_active=True)
    if not created and shared.is_expired():
        shared.is_active = True
        shared.expires_at = None
        shared.save()
    share_url = request.build_absolute_uri(shared.get_share_url())
    return JsonResponse({'success': True, 'share_url': share_url})

@login_required
@require_POST
def unshare_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id, user=request.user)
    SharedPhoto.objects.filter(photo=photo, is_active=True).update(is_active=False)
    return JsonResponse({'success': True})

def shared_photo(request, token):
    shared = get_object_or_404(SharedPhoto, share_token=token, is_active=True)
    if shared.is_expired():
        return render(request, 'storageapp/shared_expired.html')
    return render(request, 'storageapp/shared_photo.html', {'photo': shared.photo})

@login_required
@require_POST
def share_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    shared, created = SharedVideo.objects.get_or_create(video=video, is_active=True)
    if not created and shared.is_expired():
        shared.is_active = True
        shared.expires_at = None
        shared.save()
    share_url = request.build_absolute_uri(shared.get_share_url())
    return JsonResponse({'success': True, 'share_url': share_url})

@login_required
@require_POST
def unshare_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    SharedVideo.objects.filter(video=video, is_active=True).update(is_active=False)
    return JsonResponse({'success': True})

def shared_video(request, token):
    shared = get_object_or_404(SharedVideo, share_token=token, is_active=True)
    if shared.is_expired():
        return render(request, 'storageapp/shared_expired.html')
    return render(request, 'storageapp/shared_video.html', {'video': shared.video})

@login_required
@require_POST
def share_album(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    shared, created = SharedAlbum.objects.get_or_create(album=album, is_active=True)
    if not created and shared.is_expired():
        shared.is_active = True
        shared.expires_at = None
        shared.save()
    share_url = request.build_absolute_uri(shared.get_share_url())
    return JsonResponse({'success': True, 'share_url': share_url})

@login_required
@require_POST
def unshare_album(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    SharedAlbum.objects.filter(album=album, is_active=True).update(is_active=False)
    return JsonResponse({'success': True})

def shared_album(request, token):
    shared = get_object_or_404(SharedAlbum, share_token=token, is_active=True)
    if shared.is_expired():
        return render(request, 'storageapp/shared_expired.html')
    
    album = shared.album
    photos = Photo.objects.filter(album_photos__album=album).order_by('album_photos__order')
    videos = Video.objects.filter(album_videos__album=album).order_by('album_videos__order')

    return render(request, 'storageapp/shared_album.html', {
        'album': album,
        'photos': photos,
        'videos': videos
    })

@login_required
def storage_analytics(request):
    """Storage analytics page with charts"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get date range (last 30 days by default)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get storage history data
    storage_history = StorageHistory.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Prepare data for chart
    dates = []
    storage_values = []
    
    for record in storage_history:
        dates.append(record.date.strftime('%Y-%m-%d'))
        storage_values.append(round(record.storage_used / (1024 * 1024), 2))  # Convert to MB
    
    # If no history data, create some sample data
    if not storage_history.exists():
        # Create sample data based on current storage
        current_storage = profile.storage_used / (1024 * 1024)  # MB
        for i in range(30):
            date = start_date + timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
            # Add some variation to make it look realistic
            variation = current_storage * (0.8 + 0.4 * (i / 30))  # Gradual increase
            storage_values.append(round(variation, 2))
    
    storage_limit_mb = profile.get_storage_limit_mb()
    storage_used_mb = profile.get_storage_used_mb()
    available_storage_mb = storage_limit_mb - storage_used_mb
    if available_storage_mb < 0:
        available_storage_mb = 0
    
    context = {
        'profile': profile,
        'dates': json.dumps(dates),
        'storage_values': json.dumps(storage_values),
        'storage_limit_mb': storage_limit_mb,
        'storage_used_mb': storage_used_mb,
        'available_storage_mb': available_storage_mb,
        'storage_percentage': profile.get_storage_percentage(),
    }
    
    return render(request, 'storageapp/storage_analytics.html', context)
