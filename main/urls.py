from django.urls import path
from . import views

urlpatterns = [
   path('', views.home_page, name='home'),
   path('overview/', views.overview_page, name='overview'),
   path('surface/', views.surface_page, name='surface'),
   path('moons/', views.moons_page, name='moons'),
   path('missions/', views.ops_page, name='missions')
]
