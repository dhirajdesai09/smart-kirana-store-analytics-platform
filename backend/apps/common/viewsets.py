from rest_framework.exceptions import ValidationError


class StoreScopedQuerySetMixin:
    store_lookup = "store_id"

    def get_user_store_ids(self):
        if self.request.user.is_staff:
            return None
        return list(
            self.request.user.store_memberships.filter(is_active=True).values_list(
                "store_id", flat=True
            )
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        store_ids = self.get_user_store_ids()
        if store_ids is None:
            return queryset
        return queryset.filter(**{f"{self.store_lookup}__in": store_ids})

    def get_active_store(self):
        from apps.accounts.models import Store

        store_id = self.request.data.get("store") or self.request.query_params.get("store")
        memberships = self.request.user.store_memberships.filter(is_active=True)
        if store_id:
            if self.request.user.is_staff:
                return Store.objects.get(id=store_id)
            membership = memberships.filter(store_id=store_id).first()
            if not membership:
                raise ValidationError({"store": "You do not have access to this store."})
            return membership.store
        profile = getattr(self.request.user, "profile", None)
        if profile and profile.default_store_id:
            return profile.default_store
        membership = memberships.order_by("joined_at").first()
        if not membership:
            raise ValidationError({"store": "Create or join a store before adding records."})
        return membership.store
