from django.contrib import admin
from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_usd', 'odometer', 'username', 'car_vin', 'datetime_found')
    list_filter = ('datetime_found',)
    search_fields = ('title', 'username', 'car_vin', 'car_number')
    readonly_fields = ('datetime_found',)
    ordering = ('-datetime_found',)
