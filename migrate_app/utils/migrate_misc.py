from experiments.models import Location
from ..defs import MIGRATE_LOCATION_NAME


def create_migration_location():
    if not Location.objects.filter(name=MIGRATE_LOCATION_NAME).exists():
        l = Location()
        l.name = MIGRATE_LOCATION_NAME
        l.save()