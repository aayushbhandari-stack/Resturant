from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # ========================================================
    # ADMIN
    # ========================================================

    path(
        "admin/",
        admin.site.urls,
    ),

    # ========================================================
    # RMS APPLICATION
    # ========================================================

    path(
        "",
        include("rms.urls"),
    ),
    
    
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
