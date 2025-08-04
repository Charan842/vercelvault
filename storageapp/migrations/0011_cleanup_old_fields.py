# Generated manually to clean up old fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storageapp', '0010_album_ordering_models'),
    ]

    operations = [
        # This migration is intentionally empty since the old fields
        # were already removed from the models and the tables don't exist
        # We just need to mark this migration as applied
    ] 