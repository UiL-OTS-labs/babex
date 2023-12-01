"""This module is added to simulate a recruitment, it's main purpose is to
fill the database with participants for testing this app. Also the utilities
to undo the changes are provided.
"""

import random
from datetime import datetime, timedelta
from typing import List

from .models import Language, Participant

DEFAULT_PREFIX = "Gener@t3d"
DEFAULT_PHONE = "06-11"


def _generate_name(prefix: str, num: int) -> str:
    """Generate a prefixed name for a generated participant"""
    letter_pick = "abcdefghijklmnopqrstuvwxyz"
    num_letters = random.choice(range(5, 13))
    name = "".join([prefix, "_", str(num), "_"])
    uniq = "".join([random.choice(letter_pick) for i in range(num_letters)])

    return "".join([name, uniq])


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
        name = _generate_name(name_prefix, i)
        email = "generated-{}@gen.mars".format(random.randint(int(1e6), int(1e7)))
        phonenumber = DEFAULT_PHONE
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
            parent_first_name="parent_" + name,
            parent_last_name="parent_" + name,
            email=email,
            phonenumber=phonenumber,
            phonenumber_alt=phonenumber,
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
    return [pp for pp in pps if pp.name.startswith(prefix) and pp.phonenumber == DEFAULT_PHONE]


def remove_simulated_participants(prefix: str = DEFAULT_PREFIX):
    """This function attempts to delete participants created with
    simulate_recruitment
    """
    rm_pps = _get_simulated_participants(prefix)
    for pp in rm_pps:
        pp.delete()
