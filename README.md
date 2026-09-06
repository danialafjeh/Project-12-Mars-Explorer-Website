# 💻 About Project

[Complete Guide | Run this project on your computer](https://github.com/danialafjeh/Run-My-Projects-Locally)

# Mars Explorer

A Django-based Mars exploration and information platform built to present structured scientific data about Mars while demonstrating practical backend architecture with PostgreSQL, Redis caching, cache invalidation, Docker, and automated database initialization.

The project combines a server-side rendered Django application with a PostgreSQL database as the primary data source and Redis as a caching layer. It is designed around the idea that relatively static planetary information does not need to be queried from PostgreSQL on every request.

---

## Overview

Mars Explorer is an educational and portfolio-oriented web application that organizes information about Mars into several dedicated sections.

Main goal of this project is learning to work with Redis as caching layer inside a project powered by Django.

The application provides information about:

* Mars itself and its general characteristics
* Martian atmosphere
* Geographic features and surface information
* Weather information
* Mars missions
* Mars rovers
* Landing sites
* Mars' moons, Phobos and Deimos

The project does not require authentication because its purpose is to provide publicly accessible scientific information and learning to use Redis as caching layer rather than user-specific functionality. ( You can visit my previous projects that have full authentication system and more things to explore )

The main backend objective is to demonstrate how Redis can be integrated with Django to reduce unnecessary database queries for data that changes infrequently.

---

## Key Features

* Server-side rendered Django application
* PostgreSQL relational database
* Redis caching with `django-redis`
* Cache-Aside caching strategy
* Separate cache keys for individual datasets
* One-hour cache expiration
* Automatic cache invalidation using Django signals
* PostgreSQL persistence through a Docker named volume
* Automatic database migrations during container startup
* Automatic initial data loading from a Django fixture
* Conditional fixture loading to prevent duplicate data
* Dockerized Django, PostgreSQL, and Redis services
* PostgreSQL and Redis health checks
* Docker Compose service dependency management
* Structured application sections for Mars, surface, operations, and moons

---

# Architecture

The application follows a simple three-service architecture:

```text
                    ┌─────────────────────┐
                    │       Browser       │
                    └──────────┬──────────┘
                               │
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │       Django        │
                    │     Application     │
                    └───────┬───────┬─────┘
                            │       │
                  Cache     │       │ Database
                            │       │
                            ▼       ▼
                    ┌───────────┐ ┌──────────────┐
                    │   Redis   │ │  PostgreSQL  │
                    │   Cache   │ │ Source of    │
                    │           │ │ Truth        │
                    └───────────┘ └──────────────┘
```

The responsibilities of each component are intentionally separated.

### Django

Django is responsible for:

* Handling HTTP requests
* Executing application logic
* Retrieving data from Redis or PostgreSQL
* Rendering HTML templates
* Managing database models
* Managing cache invalidation through Django signals

### PostgreSQL

PostgreSQL is the application's persistent source of truth.

The actual Mars data lives in PostgreSQL. Redis does not replace PostgreSQL and is not considered the authoritative storage layer.

### Redis

Redis acts as a high-speed temporary cache.

Frequently requested data is stored in Redis so that subsequent requests can avoid unnecessary PostgreSQL queries.

The cache is disposable. If Redis is cleared, the application can retrieve the original data from PostgreSQL and rebuild the cache automatically.

---

# Application Structure

The main navigation is divided into the following sections:

```text
Home
│
├── Overview
│   ├── Mars
│   └── Atmosphere
│
├── Surface
│   ├── Geographic Features
│   └── Weather
│
├── Ops
│   ├── Missions
│   ├── Rovers
│   └── Landing Sites
│
└── Moons
    ├── Phobos
    └── Deimos
```

Each section retrieves the information it needs through the caching layer.

---

# Data Model

The `main` Django application contains the project's domain models.

The core models are:

```text
Mars
Atmosphere
GeographicFeature
Weather
Mission
Rover
LandingSite
Moon
```

## Mars

The `Mars` model represents the main planetary information.

The application treats Mars as a single primary dataset rather than a collection of multiple planets.

This makes it a suitable candidate for object-level caching.

---

## Atmosphere

`Atmosphere` contains information about the Martian atmosphere and is associated with Mars through a one-to-one relationship.

Because the application only needs a single atmosphere record, it is also cached as an individual object.

---

## GeographicFeature

`GeographicFeature` stores information about notable geographic features on Mars.

Examples can include major surface formations and other significant geographical locations.

Because multiple records are displayed together on the Surface page, the project caches the complete collection.

---

## Weather

`Weather` stores Martian weather-related information.

Like geographic features, weather data is retrieved as a collection and cached as a complete list.

---

## Mission

`Mission` represents Mars exploration missions.

The project uses a collection-level cache for missions because the Ops page displays the complete mission dataset.

---

## Rover

`Rover` represents Mars exploration rovers and their associated mission information.

Rover records are cached as a collection.

---

## LandingSite

`LandingSite` represents locations associated with Mars mission landings.

Landing sites are also cached as a complete collection.

---

## Moon

`Moon` represents Mars' natural satellites.

The project contains two expected records:

```text
Phobos
Deimos
```

Unlike the collection-based models, these two objects are cached individually.

This provides an example of object-level caching inside the same application.

---

# Redis Caching

One of the primary goals of Mars Explorer is to demonstrate practical Redis caching in Django.

The application uses:

```text
django-redis
```

as the Django cache backend.

The cache backend is configured through Django's standard cache framework.

The Redis connection is provided through the `REDIS_URL` environment variable.

Inside Docker Compose, Django connects to Redis using the service name:

```text
redis://redis:6379/0
```

The `redis` hostname works because Docker Compose provides an internal network and service-name-based DNS resolution.

---

# Cache-Aside Strategy

The project uses the **Cache-Aside** pattern.

The basic flow is:

```text
Request
   │
   ▼
Check Redis
   │
   ├── Cache Hit ──────► Return cached data
   │
   └── Cache Miss
            │
            ▼
      Query PostgreSQL
            │
            ▼
       Store in Redis
            │
            ▼
       Return data
```

This means Django does not automatically write every database query into Redis.

Instead, the application explicitly decides which data should be cached.

---

# Why Cache-Aside?

Mars Explorer contains data that is relatively static.

For example:

* Mars' physical characteristics
* Atmospheric information
* Geographic features
* Historical missions
* Rover information
* Landing sites
* Moon information

There is little reason to query PostgreSQL repeatedly for data that rarely changes.

Without caching, a request to a page containing several datasets could produce multiple database queries.

With caching, the first request populates Redis and subsequent requests can retrieve the data directly from Redis.

---

# Cache Keys

Each cached dataset has its own explicit key.

```text
mars:planet
mars:atmosphere

mars:geographic_features
mars:weather

mars:missions
mars:rovers
mars:landing_sites

mars:moon:phobos
mars:moon:deimos
```

The key naming convention provides a clear namespace for the project's cache data.

The resulting logical structure is:

```text
Overview
 ├── mars:planet
 └── mars:atmosphere

Surface
 ├── mars:geographic_features
 └── mars:weather

Ops
 ├── mars:missions
 ├── mars:rovers
 └── mars:landing_sites

Moons
 ├── mars:moon:phobos
 └── mars:moon:deimos
```

---

# Cache Expiration (TTL)

TTL means Time To Live.
Each cache entry uses a one-hour timeout:

```python
timeout=3600
```

Therefore, cached data automatically expires after 3600 seconds.

The timeout acts as a safety mechanism.

Even if an invalidation mechanism fails or data changes without triggering the expected signal, the cached value will eventually expire and Django will retrieve fresh data from PostgreSQL.

However, TTL alone is not the primary freshness mechanism in this project.

The project also uses explicit cache invalidation.

---

# `cache.get_or_set()`

The application uses Django's:

```python
cache.get_or_set()
```

method.

This combines the cache lookup and cache population operation.

For example:

```python
mars = cache.get_or_set(
    "mars:planet",
    Mars.objects.first,
    timeout=3600,
)
```

Conceptually, this means:

```text
Does "mars:planet" exist?
        │
   ┌────┴────┐
   │         │
  Yes        No
   │         │
   ▼         ▼
Return    Execute query
cache         │
value         ▼
           Store result
               │
               ▼
           Return result
```

---

# Callable Defaults

Some queries can be passed directly as callable objects.

For example:

```python
Mars.objects.first
```

is a callable method reference.

It is intentionally not written as:

```python
Mars.objects.first()
```

The difference is important.

```python
Mars.objects.first
```

means:

> Give `get_or_set()` the function so it can call it only when the cache is missing.

Whereas:

```python
Mars.objects.first()
```

means:

> Execute the database query immediately and pass the result to `get_or_set()`.

For queries requiring arguments, a lambda is used:

```python
lambda: Moon.objects.get(name="Phobos")
```

This keeps the database query lazy and ensures that it executes only on a cache miss.

---

# Overview Caching

The Overview page requires two objects:

```text
Mars
Atmosphere
```

The view uses:

```python
from django.core.cache import cache
from django.shortcuts import render
from .models import Mars, Atmosphere


def overview(request):
    mars = cache.get_or_set(
        "mars:planet",
        Mars.objects.first,
        timeout=3600,
    )

    atmosphere = cache.get_or_set(
        "mars:atmosphere",
        Atmosphere.objects.first,
        timeout=3600,
    )

    return render(
        request,
        "main/overview.html",
        {
            "mars": mars,
            "atmosphere": atmosphere,
        },
    )
```

On the first request, PostgreSQL is queried.

On subsequent requests, Redis provides both objects until their cache entries expire or are invalidated.

---

# Surface Caching

The Surface page retrieves:

```text
GeographicFeature
Weather
```

Both are collections, so the project caches the complete result set.

```python
from django.core.cache import cache
from django.shortcuts import render
from .models import GeographicFeature, Weather


def surface(request):
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

    return render(
        request,
        "main/surface.html",
        {
            "geographic_features": geographic_features,
            "weather": weather,
        },
    )
```

The use of:

```python
list(...)
```

is intentional.

The complete queryset is evaluated and the resulting collection is stored in the cache.

---

# Operations Caching

The Ops page contains:

```text
Missions
Rovers
Landing Sites
```

The three datasets are cached independently.

```python
from django.core.cache import cache
from django.shortcuts import render
from .models import Mission, Rover, LandingSite


def ops(request):
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

    return render(
        request,
        "main/ops.html",
        {
            "missions": missions,
            "rovers": rovers,
            "landing_sites": landing_sites,
        },
    )
```

This means one cache entry represents each complete dataset.

For example:

```text
mars:missions
```

contains the cached collection of missions.

---

# Moon Caching

Phobos and Deimos are cached separately.

```python
from django.core.cache import cache
from django.shortcuts import render
from .models import Moon


def moons(request):
    phobos = cache.get_or_set(
        "mars:moon:phobos",
        lambda: Moon.objects.get(name="Phobos"),
        timeout=3600,
    )

    deimos = cache.get_or_set(
        "mars:moon:deimos",
        lambda: Moon.objects.get(name="Deimos"),
        timeout=3600,
    )

    return render(
        request,
        "main/moons.html",
        {
            "phobos": phobos,
            "deimos": deimos,
        },
    )
```

This demonstrates a different caching granularity from the collection-based pages.

Instead of:

```text
mars:moons → [Phobos, Deimos]
```

the application has:

```text
mars:moon:phobos → Phobos
mars:moon:deimos → Deimos
```

---

# Cache Invalidation

TTL alone is not enough when immediate freshness matters.

For that reason, Mars Explorer uses Django model signals to invalidate affected cache entries whenever relevant database records are modified.

The general strategy is:

```text
Database object changes
        │
        ▼
Django signal
        │
        ▼
Delete related Redis key
        │
        ▼
Next request
        │
        ▼
Cache miss
        │
        ▼
Read fresh data from PostgreSQL
        │
        ▼
Store fresh data in Redis
```

This provides both:

* TTL-based expiration
* Event-driven invalidation

---

# Mission Cache Invalidation

For missions, the application caches the complete collection:

```text
mars:missions
```

Therefore, when any `Mission` is created, updated, or deleted, the entire collection cache is invalidated.

```python
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Mission


@receiver(post_save, sender=Mission)
def invalidate_mission_cache(sender, instance, **kwargs):
    cache.delete("mars:missions")


@receiver(post_delete, sender=Mission)
def invalidate_mission_cache_on_delete(sender, instance, **kwargs):
    cache.delete("mars:missions")
```

For example:

```text
Mission A
Mission B
Mission C
```

may be stored as one cached value:

```text
mars:missions → [A, B, C]
```

If Mission B changes, the entire cached collection becomes stale.

Therefore:

```python
cache.delete("mars:missions")
```

is the correct invalidation operation for this caching strategy.

The next request rebuilds the collection from PostgreSQL.

---

# Moon Cache Invalidation

Phobos and Deimos are cached individually, so invalidation can be more granular.

```python
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Moon


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
```

The project assumes the two expected moon names remain:

```text
Phobos
Deimos
```

Therefore, the cache invalidation logic does not attempt to handle arbitrary moon-name changes.

---

# Signal Registration

The signal definitions live in:

```text
main/signals.py
```

Django must import this module when the application starts so that the `@receiver` decorators can register the signal handlers.

The `MainConfig` application configuration handles this:

```python
from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        from . import signals
```

The application is registered using:

```python
"main.apps.MainConfig",
```

inside `INSTALLED_APPS`.

The startup sequence is therefore conceptually:

```text
Django starts
     │
     ▼
MainConfig.ready()
     │
     ▼
Import main.signals
     │
     ▼
@receiver decorators register handlers
     │
     ▼
Signals become active
```

---

# Why `post_save` and `post_delete`?

The project uses two Django model signals.

### `post_save`

Triggered after a model instance has been saved.

It covers operations such as:

* Creating a record
* Updating a record

### `post_delete`

Triggered after a model instance has been deleted.

Using both signals ensures that the cache does not retain stale data after either modification or deletion.

---

# PostgreSQL as the Source of Truth

Redis is not a replacement for PostgreSQL.

The architecture intentionally separates persistent storage from temporary cached storage.

```text
PostgreSQL
    │
    │ authoritative data
    ▼
Source of Truth


Redis
    │
    │ temporary representation
    ▼
Cache
```

If Redis is deleted completely, the application's data is still available in PostgreSQL.

The next request simply causes a cache miss, retrieves the data from PostgreSQL, and repopulates Redis.

This is one of the fundamental properties of a cache-aside architecture.

---

# Docker Architecture

The project is containerized using Docker Compose.

The Compose configuration defines three services:

```text
django
db
redis
```

The architecture is:

```text
docker compose
│
├── django
│   └── Django application
│
├── db
│   └── PostgreSQL 18
│
└── redis
    └── Redis 7
```

---

# Django Container

The Django image is based on:

```text
python:3.12-slim
```

The Dockerfile follows a simple layered structure:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
```

The Dockerfile intentionally copies `requirements.txt` before the rest of the source code.

This allows Docker to reuse the dependency installation layer when application source files change but the dependency list remains unchanged.

---

# Python Dependencies

The project uses:

```text
Django
psycopg2-binary
django-redis
```

among its runtime dependencies.

`psycopg2-binary` is used to provide PostgreSQL connectivity from the Python/Django container without requiring the PostgreSQL development toolchain needed to compile `psycopg2` from source in the slim base image.

---

# Docker Compose Networking

Django does not connect to PostgreSQL using:

```text
127.0.0.1
```

inside Docker.

Within a container, `127.0.0.1` refers to the container itself.

Docker Compose provides service-name DNS instead.

Therefore Django uses:

```text
POSTGRES_HOST=db
```

and:

```text
REDIS_URL=redis://redis:6379/0
```

The architecture becomes:

```text
Django container
     │
     ├── db:5432
     │
     └── redis:6379
```

---

# PostgreSQL Persistence

PostgreSQL uses a named Docker volume:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql
```

This is essential because containers are disposable, while database data needs to survive container recreation.

The distinction is:

```text
Container
    → disposable

Volume
    → persistent database storage
```

Therefore:

```text
docker compose down
```

removes the containers but preserves the PostgreSQL volume.

Whereas:

```text
docker compose down -v
```

also removes the named volume and therefore deletes the persisted database data.

---

# Redis Persistence

Redis does not use a persistent volume in this project.

This is intentional.

Redis is being used as a cache rather than the source of truth.

If Redis disappears:

```text
Redis data lost
      ↓
PostgreSQL still contains the data
      ↓
Next request causes cache miss
      ↓
PostgreSQL queried
      ↓
Redis populated again
```

There is therefore no requirement to preserve Redis cache contents across container recreation.

---

# Health Checks

Docker Compose uses health checks for PostgreSQL and Redis.

PostgreSQL uses:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d mars-explorer"]
  interval: 5s
  timeout: 5s
  retries: 5
```

Redis uses:

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 5s
  retries: 5
```

The Django service depends on both services being healthy:

```yaml
depends_on:
  db:
    condition: service_healthy
  redis:
    condition: service_healthy
```

This is more reliable than simply starting Django after the database container has been created.

A container being started does not necessarily mean that the service inside it is ready to accept connections.

---

# Environment Configuration

Django reads database and Redis configuration from environment variables.

For PostgreSQL:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}
```

For Redis:

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}
```

