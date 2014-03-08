test:
	pip install pytest pytest-flakes pytest-pep8
	DJANGO_SETTINGS_MODULE=hydraclient.test_settings py.test --doctest-modules hydraclient --flakes --pep8
