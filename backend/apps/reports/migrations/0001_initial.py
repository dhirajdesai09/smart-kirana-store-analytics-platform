from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AnalyticsReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "report_type",
                    models.CharField(
                        choices=[
                            ("sales", "Sales"),
                            ("profit", "Profit"),
                            ("inventory", "Inventory"),
                            ("supplier", "Supplier"),
                            ("monthly", "Monthly Analytics"),
                        ],
                        max_length=30,
                    ),
                ),
                ("title", models.CharField(max_length=180)),
                ("period_start", models.DateField(blank=True, null=True)),
                ("period_end", models.DateField(blank=True, null=True)),
                ("file", models.FileField(blank=True, upload_to="reports/")),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "generated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="generated_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analytics_reports",
                        to="accounts.store",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["store", "report_type", "-created_at"], name="reports_ana_store_i_61f6de_idx")
                ],
            },
        ),
    ]
