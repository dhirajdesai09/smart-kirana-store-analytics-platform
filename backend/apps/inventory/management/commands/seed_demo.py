import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import StaffMembership, Store
from apps.inventory.models import Category, InventoryLog, Product, Supplier
from apps.sales.models import Sale, SaleItem

User = get_user_model()


class Command(BaseCommand):
    help = "Seed StorePulse with realistic kirana demo data."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        user, _ = User.objects.get_or_create(
            username="owner@storepulse.local",
            defaults={
                "email": "owner@storepulse.local",
                "first_name": "Asha",
                "last_name": "Patel",
            },
        )
        user.email = "owner@storepulse.local"
        user.set_password("Demo@12345")
        user.save()

        store, _ = Store.objects.update_or_create(
            name="Patel Smart Kirana",
            owner=user,
            defaults={
                "phone": "+91 98765 43210",
                "city": "Pune",
                "state": "Maharashtra",
                "gstin": "27ABCDE1234F1Z5",
                "address": "Market Road, Kothrud",
            },
        )
        StaffMembership.objects.update_or_create(user=user, store=store, defaults={"role": StaffMembership.OWNER})
        user.profile.default_store = store
        user.profile.phone = "+91 98765 43210"
        user.profile.save()

        Sale.objects.filter(store=store).delete()
        Product.objects.filter(store=store).delete()
        Category.objects.filter(store=store).delete()
        Supplier.objects.filter(store=store).delete()

        category_names = [
            ("Rice & Grains", "#16a34a"),
            ("Edible Oil", "#f97316"),
            ("Snacks", "#7c3aed"),
            ("Dairy", "#0284c7"),
            ("Household", "#0f766e"),
            ("Personal Care", "#db2777"),
            ("Festive", "#dc2626"),
        ]
        categories = {
            name: Category.objects.create(store=store, name=name, color=color)
            for name, color in category_names
        }
        suppliers = [
            Supplier.objects.create(store=store, name="Metro Wholesale", phone="020-4001001", lead_time_days=2),
            Supplier.objects.create(store=store, name="Local FMCG Distributor", phone="020-4001002", lead_time_days=3),
            Supplier.objects.create(store=store, name="Fresh Dairy Co", phone="020-4001003", lead_time_days=1),
        ]

        product_seed = [
            ("Basmati Rice 5kg", "RICE-5KG", "Rice & Grains", 98, 520, 680, 18, 30),
            ("Toor Dal 1kg", "DAL-TOOR", "Rice & Grains", 64, 110, 145, 15, 24),
            ("Sunflower Oil 1L", "OIL-SUN1", "Edible Oil", 46, 122, 158, 12, 30),
            ("Groundnut Oil 1L", "OIL-GND1", "Edible Oil", 28, 154, 198, 8, 20),
            ("Parle-G Family Pack", "BISC-PG", "Snacks", 135, 8, 10, 40, 100),
            ("Masala Chips", "SNK-CHIP", "Snacks", 88, 16, 20, 30, 80),
            ("Milk 1L", "DAIRY-MILK", "Dairy", 38, 54, 62, 20, 60),
            ("Curd 500g", "DAIRY-CURD", "Dairy", 18, 28, 35, 15, 40),
            ("Detergent 1kg", "HOME-DET", "Household", 32, 78, 99, 10, 24),
            ("Bath Soap 4pc", "CARE-SOAP", "Personal Care", 54, 92, 120, 16, 32),
            ("Diyas Pack 12", "FEST-DIYA", "Festive", 72, 42, 65, 15, 60),
            ("Dry Fruit Mix 250g", "FEST-DF250", "Festive", 24, 160, 230, 10, 30),
        ]
        products = []
        for index, (name, sku, category, qty, purchase, selling, reorder, reorder_qty) in enumerate(product_seed):
            expiry = timezone.localdate() + timedelta(days=random.choice([15, 35, 90, 180]))
            product = Product.objects.create(
                store=store,
                category=categories[category],
                supplier=suppliers[index % len(suppliers)],
                name=name,
                sku=sku,
                quantity=Decimal(qty),
                reorder_level=Decimal(reorder),
                reorder_quantity=Decimal(reorder_qty),
                purchase_price=Decimal(purchase),
                selling_price=Decimal(selling),
                tax_rate=Decimal("5.00") if category not in {"Dairy"} else Decimal("0.00"),
                expiry_date=expiry,
            )
            InventoryLog.objects.create(
                store=store,
                product=product,
                action=InventoryLog.OPENING,
                quantity_change=product.quantity,
                quantity_after=product.quantity,
                reference="demo-seed",
                created_by=user,
            )
            products.append(product)

        baskets = [
            ["Basmati Rice 5kg", "Sunflower Oil 1L", "Toor Dal 1kg"],
            ["Parle-G Family Pack", "Milk 1L"],
            ["Masala Chips", "Bath Soap 4pc"],
            ["Milk 1L", "Curd 500g"],
            ["Diyas Pack 12", "Dry Fruit Mix 250g", "Sunflower Oil 1L"],
        ]
        product_by_name = {product.name: product for product in products}
        for day_offset in range(59, -1, -1):
            sale_date = timezone.now() - timedelta(days=day_offset)
            is_weekend = sale_date.weekday() >= 5
            festival_boost = sale_date.date() in {
                timezone.localdate() - timedelta(days=7),
                timezone.localdate() - timedelta(days=8),
                timezone.localdate() - timedelta(days=9),
            }
            invoices_today = random.randint(5, 12) + (4 if is_weekend else 0) + (8 if festival_boost else 0)
            for invoice_index in range(invoices_today):
                sale_time = sale_date.replace(
                    hour=random.choice([9, 10, 11, 17, 18, 19, 20]),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0,
                )
                invoice = f"SP-{sale_time:%Y%m%d}-{invoice_index + 1:04d}"
                sale = Sale.objects.create(
                    store=store,
                    invoice_number=invoice,
                    payment_mode=random.choice([Sale.CASH, Sale.UPI, Sale.UPI, Sale.CARD]),
                    sale_time=sale_time,
                    paid_amount=0,
                    created_by=user,
                )
                selected_names = random.choice(baskets)
                if random.random() > 0.65:
                    selected_names = selected_names + [random.choice(products).name]
                subtotal = Decimal("0")
                discount_total = Decimal("0")
                tax_total = Decimal("0")
                grand_total = Decimal("0")
                for name in selected_names:
                    product = product_by_name[name]
                    qty = Decimal(random.choice([1, 1, 1, 2, 3]))
                    if product.category.name == "Festive" and festival_boost:
                        qty += Decimal(2)
                    unit_price = product.selling_price
                    discount = Decimal(random.choice([0, 0, 0, 2, 5]))
                    taxable = max(qty * unit_price - discount, Decimal("0"))
                    tax_amount = taxable * product.tax_rate / Decimal("100")
                    line_total = taxable + tax_amount
                    profit = (unit_price - product.purchase_price) * qty - discount
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        product_name_snapshot=product.name,
                        sku_snapshot=product.sku,
                        quantity=qty,
                        unit_price=unit_price,
                        purchase_price_snapshot=product.purchase_price,
                        discount=discount,
                        tax_rate=product.tax_rate,
                        tax_amount=tax_amount,
                        line_total=line_total,
                        profit_amount=profit,
                    )
                    product.quantity = max(Decimal("0"), product.quantity - qty)
                    product.last_sold_at = sale_time
                    product.save(update_fields=["quantity", "last_sold_at", "updated_at"])
                    InventoryLog.objects.create(
                        store=store,
                        product=product,
                        action=InventoryLog.SALE,
                        quantity_change=-qty,
                        quantity_after=product.quantity,
                        reference=invoice,
                        created_by=user,
                    )
                    subtotal += qty * unit_price
                    discount_total += discount
                    tax_total += tax_amount
                    grand_total += line_total
                sale.subtotal = subtotal
                sale.discount_total = discount_total
                sale.tax_total = tax_total
                sale.grand_total = grand_total
                sale.paid_amount = grand_total
                sale.balance_amount = Decimal("0")
                sale.save()

        self.stdout.write(self.style.SUCCESS("Seeded StorePulse demo data. Login: owner@storepulse.local / Demo@12345"))
