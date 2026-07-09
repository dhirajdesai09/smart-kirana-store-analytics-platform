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
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("color", models.CharField(default="#2563eb", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="categories",
                        to="accounts.store",
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("contact_person", models.CharField(blank=True, max_length=120)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("address", models.TextField(blank=True)),
                ("gstin", models.CharField(blank=True, max_length=20)),
                ("lead_time_days", models.PositiveIntegerField(default=3)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="suppliers",
                        to="accounts.store",
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("sku", models.CharField(max_length=64)),
                ("barcode", models.CharField(blank=True, max_length=80)),
                (
                    "unit",
                    models.CharField(
                        choices=[("piece", "Piece"), ("kg", "Kg"), ("litre", "Litre"), ("packet", "Packet")],
                        default="piece",
                        max_length=20,
                    ),
                ),
                ("quantity", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("reorder_level", models.DecimalField(decimal_places=2, default=10, max_digits=12)),
                ("reorder_quantity", models.DecimalField(decimal_places=2, default=25, max_digits=12)),
                ("purchase_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("selling_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("tax_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("expiry_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("last_sold_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="inventory.category",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="accounts.store",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.supplier",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "indexes": [
                    models.Index(fields=["store", "sku"], name="inventory_p_store_i_9130fb_idx"),
                    models.Index(fields=["store", "is_active"], name="inventory_p_store_i_3301df_idx"),
                    models.Index(fields=["store", "expiry_date"], name="inventory_p_store_i_679f29_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="InventoryLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("purchase", "Purchase"),
                            ("sale", "Sale"),
                            ("adjustment", "Adjustment"),
                            ("return", "Return"),
                            ("expiry", "Expiry"),
                            ("opening", "Opening"),
                        ],
                        max_length=20,
                    ),
                ),
                ("quantity_change", models.DecimalField(decimal_places=2, max_digits=12)),
                ("quantity_after", models.DecimalField(decimal_places=2, max_digits=12)),
                ("reference", models.CharField(blank=True, max_length=120)),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="inventory_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inventory_logs",
                        to="inventory.product",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inventory_logs",
                        to="accounts.store",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["store", "-created_at"], name="inventory_i_store_i_1ed536_idx"),
                    models.Index(fields=["product", "-created_at"], name="inventory_i_product_5e7366_idx"),
                    models.Index(fields=["action", "-created_at"], name="inventory_i_action_364f2f_idx"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(fields=("store", "name"), name="unique_category_per_store"),
        ),
        migrations.AddConstraint(
            model_name="supplier",
            constraint=models.UniqueConstraint(fields=("store", "name"), name="unique_supplier_per_store"),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(fields=("store", "sku"), name="unique_sku_per_store"),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(condition=models.Q(("selling_price__gte", 0)), name="product_selling_price_positive"),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(condition=models.Q(("purchase_price__gte", 0)), name="product_purchase_price_positive"),
        ),
    ]
