from ..models import Participant, SecondaryEmail


def merge_participants(old: Participant, new: Participant) -> Participant:
    """This function merges a new participant object into a new one,
    by following the following steps:

    - The new email address is added as a secondary address to the old one
    - Adds all secondary emails from the new object to the old object
    - Moves experiments from new to old. TODO: <----
    - Updates specific criteria
    - Updates name, phone number and social_status
    """

    # Move the new email to the old as a secondary email
    secondary_email = SecondaryEmail()
    secondary_email.email = new.email
    secondary_email.participant = old
    secondary_email.save()

    # Merge new secondary emails into old, if they are not yet there
    for secondary_email in new.secondaryemail_set.all():
        # If the new email is not yet known in the old object
        if not old.secondaryemail_set.filter(email=secondary_email.email):
            secondary_email.participant = old
            secondary_email.save()
        else:
            secondary_email.delete()

    # TODO: transfer experiments

    # Merge specific criteria answers
    for criterium_answer in new.criteriumanswer_set.all():
        # If the new email is not yet known in the old object
        old_answer = old.criteriumanswer_set.filter(
                criterium=criterium_answer.criterium
        )
        if old_answer:
            old_answer = old_answer[0]
            old_answer.answer = criterium_answer.answer
            old_answer.save()
            criterium_answer.delete()
        else:
            criterium_answer.participant = old
            criterium_answer.save()

    # Update attributes
    old.name = new.name
    old.phonenumber = new.phonenumber
    old.social_status = new.social_status
    old.save()

    # Finally, delete the new object
    new.delete()

    return old