The project intentionally uses environment variables rather than hard-coding Docker service addresses into Django settings.

---

# Database Initialization

The project includes an `entrypoint.sh` script responsible for preparing the Django application when the container starts.

```bash
#!/bin/sh

python manage.py migrate

if [ "$(python manage.py shell -c "from main.models import Mars; print(Mars.objects.exists())" | tail -n 1)" = "True" ]; then
    echo "Sample data already exists. Skipping loaddata."
else
    echo "Loading sample data..."
    python manage.py loaddata main/mars_data.json
fi

python manage.py runserver 0.0.0.0:8000
```

The startup process is:

```text
Container starts
       │
       ▼
Run migrations
       │
       ▼
Check whether Mars data exists
       │
   ┌───┴────┐
   │        │
 True      False
   │        │
   ▼        ▼
Skip      Load fixture
   │        │
   └───┬────┘
       ▼
Start Django
```

---

# Automatic Migrations

The entrypoint always runs:

```bash
python manage.py migrate
```

This is safe to execute repeatedly.

Django checks which migrations have already been applied and only executes unapplied migrations.

Therefore an existing database does not have its schema recreated every time the container starts.

---

# Fixture-Based Sample Data

The project's initial Mars data is stored in:

```text
main/mars_data.json
```

It was generated as a Django fixture and contains the application's initial records.

