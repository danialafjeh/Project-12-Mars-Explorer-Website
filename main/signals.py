from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Mars, Atmosphere, Weather, GeographicFeature, Moon, Mission, Rover, LandingSite


@receiver(post_save, sender=Mars)
def invalidate_mars_cache(sender, instance, **kwargs):
    cache.delete("mars:planet")

@receiver(post_delete, sender=Mars)
def invalidate_mars_cache_on_delete(sender, instance, **kwargs):
    cache.delete("mars:planet")



@receiver(post_save, sender=Atmosphere)
def invalidate_atmosphere_cache(sender, instance, **kwargs):
    cache.delete("mars:atmosphere")

@receiver(post_delete, sender=Atmosphere)
def invalidate_atmosphere_cache_on_delete(sender, instance, **kwargs):
    cache.delete("mars:atmosphere")



@receiver(post_save, sender=Weather)
def invalidate_weather_cache(sender, instance, **kwargs):
    cache.delete("mars:weather")

@receiver(post_delete, sender=Weather)
def invalidate_weather_cache_on_delete(sender, instance, **kwargs):
    cache.delete("mars:weather")



@receiver(post_save, sender=GeographicFeature)
def invalidate_GF_cache(sender, instance, **kwargs):
    cache.delete("mars:geographic_features")

@receiver(post_delete, sender=GeographicFeature)
def invalidate_GF_cache_on_delete(sender, instance, **kwargs):
    cache.delete("mars:geographic_features")



@receiver(post_save, sender=Moon)
def invalidate_moon_cache(sender, instance, **kwargs):
    if instance.name == "Phobos":
        cache.delete("mars:moon:phobos")

    elif instance.name == "Deimos":
        cache.delete("mars:moon:deimos")

@receiver(post_delete, sender=Moon)
def invalidate_moon_cache_on_delete(sender, instance, **kwargs):
    if instance.name == "Phobos":
        cache.delete("mars:moon:phobos")

    elif instance.name == "Deimos":
        cache.delete("mars:moon:deimos")



@receiver(post_save, sender=Mission)
def invalidate_mission_cache(sender, instance, **kwargs):
    cache.delete("mars:missions")

@receiver(post_delete, sender=Mission)
def invalidate_mission_cache_on_delete(sender, instance, **kwargs):
    cache.delete("mars:missions")



@receiver(post_save, sender=Rover)
def invalidate_rover_cache(sender, instance, **kwargs):
    cache.delete("mars:rovers")

@receiver(post_delete, sender=Rover)
def invalidate_rover_cache_on_delete(sender, instance, **kwargs):
    cache.delete("mars:rovers")



@receiver(post_save, sender=LandingSite)
def invalidate_weather_cache(sender, instance, **kwargs):
    cache.delete("mars:landing_sites")

@receiver(post_delete, sender=LandingSite)
def invalidate_weather_cache_on_delete(sender, instance, **kwargs):
    cache.delete("mars:landing_sites")
