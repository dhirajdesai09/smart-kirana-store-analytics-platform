from rest_framework import serializers

from .models import AnalyticsReport


class AnalyticsReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)

    class Meta:
        model = AnalyticsReport
        fields = [
            "id",
            "store",
            "report_type",
            "title",
            "period_start",
            "period_end",
            "file",
            "metadata",
            "generated_by",
            "generated_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "generated_by", "generated_by_name", "created_at"]
