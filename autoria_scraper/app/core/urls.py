from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('scraper/', include('scraper.urls', namespace='scraper')),
]