The fixture can be loaded with:

```bash
python manage.py loaddata main/mars_data.json
```

The Docker entrypoint does not blindly execute `loaddata` every time.

Instead, it checks whether a `Mars` record already exists.

If data is already present:

```text
Sample data already exists. Skipping loaddata.
```

If the database is empty:

```text
Loading sample data...
```

and the fixture is loaded.

This prevents duplicate fixture loading when the PostgreSQL volume already contains data.

---

# Why Check `Mars`?

`Mars` is used as the existence check because it is the primary model of the application and the project expects a Mars record to exist whenever the sample dataset has been initialized.

The check is therefore effectively being used as a simple seed-state indicator.

---

# Why `tail -n 1`?

The shell command:

```bash
python manage.py shell -c "from main.models import Mars; print(Mars.objects.exists())"
```

can produce additional informational output from Django before printing:

```text
True
```

For example:

```text
20 objects imported automatically (use -v 2 for details).
True
```

The shell condition needs to compare only the final value.

Therefore:

```bash
| tail -n 1
```

extracts the last line:

```text
True
```

and allows the shell condition to work reliably.

---

# Database Persistence Behavior

The Docker setup deliberately separates container lifecycle from database lifecycle.

```text
docker compose down
        │
        ├── Containers removed
        │
        └── postgres_data preserved
```

