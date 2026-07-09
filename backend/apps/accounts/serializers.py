from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import StaffMembership, Store, UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "name"]
        read_only_fields = ["id", "username", "name"]

    def get_name(self, obj):
        return obj.get_full_name() or obj.email or obj.username


class StoreSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "owner",
            "owner_name",
            "business_type",
            "gstin",
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "currency",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "owner_name", "created_at", "updated_at"]


class StaffMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = StaffMembership
        fields = [
            "id",
            "store",
            "user",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
            "is_active",
            "joined_at",
        ]
        read_only_fields = ["id", "user", "joined_at"]

    def validate_store(self, store):
        request = self.context["request"]
        if request.user.is_staff:
            return store
        if not store.memberships.filter(
            user=request.user,
            is_active=True,
            role__in=[StaffMembership.OWNER, StaffMembership.MANAGER],
        ).exists():
            raise serializers.ValidationError("Only owners and managers can manage staff.")
        return store

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.pop("email").lower()
        password = validated_data.pop("password", None)
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email, "first_name": first_name, "last_name": last_name},
        )
        if not created:
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.save(update_fields=["first_name", "last_name"])
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        membership, _ = StaffMembership.objects.update_or_create(
            user=user,
            store=validated_data["store"],
            defaults={
                "role": validated_data.get("role", StaffMembership.CASHIER),
                "is_active": validated_data.get("is_active", True),
            },
        )
        return membership


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    default_store = StoreSerializer(read_only=True)
    default_store_id = serializers.PrimaryKeyRelatedField(
        source="default_store",
        queryset=Store.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = UserProfile
        fields = ["user", "phone", "avatar_url", "timezone", "default_store", "default_store_id"]

    def validate_default_store_id(self, store):
        request = self.context["request"]
        if store and not store.memberships.filter(user=request.user, is_active=True).exists():
            raise serializers.ValidationError("You do not have access to this store.")
        return store


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    store_name = serializers.CharField(max_length=160)
    phone = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        store = Store.objects.create(
            name=validated_data["store_name"],
            owner=user,
            phone=validated_data.get("phone", ""),
            city=validated_data.get("city", ""),
            state=validated_data.get("state", ""),
        )
        StaffMembership.objects.create(user=user, store=store, role=StaffMembership.OWNER)
        profile = user.profile
        profile.phone = validated_data.get("phone", "")
        profile.default_store = store
        profile.save(update_fields=["phone", "default_store"])
        return user
