from hydraclient.contrib.django.hydraclient.urls import service_urlpatterns
from django.conf.urls import patterns, url, include
from django.conf import settings

urlpatterns = service_urlpatterns(settings.CONFIG_URL)
