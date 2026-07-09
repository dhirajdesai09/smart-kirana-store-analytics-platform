from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Store",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("business_type", models.CharField(default="Kirana / Grocery", max_length=120)),
                ("gstin", models.CharField(blank=True, max_length=20)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("address", models.TextField(blank=True)),
                ("city", models.CharField(blank=True, max_length=80)),
                ("state", models.CharField(blank=True, max_length=80)),
                ("pincode", models.CharField(blank=True, max_length=12)),
                ("currency", models.CharField(default="INR", max_length=8)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="owned_stores",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("avatar_url", models.URLField(blank=True)),
                ("timezone", models.CharField(default="Asia/Kolkata", max_length=64)),
                (
                    "default_store",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="default_for_profiles",
                        to="accounts.store",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StaffMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("owner", "Owner"),
                            ("manager", "Manager"),
                            ("cashier", "Cashier"),
                            ("analyst", "Analyst"),
                        ],
                        default="cashier",
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memberships",
                        to="accounts.store",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="store_memberships",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["store__name", "user__first_name"]},
        ),
        migrations.AddConstraint(
            model_name="staffmembership",
            constraint=models.UniqueConstraint(fields=("user", "store"), name="unique_user_store_membership"),
        ),
    ]
