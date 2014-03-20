from django.conf.urls import patterns, url


def service_urlpatterns(cfg_url):
    return patterns(
        'hydraclient.contrib.django.hydraclient.views',
        url(
            '.*',
            'resource',
            kwargs={"cfg_url": cfg_url}
        )
    )
