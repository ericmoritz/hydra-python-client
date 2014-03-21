from hydraclient.core.settings import DEFAULT_JSONLD_CONTEXT
import os

###===================================================================
### Added for hydraclient.contrib.django.hydraclient
###===================================================================
CONFIG_URL=os.environ['CONFIG_URL']

DEFAULT_JSONLD_CONTEXT = dict(
    DEFAULT_JSONLD_CONTEXT,
    **{
        "weather": "http://vocab-ld.org/vocab/weather#"
    }
)

TEMPLATE_CONTEXT_PROCESSORS = (
"django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.core.context_processors.request",
"django.contrib.messages.context_processors.messages",
)

INSTALLED_APPS = [
    'hydraclient.contrib.django.hydraclient',
    'weather',
]

APPEND_SLASH = False
ROOT_URLCONF = "weather_client.urls"
DEBUG=True
TEMPLATE_DEBUG=True
