from rest_framework import serializers

from app.models.vulnerabilities.vulnerability import (
    Vulnerability,
    VulnerabilityAsset,
    VulnerabilityHistory,
)
from app.services.risk_score import score_vulnerability
from app.services.vuln_service import build_fingerprint


class VulnerabilityAssetSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    asset_ip = serializers.CharField(source="asset.ip", read_only=True)

    class Meta:
        model = VulnerabilityAsset
        fields = (
            "id", "asset", "asset_name", "asset_ip",
            "component", "version", "port", "protocol", "evidence",
        )


class VulnerabilityHistorySerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source="operator.nickname", read_only=True)

    class Meta:
        model = VulnerabilityHistory
        fields = ("id", "operator", "operator_name", "old_status", "new_status", "note", "created_at")


class VulnerabilitySerializer(serializers.ModelSerializer):
    assets = VulnerabilityAssetSerializer(many=True, read_only=True)
    histories = VulnerabilityHistorySerializer(many=True, read_only=True)
    asset_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False, default=list
    )
    risk_score = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source="created_by.nickname", read_only=True)

    class Meta:
        model = Vulnerability
        fields = (
            "id", "name", "description", "cve_id", "cnnvd_id", "source", "vuln_type",
            "risk_level", "cvss_score", "status", "impact", "solution", "poc",
            "verify_info", "fingerprint", "sla_due_at", "discovered_at", "verified_at",
            "fixed_at", "closed_at", "affected_url", "request_method", "request_header",
            "request_body", "response_header", "response_body", "affected_component",
            "affected_version", "affected_port", "protocol", "created_by",
            "created_by_name", "created_at", "updated_at", "assets", "histories",
            "asset_ids", "risk_score",
        )
        read_only_fields = (
            "id", "created_by", "fingerprint", "discovered_at", "verified_at",
            "fixed_at", "closed_at", "created_at", "updated_at",
        )

    def get_risk_score(self, obj):
        link = obj.assets.first()
        return score_vulnerability(obj, link.asset if link else None)

    def _set_assets(self, vuln, asset_ids):
        vuln.assets.all().delete()
        for aid in asset_ids:
            VulnerabilityAsset.objects.create(vulnerability=vuln, asset_id=aid)

    def create(self, validated_data):
        asset_ids = validated_data.pop("asset_ids", []) or []
        if not validated_data.get("fingerprint"):
            validated_data["fingerprint"] = build_fingerprint(
                validated_data.get("name", ""),
                validated_data.get("cve_id"),
                validated_data.get("vuln_type", ""),
            )
        vuln = Vulnerability.objects.create(**validated_data)
        self._set_assets(vuln, asset_ids)
        return vuln

    def update(self, instance, validated_data):
        asset_ids = validated_data.pop("asset_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if not instance.fingerprint:
            instance.fingerprint = build_fingerprint(
                instance.name, instance.cve_id, instance.vuln_type
            )
        instance.save()
        if asset_ids is not None:
            self._set_assets(instance, asset_ids or [])
        return instance
