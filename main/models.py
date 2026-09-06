from django.db import models

# Create your models here.

class Mars(models.Model):
    name = models.CharField(max_length=50, unique=True)
    mass_kg = models.FloatField()
    radius_km = models.FloatField()
    diameter_km = models.FloatField()
    gravity_m_s2 = models.FloatField()
    density_kg_m3 = models.FloatField()
    distance_from_sun_km = models.FloatField()
    rotation_period_hours = models.FloatField()
    orbital_period_days = models.FloatField()
    axial_tilt_degrees = models.FloatField()
    description = models.TextField()

    class Meta:
        verbose_name_plural = 'Planet Mars'

    def __str__(self):
        return f'Planet Main Info : {self.name}'



class Atmosphere(models.Model):
    mars = models.OneToOneField(Mars, on_delete=models.CASCADE, related_name="atmosphere")
    surface_pressure_pa = models.FloatField()
    average_temperature_c = models.FloatField()
    composition = models.JSONField()
    description = models.TextField()

    class Meta:
            verbose_name_plural = 'Atmosphere'

    def __str__(self):
        return f'Mars Atmosphere Info'



class Weather(models.Model):
    HEMISPHERE_CHOICES = [
        ("northern", "Northern Hemisphere"),
        ("southern", "Southern Hemisphere"),
    ]
    SEASON_CHOICES = [
        ("spring", "Spring"),
        ("summer", "Summer"),
        ("autumn", "Autumn"),
        ("winter", "Winter"),
    ]

    mars = models.ForeignKey(Mars, on_delete=models.CASCADE, related_name="weathers")
    hemisphere = models.CharField(max_length=10, choices=HEMISPHERE_CHOICES)
    season = models.CharField(max_length=10, choices=SEASON_CHOICES)
    min_temperature_c = models.FloatField()
    max_temperature_c = models.FloatField()
    average_temperature_c = models.FloatField()
    description = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["hemisphere", "season"],
                name="unique_hemisphere_season"
            )
        ]

        verbose_name_plural = 'Weather'

    def __str__(self):
        return f'Mars Weather Info : {self.hemisphere} + {self.season}'



class GeographicFeature(models.Model):
    FEATURE_TYPES = [
        ("mountain", "Mountain"),
        ("volcano", "Volcano"),
        ("canyon", "Canyon"),
        ("crater", "Crater"),
        ("valley", "Valley"),
        ("plain", "Plain"),
    ]

    mars = models.ForeignKey(Mars, on_delete=models.CASCADE, related_name="geographices")
    name = models.CharField(max_length=150)
    feature_type = models.CharField(max_length=20,choices=FEATURE_TYPES)
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation_m = models.FloatField(null=True,blank=True)
    diameter_km = models.FloatField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f'Mars Geographic Feature Info : {self.name}'



class Moon(models.Model):
    mars = models.ForeignKey(Mars, on_delete=models.CASCADE, related_name="moons")
    name = models.CharField(max_length=50, unique=True)
    radius_km = models.FloatField()
    mass_kg = models.FloatField()
    orbital_period_days = models.FloatField()
    description = models.TextField()

    def __str__(self):
        return f'Mars Moon Info : {self.name}'



class Mission(models.Model):
    MISSION_TYPES = [
        ("orbiter", "Orbiter"),
        ("lander", "Lander"),
        ("rover", "Rover"),
        ("flyby", "Flyby"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("inactive", "Inactive"),
    ]

    mars = models.ForeignKey(Mars, on_delete=models.CASCADE, related_name="missions")
    name = models.CharField(max_length=150, unique=True)
    agency = models.CharField(max_length=100)
    mission_type = models.CharField(max_length=20, choices=MISSION_TYPES)
    launch_date = models.DateField()
    arrival_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    description = models.TextField()

    def __str__(self):
        return f'Mars Mission : {self.name}'



class Rover(models.Model):
    mission = models.OneToOneField(Mission,on_delete=models.CASCADE, related_name="rover")
    name = models.CharField(max_length=100,unique=True)
    landing_date = models.DateField()
    landing_site = models.CharField(max_length=150)
    current_status = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f'Mars Rover : {self.name}'



class LandingSite(models.Model):
    mars = models.ForeignKey(Mars, on_delete=models.CASCADE, related_name="landingsites")
    name = models.CharField(max_length=150, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    region = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return f'Mars Landing Site : {self.name}'
