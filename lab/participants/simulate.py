"""This module is added to simulate a recruitment, it's main purpose is to
fill the database with participants for testing this app. Also the utilities
to undo the changes are provided.
"""

import random
from datetime import datetime, timedelta
from typing import List

from faker import Faker

from .models import Language, Participant

DEFAULT_PREFIX = "F_"

fake = Faker()


def _generate_random_languages() -> list[Language]:
    language_names = ["Nederlands", "Engels", "Frans", "Spaans", "Duits", "Arabisch"]
    languages = [Language.objects.get_or_create(name=lang)[0] for lang in language_names]
    return random.sample(languages, k=random.randint(1, 4))


def simulate_recruitment(number: int, date: datetime, day_range: int = 60, name_prefix=DEFAULT_PREFIX):
    """Simulate a recruitment this will add participant to the database. It's
    useful for generating participants to give some body to the database.

    The name_prefix gives a unlikely name for a baby in order to remove it
    from the database.

    The baby's are born roughly in a uniform interval of day_range around date
    uniform.

    TODO check whether it's possible to save all objects at once

    Keyword arguments:
    :param int number: the number of participants to create
    :param datetime date: The date around which the participants are born
    :param days_spread: The number of days around the data the children are born
    :param str name_prefix: A prefix to prepend to the participant name
    """
    for i in range(number):
        name = DEFAULT_PREFIX + fake.name()
        email = "generated-{}@gen.mars".format(random.randint(int(1e6), int(1e7)))
        days_add = int(round((random.random() - 0.5) * day_range))
        birth_date = date + timedelta(days=days_add)
        sex = random.choice(list(Participant.Sex))
        pregnancy_duration = random.choice(list(Participant.PregnancyDuration))
        birth_weight = random.choice(list(Participant.BirthWeight))
        dyslexic_parent = random.choice(list(Participant.WhichParent))
        tos_parent = random.choice(list(Participant.WhichParent))

        pp = Participant.objects.create(
            name=name,
            sex=sex,
            birth_date=birth_date,
            birth_weight=birth_weight,
            pregnancy_duration=pregnancy_duration,
            parent_first_name=fake.first_name(),
            parent_last_name=fake.last_name(),
            email=email,
            phonenumber=fake.phone_number(),
            phonenumber_alt=fake.phone_number(),
            dyslexic_parent=dyslexic_parent,
            tos_parent=tos_parent,
            save_longer=random.choice([True, False]),
            english_contact=random.choice([True, False]),
            email_subscription=random.choice([True, False]),
        )
        pp.languages.set(_generate_random_languages())
        pp.save()


def _get_simulated_participants(prefix) -> List[Participant]:
    """
    The encrypted fields are a bit unfriendly with Model.objects.filter()
    This touches the fields in order to decrypt the values.
    This method finds the fake pp's in order to delete them
    """
    pps = Participant.objects.all()
    return [pp for pp in pps if pp.name.startswith(prefix)]


def remove_simulated_participants(prefix: str = DEFAULT_PREFIX):
    """This function attempts to delete participants created with
    simulate_recruitment
    """
    rm_pps = _get_simulated_participants(prefix)
    for pp in rm_pps:
        pp.data.delete()
        pp.delete()
