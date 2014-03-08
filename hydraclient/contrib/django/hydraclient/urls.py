from django.conf.urls import patterns, url


def service_urlpatterns(base_irl):
    return patterns(
        'hydraclient.contrib.django.hydraclient.views',
        url(
            '(.*)',
            'resource',
            kwargs={"base_irl": base_irl}
        )
    )
