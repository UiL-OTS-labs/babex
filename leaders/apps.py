from django.apps import AppConfig


class LeadersConfig(AppConfig):
    name = 'leaders'

    def ready(self):
        import leaders.signals  # NoQA
