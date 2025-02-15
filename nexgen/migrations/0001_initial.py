# Generated by Django 5.1.6 on 2025-02-15 06:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('ChatID', models.AutoField(primary_key=True, serialize=False)),
                ('Title', models.CharField(max_length=255)),
                ('CreatedAt', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('ChatMessageID', models.AutoField(primary_key=True, serialize=False)),
                ('Message', models.TextField()),
                ('CreatedAt', models.DateTimeField(auto_now_add=True)),
                ('HumanFlag', models.BooleanField(default=True)),
                ('ChatID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='nexgen.chat')),
            ],
        ),
    ]