When the application starts again, the existing PostgreSQL data remains available.

In contrast:

```text
docker compose down -v
        │
        ├── Containers removed
        │
        └── postgres_data removed
```

The next startup therefore creates a fresh database and loads the fixture again.

This behavior is intentional.

---

# `.dockerignore`

The project prevents unnecessary local files from being copied into the Docker build context.

The `.dockerignore` contains entries such as:

```text
__pycache__
*.pyc
*.pyo
*.pyd
.git
.gitignore
venv
denv
.env
```

This keeps the Docker build context smaller and prevents local development environments and Git metadata from being copied into the image.

---

# Project Structure

The core Dockerized project structure is:

```text
mars-explorer/
│
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
├── .dockerignore
│
└── main/
    ├── models.py
    ├── views.py
    ├── signals.py
    └── mars_data.json
```

The project also contains the Django templates, static assets, migrations, and standard Django project configuration required by the application.

---

# Cache Lifecycle

A typical cached dataset follows this lifecycle:

```text
                    ┌──────────────────┐
                    │  HTTP Request     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Check Redis     │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
             Cache Hit              Cache Miss
                 │                       │
                 ▼                       ▼
          Return cached data       Query PostgreSQL
                                         │
                                         ▼
                                  Store in Redis
                                         │
                                         ▼
                                  Return fresh data
```

