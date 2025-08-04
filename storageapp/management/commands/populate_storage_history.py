from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from storageapp.models import StorageHistory, Photo, Video
from django.db.models import Sum


class Command(BaseCommand):
    help = 'Populate storage history for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of history to generate (default: 30)'
        )

    def handle(self, *args, **options):
        days = options['days']
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        self.stdout.write(f'Generating storage history for the last {days} days...')
        
        users = User.objects.all()
        total_records = 0
        
        for user in users:
            self.stdout.write(f'Processing user: {user.username}')
            
            # Get user's photos and videos
            photos = Photo.objects.filter(user=user)
            videos = Video.objects.filter(user=user)
            
            # Calculate storage for each day
            current_date = start_date
            while current_date <= end_date:
                # Calculate storage used on this date
                # For simplicity, we'll use the current storage usage
                # In a real scenario, you might want to track file creation dates
                storage_used = 0
                
                # Add storage from photos
                photos_storage = photos.aggregate(total=Sum('file_size'))['total'] or 0
                storage_used += photos_storage
                
                # Add storage from videos
                videos_storage = videos.aggregate(total=Sum('file_size'))['total'] or 0
                storage_used += videos_storage
                
                # Create or update storage history record
                storage_history, created = StorageHistory.objects.get_or_create(
                    user=user,
                    date=current_date,
                    defaults={'storage_used': storage_used}
                )
                
                if not created:
                    storage_history.storage_used = storage_used
                    storage_history.save()
                
                total_records += 1
                current_date += timedelta(days=1)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created/updated {total_records} storage history records'
            )
        ) 