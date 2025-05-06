from django.http import JsonResponse
from django.views.generic import ListView
from django.db.models import Count, Avg, Min, Max
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Car


class CarListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'scraper/car_list.html'
    context_object_name = 'cars'
    paginate_by = 20
    ordering = ['-datetime_found']


def stats_view(request):
    stats = {
        'total_cars': Car.objects.count(),
        'average_price': Car.objects.aggregate(Avg('price_usd'))['price_usd__avg'],
        'max_price': Car.objects.aggregate(Max('price_usd'))['price_usd__max'],
        'min_price': Car.objects.aggregate(Min('price_usd'))['price_usd__min'],
        'average_odometer': Car.objects.aggregate(Avg('odometer'))['odometer__avg'],
    }
    return JsonResponse(stats)
