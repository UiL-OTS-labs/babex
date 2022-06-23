from ..models import Participant, SecondaryEmail
from auditlog.enums import UserType, Event
import auditlog.utils.log as auditlog


def merge_participants(existing: Participant,
                       new: Participant,
                       performing_user=None) -> Participant:
    """This function merges a new participant object into an existing one,
    by following the following steps:

    - The existing email address is added as a secondary address
    - Adds all secondary emails from the new object to the existing object
    - Moves experiments from new to existing.
    - Moves comments from new to existing
    - Updates specific criteria
    - Updates name, email, phone number and social_status
    """

    # Copy the existing email to a secondary email
    secondary_email = SecondaryEmail()
    secondary_email.email = existing.email
    secondary_email.participant = existing
    secondary_email.save()

    # Get all existing emails from the existing set
    # We cannot compare emails in the database, as the database contains
    # encrypted values only
    existing_emails = [x.email for x in existing.secondaryemail_set.all()]

    # Merge new secondary emails into existing, if they are not yet there
    for secondary_email in new.secondaryemail_set.all():
        # If the new email is not yet known in the existing object
        if secondary_email.email in existing_emails:
            secondary_email.delete()
        else:
            secondary_email.participant = existing
            secondary_email.save()

    # Move all appointments to the existing model.
    # In theory this can result in doubles in an experiment, but we're assuming
    # no participant has managed to turn up twice for the same experiment.
    for appointment in new.appointments.all():
        appointment.participant = existing
        appointment.save()

    # Merge specific criteria answers
    for criterion_answer in new.criterionanswer_set.all():
        # If the new email is not yet known in the existing object
        existing_answer = existing.criterionanswer_set.filter(
            criterion=criterion_answer.criterion
        )
        if existing_answer:
            existing_answer = existing_answer[0]
            existing_answer.answer = criterion_answer.answer
            existing_answer.save()
            criterion_answer.delete()
        else:
            criterion_answer.participant = existing
            criterion_answer.save()

    # Move comments
    for comment in new.comment_set.all():
        comment.participant = existing
        comment.save()

    # Transfer account if 'existing' does not have one but 'new' does.
    # If both have an account, 'existing' should take priority
    # If existing has an account, but new does not, no steps are needed ;)
    if not existing.api_user and new.api_user:
        api_user = new.api_user
        api_user.participant = existing
        api_user.save()
        new.api_user = None

    # Finally, delete the new object
    new.delete()

    # Update attributes
    existing.name = new.name
    existing.phonenumber = new.phonenumber
    existing.social_status = new.social_status
    existing.email = new.email
    existing.save()


    # Log the modification
    _log(existing, new, performing_user)

    return existing


def _log(existing: Participant,
         new: Participant,
         performing_user=None) -> None:

    message = "Admin merged participant '{}' into '{}'".format(new, existing)

    auditlog.log(
        Event.MODIFY_DATA,
        message,
        performing_user,
        UserType.ADMIN,
    )
