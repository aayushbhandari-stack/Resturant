from django.contrib import admin
from django.urls import path, include


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
