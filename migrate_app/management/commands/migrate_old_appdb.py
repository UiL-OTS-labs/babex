from django.core.management.base import BaseCommand
from migrate_app.utils.migrate_users import migrate_admins, migrate_leaders
from migrate_app.utils.migrate_misc import create_migration_location
from migrate_app.utils.migrate_participants import migrate_participants


class Command(BaseCommand):
    help = "Migrates all data from the old application database into this " \
           "application's database"

    def handle(self, *args, **options):
        print('Migrating admins... ', end='')
        migrate_admins()
        print('Done!', end='\n\n')

        print('Migrating leaders... ', end='')
        migrate_leaders()
        print('Done!', end='\n\n')

        print('Creating migration location object... ', end='')
        create_migration_location()
        print('Done!', end='\n\n')

        print('Migrating participants... ', end='')
        migrate_participants()
        print('Done!', end='\n\n')

