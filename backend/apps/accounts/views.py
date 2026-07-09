from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsStoreMember, IsStoreOwnerOrManager
from apps.common.viewsets import StoreScopedQuerySetMixin

from .models import StaffMembership, Store
from .serializers import RegisterSerializer, StaffMembershipSerializer, StoreSerializer, UserProfileSerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"id": user.id, "email": user.email}, status=status.HTTP_201_CREATED)


class MeView(APIView):
    def get(self, request):
        serializer = UserProfileSerializer(request.user.profile, context={"request": request})
        memberships = StaffMembership.objects.filter(user=request.user, is_active=True).select_related("store")
        return Response(
            {
                "profile": serializer.data,
                "stores": StoreSerializer([membership.store for membership in memberships], many=True).data,
                "roles": [
                    {"store": membership.store_id, "role": membership.role}
                    for membership in memberships
                ],
            }
        )

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user.profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {
                "detail": "If the email exists, a reset link will be sent. Configure an email backend for production delivery."
            }
        )


class StoreViewSet(StoreScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsStoreMember]
    queryset = Store.objects.select_related("owner").all()
    search_fields = ["name", "city", "state", "gstin"]
    ordering_fields = ["name", "created_at", "city"]
    store_lookup = "id"

    def perform_create(self, serializer):
        store = serializer.save(owner=self.request.user)
        StaffMembership.objects.get_or_create(
            user=self.request.user,
            store=store,
            defaults={"role": StaffMembership.OWNER},
        )
        profile = self.request.user.profile
        if not profile.default_store_id:
            profile.default_store = store
            profile.save(update_fields=["default_store"])


class StaffViewSet(StoreScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = StaffMembershipSerializer
    permission_classes = [IsStoreOwnerOrManager]
    queryset = StaffMembership.objects.select_related("user", "store").all()
    filterset_fields = ["store", "role", "is_active"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    ordering_fields = ["joined_at", "role"]
