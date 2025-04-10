from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='dean',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='courses', to='core.dean'),
        ),
    ]