If the underlying database object changes:

```text
PostgreSQL object changes
          │
          ▼
     Django signal
          │
          ▼
    Delete cache key
          │
          ▼
      Next request
          │
          ▼
      Cache miss
          │
          ▼
    Fresh DB query
          │
          ▼
     Redis updated
```

---

# Cache Hit vs Cache Miss

Consider:

```python
mars = cache.get_or_set(
    "mars:planet",
    Mars.objects.first,
    timeout=3600,
)
```

### First request

```text
Redis:
mars:planet → missing

PostgreSQL:
SELECT ...

Redis:
mars:planet → Mars object

Response:
Mars object
```

### Subsequent request

```text
Redis:
mars:planet → exists

PostgreSQL:
No query required for this cached object

Response:
Cached Mars object
```

This is the primary performance benefit demonstrated by the project.

---

# Measuring Database Queries

During development, database query counts can be inspected through Django's database connection:

```python
from django.db import connection

connection.queries_log.clear()

# application logic

print("DATABASE QUERIES:", len(connection.queries))
```

This can be useful when verifying that a cache hit avoids the expected database queries.

For example, if the relevant data is already cached, a request can produce:

```text
DATABASE QUERIES: 0
```

for the measured section/request.

The query counter represents database queries recorded by Django during that context; it should therefore be interpreted according to where and when the counter is reset.

