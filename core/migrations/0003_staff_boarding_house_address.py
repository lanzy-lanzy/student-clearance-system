from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_student_boarder_since'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='boarding_house_address',
            field=models.TextField(blank=True, null=True, verbose_name='Boarding House Address'),
        ),
    ]
