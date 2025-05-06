from django.db import models


class Car(models.Model):
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=500)
    price_usd = models.IntegerField()
    odometer = models.IntegerField()
    username = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=500)
    image_url = models.URLField(max_length=500)
    images_count = models.IntegerField()
    car_number = models.CharField(max_length=500, blank=True, null=True)
    car_vin = models.CharField(max_length=500, blank=True, null=True)
    datetime_found = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['url', 'car_vin']
        indexes = [
            models.Index(fields=['url']),
            models.Index(fields=['car_vin']),
            models.Index(fields=['datetime_found']),
        ]

    def __str__(self):
        return f"{self.title} - {self.price_usd} USD"
