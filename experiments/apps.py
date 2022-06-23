from django.apps import AppConfig


class ExperimentsConfig(AppConfig):
    name = 'experiments'

    def ready(self):
        import experiments.signals