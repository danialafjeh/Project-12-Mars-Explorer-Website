from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Mars)
admin.site.register(models.Atmosphere)
admin.site.register(models.Weather)
admin.site.register(models.GeographicFeature)
admin.site.register(models.Moon)
admin.site.register(models.Mission)
admin.site.register(models.Rover)
admin.site.register(models.LandingSite)
