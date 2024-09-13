# Generated by Django 5.1.1 on 2024-09-11 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('event', models.CharField(max_length=63)),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='UserWithAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=24)),
                ('chip_identifier', models.CharField(max_length=255)),
                ('pass_code', models.CharField(max_length=4)),
            ],
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
