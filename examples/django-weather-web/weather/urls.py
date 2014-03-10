from hydraclient.contrib.django.hydraclient.urls import service_urlpatterns
from django.conf import settings
import os

urlpatterns = service_urlpatterns(settings.WEATHER_BASE_URL)
