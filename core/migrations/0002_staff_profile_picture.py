# Generated by Django 5.1.6 on 2025-02-19 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='staff_profiles/'),
        ),
    ]
