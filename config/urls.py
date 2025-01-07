from django.views.static import serve
from django.urls import re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
import logging

logger = logging.getLogger(__name__)


urlpatterns = [
    path("backend/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/stores/", include("store.urls")),
    path("", include("admin_panel.urls")),
]

if settings.DEBUG:
    logger.info("WORKING IN DEBUG MODE")
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

else:
    logger.warning("WORKING IN PRODUCTION MODE")
    urlpatterns += (
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
        re_path(
            r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}
        ),
    )


admin.site.site_header = "The Database Captain"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to the Eye Health"
