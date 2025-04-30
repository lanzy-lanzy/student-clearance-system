from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_year', models.CharField(help_text='Current school year in format YYYY-YYYY', max_length=9)),
                ('semester', models.CharField(choices=[('1ST_MID', '1st Sem - Midterm'), ('1ST_FIN', '1st Sem - Final'), ('2ND_MID', '2nd Sem - Midterm'), ('2ND_FIN', '2nd Sem - Final'), ('SUM', 'Summer')], help_text='Current semester', max_length=7)),
                ('clearance_active', models.BooleanField(default=False, help_text='Whether clearance requests are currently active')),
                ('maintenance_mode', models.BooleanField(default=False, help_text='Whether the system is in maintenance mode')),
                ('email_notifications', models.BooleanField(default=True, help_text='Whether email notifications are enabled')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'verbose_name': 'System Settings',
                'verbose_name_plural': 'System Settings',
            },
        ),
    ]
