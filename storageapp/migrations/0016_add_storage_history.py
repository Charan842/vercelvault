# Generated manually for StorageHistory model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storageapp', '0015_auto_20250621_1427'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StorageHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('storage_used', models.BigIntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='storage_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
                'unique_together': {('user', 'date')},
            },
        ),
    ] 