---

# Why Cache the Entire Collection?

For this project, several models are small and relatively static.

For example:

```text
Mission
Rover
LandingSite
GeographicFeature
Weather
```

Instead of creating one Redis key for every record, the application stores the complete collection under one key:

```text
mars:missions
mars:rovers
mars:landing_sites
mars:geographic_features
mars:weather
```

This keeps the implementation simple and reduces the number of Redis operations required to render a page.

For a small, mostly static dataset, this is a reasonable trade-off.

---

# Alternative Caching Strategies

The collection-level caching strategy used by Mars Explorer is not the only standard way to cache database data.

The appropriate strategy depends on:

* Dataset size
* Update frequency
* Access patterns
* Required cache granularity
* Invalidation complexity
* Number of database queries
* Memory usage

Two important alternatives are object-level caching and queryset/page-level caching.

---

## Object-Level Caching

Instead of storing an entire collection:

```text
mars:missions
    ↓
[Mission 1, Mission 2, Mission 3, ...]
```

each object can have its own cache entry:

```text
mars:mission:1 → Mission 1
mars:mission:2 → Mission 2
mars:mission:3 → Mission 3
```

This provides much more granular invalidation.

For example, if Mission 2 changes:

```python
cache.delete("mars:mission:2")
```

Mission 1 and Mission 3 remain cached.

