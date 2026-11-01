"""
URL configuration for NMAX project.
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny


def health(request):
    return JsonResponse({"status": "ok"})


class PublicSchemaView(SpectacularAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []


class PublicDocsView(SpectacularSwaggerView):
    permission_classes = [AllowAny]
    authentication_classes = []


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("api/v1/", include("app.api.v1.urls")),
    path("api/schema/", PublicSchemaView.as_view(), name="schema"),
    path("api/docs/", PublicDocsView.as_view(url_name="schema"), name="docs"),
]
