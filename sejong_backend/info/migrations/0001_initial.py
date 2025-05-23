# Generated by Django 5.1.8 on 2025-05-10 07:40

import django_mongodb_backend.fields
import gdstorage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AnnouncementImage",
            fields=[
                (
                    "id",
                    django_mongodb_backend.fields.ObjectIdAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(help_text="Image title", max_length=200)),
                (
                    "image",
                    models.ImageField(
                        help_text="Image file",
                        storage=gdstorage.storage.GoogleDriveStorage(),
                        upload_to="sejong/announcements",
                    ),
                ),
                (
                    "google_drive_file_id",
                    models.CharField(
                        blank=True,
                        help_text="Google Drive file Id",
                        max_length=100,
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Counter",
            fields=[
                (
                    "id",
                    django_mongodb_backend.fields.ObjectIdAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("collection_name", models.CharField(max_length=100, unique=True)),
                ("current_id", models.IntegerField(default=0)),
            ],
            options={
                "db_table": "counters",
            },
        ),
        migrations.CreateModel(
            name="TimeSlot",
            fields=[
                (
                    "id",
                    django_mongodb_backend.fields.ObjectIdAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "day",
                    models.IntegerField(
                        choices=[
                            (0, "Monday"),
                            (1, "Tuesday"),
                            (2, "Wednesday"),
                            (3, "Thursday"),
                            (4, "Friday"),
                            (5, "Saturday"),
                            (6, "Sunday"),
                        ]
                    ),
                ),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                (
                    "classroom",
                    models.IntegerField(
                        choices=[
                            (301, 301),
                            (303, 303),
                            (306, 306),
                            (307, 307),
                            (308, 308),
                        ]
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Announcement",
            fields=[
                (
                    "id",
                    django_mongodb_backend.fields.ObjectIdAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("custom_id", models.IntegerField(blank=True, null=True, unique=True)),
                (
                    "title",
                    models.CharField(help_text="Announcement title", max_length=200),
                ),
                ("content", models.TextField(help_text="Announcement content")),
                (
                    "images",
                    models.JSONField(
                        blank=True, help_text="Serialized images", null=True
                    ),
                ),
                (
                    "time_posted",
                    models.DateTimeField(
                        auto_now_add=True, help_text="Date of announcement"
                    ),
                ),
                (
                    "author",
                    models.CharField(
                        help_text="Author of the announcement", max_length=100
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, help_text="Is the announcement active?"
                    ),
                ),
                (
                    "images_many_to_many",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Images related to the announcement",
                        to="info.announcementimage",
                    ),
                ),
            ],
            options={
                "db_table": "announcements",
            },
        ),
        migrations.CreateModel(
            name="Schedule",
            fields=[
                (
                    "id",
                    django_mongodb_backend.fields.ObjectIdAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("group", models.CharField(help_text="Group name", max_length=50)),
                (
                    "time",
                    models.JSONField(
                        blank=True, help_text="Serialized time slots", null=True
                    ),
                ),
                ("teacher", models.CharField(help_text="Teacher name", max_length=100)),
                (
                    "book",
                    models.IntegerField(
                        choices=[
                            (1, "1"),
                            (2, "2"),
                            (3, "3"),
                            (4, "4"),
                            (5, "5"),
                            (6, "6"),
                            (7, "7"),
                            (8, "8"),
                        ],
                        help_text="Book number (from 1 to 8)",
                    ),
                ),
                (
                    "time_many_to_many",
                    models.ManyToManyField(
                        help_text="Time slots for the schedule", to="info.timeslot"
                    ),
                ),
            ],
            options={
                "db_table": "schedules",
            },
        ),
    ]
