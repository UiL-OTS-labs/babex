'''This module is added to simulate a recruitment, it's main purpose is to
fill the database with participants for testing this app.
'''

from .models import Participant
import random
from datetime import datetime
from datetime import timedelta
from typing import List


DEFAULT_PREFIX = "Gener@t3d"
DEFAULT_PHONE = "06-11" 


def _generate_name(prefix: str, num: int) -> str:
    """ Generate a prefixed name for a generated participant"""
    letter_pick = "abcdefghijklmnopqrstuvwxyz"
    num_letters = random.choice(range(5,13))
    name = "".join([prefix, "_", str(num), "_"])
    uniq = "".join([random.choice(letter_pick) for i in range(num_letters)])

    return "".join([name, uniq])


def _generate_parent_dylexia(chance=.05) -> bool:
    """gives a chance of haveing a parent with dyslexia"""
    return random.random() < chance


def simulate_recruitment(
        number:int,
        date : datetime, 
        day_range: int = 60,
        name_prefix=DEFAULT_PREFIX
        ):
    """Simulate a recruitment this will add participant to the database. It's
    useful for generating participants to give some body to the database.

    The name_prefix gives a unlikely name for a baby in order to remvove it
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
    WEEK_MU, WEEK_SIGMA = 40, 2

    for i in range(number):

        name = _generate_name(name_prefix, i)
        email = "generated-{}@gen.mars".format(random.randint(1e6,1e7))
        dyslexic_parent = _generate_parent_dylexia()
        multilingual = _generate_parent_dylexia()
        pweeks = int(round(random.normalvariate(WEEK_MU, WEEK_SIGMA)))
        pdays = pweeks * 7 + random.choice(list(range(7)))
        birth_weight = random.normalvariate(3500, 1000)
        phonenumber = DEFAULT_PHONE
        days_add = int(round((random.random() - .5) * day_range))
        birth_date = date + timedelta(days=days_add)
        gender = random.choice("FM")
        city = "".join(reversed("Utrecht-City"))

        pp = Participant.objects.create(
                email = email,
                name = name,
                language = "BLanguage",
                dyslexic_parent = dyslexic_parent,
                birth_date = birth_date,
                phonenumber = phonenumber,
                sex=gender,
                email_subscription=random.choice([True, False]),
                birth_weight=birth_weight,
                pregnancy_weeks = pweeks,
                pregnancy_days = pdays,
                parent_name = "parent_" + name,
                city = city
                )

        pp.save()

def _get_simulated_participants(prefix) -> List[Participant]:
    """
    The encrypted fields are a bit unfriendly with Model.objects.filter()
    This touches the fields in order to decrypt the values.
    This method finds the fake pp's in order to delete them
    """
    pps = Participant.objects.all()
    city = "".join(reversed("Utrecht-City"))
    start = prefix[0].upper() + prefix[1:]
    def check_pp(pp: Participant):
        if pp.name[:len(prefix)] == prefix and \
           pp.phonenumber == DEFAULT_PHONE and \
           pp.city == city:
               return True
        return False

    l = [pp for pp in pps if check_pp(pp)]
    return l

def remove_simulated_participants(prefix: str= DEFAULT_PREFIX):
    """This function attempts to delete participants created with
    simulate_recruitment
    """
    rm_pps = _get_simulated_participants(prefix)
    for pp in rm_pps:
        pp.delete()





