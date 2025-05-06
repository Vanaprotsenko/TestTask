from django.urls import path
from . import views

app_name = 'scraper'

urlpatterns = [
    path('cars/', views.CarListView.as_view(), name='car_list'),
    path('stats/', views.stats_view, name='stats'),
]
