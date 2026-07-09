from django.conf import settings
from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=160)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_stores",
    )
    business_type = models.CharField(max_length=120, default="Kirana / Grocery")
    gstin = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(max_length=12, blank=True)
    currency = models.CharField(max_length=8, default="INR")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StaffMembership(models.Model):
    OWNER = "owner"
    MANAGER = "manager"
    CASHIER = "cashier"
    ANALYST = "analyst"
    ROLE_CHOICES = [
        (OWNER, "Owner"),
        (MANAGER, "Manager"),
        (CASHIER, "Cashier"),
        (ANALYST, "Analyst"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="store_memberships",
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CASHIER)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "store"], name="unique_user_store_membership")
        ]
        ordering = ["store__name", "user__first_name"]

    def __str__(self):
        return f"{self.user} - {self.store} ({self.role})"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar_url = models.URLField(blank=True)
    default_store = models.ForeignKey(
        Store,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="default_for_profiles",
    )
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")

    def __str__(self):
        return f"Profile for {self.user}"
