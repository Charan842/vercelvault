# Generated manually for drag-and-drop reordering

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storageapp', '0009_remove_userprofile_dark_mode'),
    ]

    operations = [
        # Create new through models
        migrations.CreateModel(
            name='AlbumPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_photos', to='storageapp.album')),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_photos', to='storageapp.photo')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('album', 'photo')},
            },
        ),
        migrations.CreateModel(
            name='AlbumVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_videos', to='storageapp.album')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_videos', to='storageapp.video')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('album', 'video')},
            },
        ),
    ] 