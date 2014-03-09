test:
	pip install pytest pytest-flakes pytest-pep8
	DJANGO_SETTINGS_MODULE=hydraclient.contrib.django.hydraclient.test_settings py.test --doctest-modules hydraclient --flakes --pep8

django-weather-web:
	./examples/django-weather-web/manage.py runserver
