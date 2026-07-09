from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("inventory", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Sale",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number", models.CharField(max_length=40)),
                ("customer_name", models.CharField(blank=True, max_length=160)),
                ("customer_phone", models.CharField(blank=True, max_length=20)),
                ("customer_gstin", models.CharField(blank=True, max_length=20)),
                (
                    "payment_mode",
                    models.CharField(
                        choices=[("cash", "Cash"), ("upi", "UPI"), ("card", "Card"), ("credit", "Credit"), ("mixed", "Mixed")],
                        default="cash",
                        max_length=20,
                    ),
                ),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("discount_total", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("tax_total", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("grand_total", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("paid_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("balance_amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("completed", "Completed"), ("refunded", "Refunded")],
                        default="completed",
                        max_length=20,
                    ),
                ),
                ("sale_time", models.DateTimeField()),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sales",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sales",
                        to="accounts.store",
                    ),
                ),
            ],
            options={
                "ordering": ["-sale_time"],
                "indexes": [
                    models.Index(fields=["store", "-sale_time"], name="sales_sale_store_i_eb166f_idx"),
                    models.Index(fields=["store", "payment_mode"], name="sales_sale_store_i_79faf6_idx"),
                    models.Index(fields=["store", "status"], name="sales_sale_store_i_c25f78_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="SaleItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name_snapshot", models.CharField(max_length=180)),
                ("sku_snapshot", models.CharField(max_length=64)),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=12)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("purchase_price_snapshot", models.DecimalField(decimal_places=2, max_digits=12)),
                ("discount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("tax_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("line_total", models.DecimalField(decimal_places=2, max_digits=14)),
                ("profit_amount", models.DecimalField(decimal_places=2, max_digits=14)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sale_items",
                        to="inventory.product",
                    ),
                ),
                (
                    "sale",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="sales.sale",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
                "indexes": [
                    models.Index(fields=["product"], name="sales_sale_product_e8066a_idx"),
                    models.Index(fields=["sale"], name="sales_sale_sale_id_28710d_idx"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="sale",
            constraint=models.UniqueConstraint(fields=("store", "invoice_number"), name="unique_invoice_per_store"),
        ),
    ]
