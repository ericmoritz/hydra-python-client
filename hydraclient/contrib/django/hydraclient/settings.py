from hydraclient.core.settings import DEFAULT_JSONLD_CONTEXT
from django.conf import settings

DEFAULT_JSONLD_CONTEXT = getattr(
    settings, 
    "DEFAULT_JSONLD_CONTEXT", 
    DEFAULT_JSONLD_CONTEXT
)