---

## Example: Object-Level Mission Caching

A Django view could use an object-level strategy like this:

```python
from django.core.cache import cache
from django.shortcuts import render
from .models import Mission


def ops(request):
    missions = []

    mission_ids = Mission.objects.values_list("id", flat=True)

    for mission_id in mission_ids:
        mission = cache.get_or_set(
            f"mars:mission:{mission_id}",
            lambda mission_id=mission_id: Mission.objects.get(id=mission_id),
            timeout=3600,
        )

        missions.append(mission)

    return render(
        request,
        "main/ops.html",
        {
            "missions": missions,
        },
    )
```

The cache would look conceptually like:

```text
mars:mission:1 → Mission 1
mars:mission:2 → Mission 2
mars:mission:3 → Mission 3
```

If Mission 2 is updated:

```python
cache.delete(f"mars:mission:{instance.id}")
```

only its cache entry is invalidated.

---

# Object-Level Caching: Advantages

Object-level caching is useful when:

* Individual records are frequently requested
* Individual records change independently
* The dataset is large
* Granular invalidation is important
* Different requests need different subsets of the data

For a large dataset, storing every record independently can provide significant flexibility.

---

# Object-Level Caching: Disadvantages

The strategy also introduces additional complexity.

The example above first needs:

```python
Mission.objects.values_list("id", flat=True)
```

to discover which objects exist.

Then, on cache misses, individual database queries can occur:

```text
Query for IDs
      +
Query for Mission 1
      +
Query for Mission 2
      +
Query for Mission 3
      +
...
```

If many objects are missing from the cache, this can result in an N+1-style access pattern.

Therefore, object-level caching is not automatically better.

For a small dataset such as the one in Mars Explorer, caching the complete collection is simpler and can be more efficient.

---

# Collection-Level vs Object-Level Caching

The difference can be summarized as:

```text
Collection-Level
────────────────────────────
mars:missions
    └── [1, 2, 3, 4, 5]


Object-Level
────────────────────────────
mars:mission:1 → 1
mars:mission:2 → 2
mars:mission:3 → 3
mars:mission:4 → 4
mars:mission:5 → 5
```

### Collection-Level

Advantages:

* Simple implementation
* Fewer Redis keys
* Easy page rendering
* Usually fewer database queries on a cold cache
* Good for small/static datasets

Disadvantages:

* Updating one object invalidates the entire collection
* A large collection can consume more memory per cache value
* Every consumer receives the same cached collection

### Object-Level

Advantages:

* Granular invalidation
* Efficient for frequently accessed individual records
* Individual objects can expire independently
* Better suited to large or highly dynamic datasets

Disadvantages:

* More Redis keys
* More complex invalidation
* Potentially more database queries
* More complicated cache population logic

---

# Other Standard Caching Strategies

Redis caching can also be implemented at other levels depending on the application.

### View-Level Caching

Instead of caching model data manually, an entire rendered response can be cached.

Conceptually:

```text
Request
   ↓
Cache rendered response
   ↓
Return HTML
```

This can be useful for pages whose complete output is identical for many users.

However, it is less granular than caching individual datasets.

---

### Template Fragment Caching

Only a specific portion of a page can be cached.

For example:

```text
Page
├── Dynamic navigation
├── Cached Mars information
└── Dynamic footer
```

This is useful when only one section of a page is expensive to render.

---

### Low-Level Django Cache API

The current project already uses Django's low-level cache API:

```python
cache.get_or_set(...)
cache.delete(...)
```

This approach provides the developer with explicit control over:

* What is cached
* Cache keys
* TTL
* Cache invalidation
* Cache granularity

This is particularly appropriate for demonstrating Redis caching concepts.

---

# Choosing the Right Strategy

There is no universally superior caching strategy.

A useful rule of thumb is:

```text
Small + static collection
        ↓
Cache the collection


Large + independently accessed objects
        ↓
Cache individual objects


Identical complete responses
        ↓
Consider view-level caching


Only one expensive page section
        ↓
Consider fragment caching
```

