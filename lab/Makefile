test:
	DJANGO_SETTINGS_MODULE=ppn_backend.settings pytest --ignore=integration_tests $(PYTEST_ARGS)

testint:
	DJANGO_SETTINGS_MODULE=ppn_backend.settings pytest -k integration_tests --tracing retain-on-failure $(PYTEST_ARGS)
