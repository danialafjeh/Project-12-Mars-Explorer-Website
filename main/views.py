from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from .models import Mars, Atmosphere, Weather, GeographicFeature, Moon, Mission, Rover, LandingSite

# Create your views here.

def home_page(request):
    return render(request, 'home.html')



def overview_page(request):
    mars = cache.get_or_set(
        "mars:planet",
        lambda: Mars.objects.first(),
        timeout=3600,
    )
    atmosphere = cache.get_or_set(
        "mars:atmosphere",
        lambda: Atmosphere.objects.first(),
        timeout=3600,
    )

    info = {
        'mars':mars,
        'atmosphere':atmosphere
    }
    return render(request, 'overview.html', info)



def surface_page(request):
    geographic_features = cache.get_or_set(
        "mars:geographic_features",
        lambda: list(GeographicFeature.objects.all()),
        timeout=3600,
    )
    weather = cache.get_or_set(
        "mars:weather",
        lambda: list(Weather.objects.all()),
        timeout=3600,
    )
    info = {
        'geographics':geographic_features,
        'weather':weather
    }
    return render(request, 'surface.html', info)



def moons_page(request):
    phobos = cache.get_or_set(
        "mars:moon:phobos",
        lambda: Moon.objects.get(name='Phobos'),
        timeout=3600,
    )
    deimos = cache.get_or_set(
        "mars:moon:deimos",
        lambda: Moon.objects.get(name='Deimos'),
        timeout=3600,
    )

    info = {
        'phobos':phobos,
        'deimos':deimos
    }
    return render(request, 'moons.html', info)



def ops_page(request):
    missions = cache.get_or_set(
        "mars:missions",
        lambda: list(Mission.objects.all()),
        timeout=3600,
    )
    rovers = cache.get_or_set(
        "mars:rovers",
        lambda: list(Rover.objects.all()),
        timeout=3600,
    )
    landing_sites = cache.get_or_set(
        "mars:landing_sites",
        lambda: list(LandingSite.objects.all()),
        timeout=3600,
    )

    info = {
        'ops':missions,
        'rovers':rovers,
        'sites':landing_sites
    }
    return render(request, 'missions.html', info)
