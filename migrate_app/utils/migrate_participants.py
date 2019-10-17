from ..models import Participants as OldParticipant
from participants.models import Participant, SecondaryEmail


def migrate_participants():
    old_participants = OldParticipant.objects.all()

    for old_participant in old_participants:  # type: OldParticipant
        if Participant.objects.filter(email=old_participant.email).exists():
            print("\nParticipant with email {} already exists in the new DB! "
                  "Skipping...".format(old_participant.email))
            continue

        new_participant = Participant()

        new_participant.email = old_participant.email
        new_participant.name = old_participant.name
        new_participant.language = old_participant.language
        new_participant.birth_date = old_participant.date_of_birth
        new_participant.multilingual = _get_multilingual(old_participant)
        new_participant.phonenumber = old_participant.phonenumber
        new_participant.handedness = _get_handedness(old_participant)

        new_participant.dyslexic = _yes_no_null_mapper(old_participant,
                                                       'dyslectic')

        new_participant.sex = old_participant.sex
        new_participant.social_status = _get_social_status(old_participant)

        new_participant.email_subscription = _yes_no_null_mapper(
            old_participant,
            'email_subscription'
        )
        new_participant.capable = _yes_no_null_mapper(
            old_participant,
            'capable'
        )

        new_participant.save()

        for email in old_participant.email_secondary.split(','):
            se = SecondaryEmail()
            se.participant = new_participant
            se.email = email
            se.save()


def _yes_no_null_mapper(old_participant, attribute):
    value = getattr(old_participant, attribute)

    if value == 'yes':
        return True
    elif value == 'no':
        return False
    else:
        return None


def _get_handedness(old_participant):
    if old_participant.handedness == 'right':
        return 'R'
    elif old_participant.handedness == 'left':
        return 'L'
    else:
        return None


def _get_multilingual(old_participant: OldParticipant):
    if old_participant.multiple_lang == 'many':
        return True
    elif old_participant.multiple_lang == 'one':
        return False
    else:
        return None


def _get_social_status(old_participant: OldParticipant):
    if old_participant.social_role == 'student':
        return 'S'
    if old_participant.social_role is None or old_participant.social_role == '':
        return None

    return 'O'