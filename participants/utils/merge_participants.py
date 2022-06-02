from ..models import Participant, SecondaryEmail
from auditlog.enums import UserType, Event
import auditlog.utils.log as auditlog


def merge_participants(old: Participant,
                       new: Participant,
                       performing_user=None) -> Participant:
    """This function merges a new participant object into a new one,
    by following the following steps:

    - The new email address is added as a secondary address to the old one
    - Adds all secondary emails from the new object to the old object
    - Moves experiments from new to old.
    - Updates specific criteria
    - Updates name, phone number and social_status
    """

    # Move the new email to the old as a secondary email
    secondary_email = SecondaryEmail()
    secondary_email.email = new.email
    secondary_email.participant = old
    secondary_email.save()

    # Get all existing emails from the old set
    # We cannot compare emails in the database, as the database contains
    # encrypted values only
    existing_emails = [x.email for x in old.secondaryemail_set.all()]

    # Merge new secondary emails into old, if they are not yet there
    for secondary_email in new.secondaryemail_set.all():
        # If the new email is not yet known in the old object
        if secondary_email.email in existing_emails:
            secondary_email.delete()
        else:
            secondary_email.participant = old
            secondary_email.save()

    # Move all appointments to the old model.
    # In theory this can result in doubles in an experiment, but we're assuming
    # no participant has managed to turn up twice for the same experiment.
    for appointment in new.appointments.all():
        appointment.participant = old
        appointment.save()

    # Merge specific criteria answers
    for criterion_answer in new.criterionanswer_set.all():
        # If the new email is not yet known in the old object
        old_answer = old.criterionanswer_set.filter(
            criterion=criterion_answer.criterion
        )
        if old_answer:
            old_answer = old_answer[0]
            old_answer.answer = criterion_answer.answer
            old_answer.save()
            criterion_answer.delete()
        else:
            criterion_answer.participant = old
            criterion_answer.save()

    # Move comments
    for comment in new.comment_set.all():
        comment.participant = old
        comment.save()

    # Transfer account if 'old' does not have one but 'new' does.
    # If both have an account, 'old' should take priority
    # If old has an account, but new does not, no steps are needed ;)
    if not old.api_user and new.api_user:
        api_user = new.api_user
        api_user.participant = old
        api_user.save()
        new.api_user = None

    # Finally, delete the new object
    new.delete()

    # Update attributes
    old.name = new.name
    old.phonenumber = new.phonenumber
    old.social_status = new.social_status
    old.save()


    # Log the modification
    _log(old, new, performing_user)

    return old


def _log(old: Participant,
         new: Participant,
         performing_user=None) -> None:

    message = "Admin merged participant '{}' into '{}'".format(new, old)

    auditlog.log(
        Event.MODIFY_DATA,
        message,
        performing_user,
        UserType.ADMIN,
    )
