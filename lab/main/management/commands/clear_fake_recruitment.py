
from django.core.management.base import BaseCommand, CommandError
from participants.simulate import remove_simulated_participants


class Command(BaseCommand):
    """
    Allow mangage.py to remove participants added with fake_recruitement
    """
    help = 'Generate participants for testing purposes, NOT for production'

    def handle(self, *args, **options):
        """Validates provided arguments"""
        remove_simulated_participants()



