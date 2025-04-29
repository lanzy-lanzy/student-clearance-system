from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='boarder_since',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date Started as a Boarder'),
        ),
    ]
