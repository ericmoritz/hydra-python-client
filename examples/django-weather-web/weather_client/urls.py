from hydraclient.contrib.django.hydraclient.urls import service_urlpatterns
from django.conf import settings

urlpatterns = service_urlpatterns(settings.WEATHER_BASE_URL)