Mars Explorer deliberately uses collection-level caching for most datasets because the data is small, mostly static, and displayed as complete collections.

Phobos and Deimos demonstrate object-level caching because they are naturally addressed as individual entities.

This combination makes the project useful not only as an application but also as a practical demonstration of different caching granularities.

---

# Cache Invalidation vs TTL

Two common mechanisms are used to keep cached data fresh.

## TTL

TTL means Time To Live.

For example:

```python
timeout=3600
```

means:

```text
Cache created
     ↓
60 minutes
     ↓
Cache expires
     ↓
Next request retrieves fresh data
```

TTL is simple and provides an automatic expiration mechanism.

---

## Explicit Invalidation

Explicit invalidation deletes a cache entry when its underlying data changes.

For example:

```python
cache.delete("mars:missions")
```

This allows the application to refresh the cache immediately instead of waiting for the TTL to expire.

Mars Explorer uses both approaches:

```text
TTL
+
Signal-Based Invalidation
```

This provides a practical balance between simplicity and freshness.

---

# Design Decisions

Several implementation decisions were intentionally made based on the characteristics of the project.

### PostgreSQL instead of Redis as primary storage

PostgreSQL provides durable relational storage and remains the source of truth.

### Redis as a cache

Redis is used to reduce repeated database access rather than replace PostgreSQL.

### Cache-Aside

The application explicitly controls when data is read from or written to the cache.

### Collection-level caching

Small, mostly static collections are cached as complete datasets.

### Object-level caching for moons

Phobos and Deimos demonstrate a more granular caching strategy.

### Signal-based invalidation

Relevant cache keys are deleted when their database records change.

### TTL

A one-hour expiration provides an additional safety mechanism.

### Docker Compose

The entire application stack is represented as independent services.

### Named PostgreSQL volume

Persistent database data survives container recreation.

### No Redis volume

The cache is disposable and can be reconstructed from PostgreSQL.

### Fixture-based initialization

The repository contains a known initial dataset that can be loaded automatically into a fresh database.

---

# Technology Stack

| Technology       | Purpose                          |
| ---------------- | -------------------------------- |
| Python           | Application programming language |
| Django           | Web framework                    |
| PostgreSQL       | Primary relational database      |
| Redis            | Caching layer                    |
| django-redis     | Django Redis cache backend       |
| Docker           | Containerization                 |
| Docker Compose   | Multi-container orchestration    |
| HTML/CSS/JS      | Frontend                         |
| Django Templates | Server-side rendering            |

## Frontend Template Attribution

The frontend of this project is based on a pre-designed template from [Free Website Templates](https://www.freewebsitetemplates.com/). The original template was customized and adapted for this project, including modifications to the existing layout and styling, as well as adding and removing sections to meet the project's requirements and overall design.

---

# Summary

Mars Explorer is a Django application focused on Mars exploration data and practical backend architecture.

Its most important architectural principle is the separation between persistent data and cached data:

```text
                 ┌─────────────────┐
                 │   PostgreSQL    │
                 │ Source of Truth │
                 └────────┬────────┘
                          │
                          │ Cache Miss
                          ▼
                 ┌─────────────────┐
                 │      Redis      │
                 │      Cache      │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     Django      │
                 │  Application    │
                 └─────────────────┘
```

The application uses Cache-Aside caching, explicit cache keys, TTL-based expiration, and signal-driven invalidation.

Most datasets are cached as complete collections because the application's data is relatively small and static. Individual Mars moons are cached separately to demonstrate object-level caching and granular invalidation.

Docker Compose packages Django, PostgreSQL, and Redis into a reproducible multi-service architecture, while a persistent PostgreSQL volume protects the application's database from container recreation.

The result is a compact but complete demonstration of:

* Django application development
* PostgreSQL integration
* Redis caching
* Cache-Aside architecture
* Cache invalidation
* Django signals
* Docker containerization
* Docker Compose networking
* Database persistence
* Automated migrations
* Fixture-based initialization
* Multiple caching strategies and their trade-offs
