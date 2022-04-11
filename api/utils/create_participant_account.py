from enum import Enum

from django.conf import settings

from participants.utils.mailinglist_unsubscribe import get_login_page_url
from uil.core.utils.mail import send_template_email

from api.auth.models import ApiUser, ApiGroup, UserToken
from api.utils import get_reset_links
from comments.utils import add_system_comment
from leaders.utils import _get_tomorrow
from participants.models import Participant
from main.utils import get_supreme_admin
from participants.utils import get_mailinglist_unsubscribe_url

SYSTEM_MESSAGES = {
    'multiple_participants': "A user tried to create an account, but the "
                             "email that they specified is used by multiple "
                             "different participants. This participant is a "
                             "newly created ony, and the other participants "
                             "with the same email where: {}"
}


class ReturnValues(Enum):
    OK = 0
    ACCOUNT_ALREADY_EXISTS = 1


def create_participant_account(email: str,
                               name: str,
                               multilingual: bool = None,
                               language: str = None,
                               dyslexic: bool = None,
                               mailing_list: bool = False,
                               password: str = None) -> 'ReturnValues':

    email = email.strip()
    # Get a list of participants that use this email
    participants = Participant.objects.find_by_email(email)

    # Count the number of results
    num_found_participants = len(participants)

    # If we found more than one, create a new participant and add a warning
    # comment for the admins
    if num_found_participants > 1:
        participant = _create_new_participant(email, name, multilingual,
                                              language, dyslexic, mailing_list)

        message = SYSTEM_MESSAGES['multiple_participants'].format(
            ", ".join([str(x) for x in participants])
        )
        add_system_comment(participant, message)

        new_participant = True

    # If we found none, just create a new one
    elif num_found_participants < 1:  # or == 0, doesn't matter
        participant = _create_new_participant(email, name, multilingual,
                                              language, dyslexic, mailing_list)
        new_participant = True
    else:
        # If we found 1, we can use that one
        participant = participants[0]

        new_participant = False

        # Switch emails if needed
        if participant.email != email:
            _switch_main_email(participant, email)

    # Create a queryset to check if this email is already used
    api_user = ApiUser.objects.get_by_email(email)

    # If this participant already has an attached account
    if participant.api_user:
        # Stop and return that the account already exists
        return ReturnValues.ACCOUNT_ALREADY_EXISTS

    # Check if we have an existing api user with the same email (can happen
    # with leaders for example)
    elif api_user:
        # If there already is an account with this email
        user = api_user

        # Check if this account is already a participant
        if user.is_participant:
            # Delete the new one (if it's new)
            if new_participant:
                participant.delete()

            # Stop and return that the account already exists
            return ReturnValues.ACCOUNT_ALREADY_EXISTS

        # Otherwise, add the relevant participant data to this account (as it
        # might be a leader)
        else:
            _add_participant_group(user)
            participant.api_user = user
            participant.save()
            _send_existing_account_mail(participant, user)

    # If there's no account associated in any way, create one!
    else:
        _create_new_account(participant, password)

    return ReturnValues.OK


def _create_new_participant(email: str,
                            name: str,
                            multilingual: bool = None,
                            language: str = None,
                            dyslexic: bool = None,
                            mailing_list: bool = False) -> Participant:
    """
    This function creates (and saves) a new participant object based upon
    the parameters.
    """

    participant = Participant()
    participant.email = email
    participant.name = name
    participant.multilingual = multilingual
    participant.language = language
    participant.dyslexic = dyslexic
    participant.email_subscription = mailing_list

    participant.save()

    return participant


def _create_new_account(participant: Participant, password: str = None) -> None:
    """
    This function creates (and saves) a new ApiUser and attaches it to the
    given participant. If no password is specified, the user will receive an
    email giving them instructions on how to set one.

    :param participant: The participant object to create the account for
    :param password: (optional) the password for this user
    :return: Nada!
    """
    user = ApiUser()

    user.email = participant.email
    user.save()

    participant.api_user = user
    participant.save()

    _add_participant_group(user)

    token = UserToken.objects.create(
        user=user,
        expiration=_get_tomorrow(),
        type=UserToken.PASSWORD_RESET,
    )

    link, alternative_link = get_reset_links(token.token)

    context = {
        'participant': participant,
        'unsub_link': get_mailinglist_unsubscribe_url(participant),
        'login_link': get_login_page_url(),
        'set_password_link': link,
        'has_password': False,
    }

    if password:
        user.set_password(password)
        user.save()
        context['has_password'] = True

    send_template_email(
        [participant.email],
        "UiL OTS: Account aangemaakt",
        'api/mail/new_account',
        context,
        get_supreme_admin().email
    )


def _send_existing_account_mail(
        participant: Participant,
        user: ApiUser
) -> None:
    """This method sends an e-mail to users which are already known as a
    leader, but have now created a participant. It informs them of the fact
    that they can use their existing account.

    Previously, this case resulted in no mail at all, which is confusing.
    """

    link = None

    if not user.is_ldap_account:
        token = UserToken.objects.create(
            user=user,
            expiration=_get_tomorrow(),
            type=UserToken.PASSWORD_RESET,
        )

        link, alternative_link = get_reset_links(token.token)

    context = {
        'participant': participant,
        'unsub_link': get_mailinglist_unsubscribe_url(participant),
        'set_password_link': link,
        'login_link': get_login_page_url(),
        'is_ldap_user': user.is_ldap_account,
    }

    send_template_email(
        [participant.email],
        "UiL OTS: Account aangemaakt",
        'api/mail/existing_leader_new_participant',
        context,
        get_supreme_admin().email
    )


def _add_participant_group(api_user: ApiUser) -> None:
    """
    This function adds a given ApiUser to the Participant group
    :param api_user:
    :return:
    """
    group = ApiGroup.objects.get(name=settings.PARTICIPANT_GROUP)

    api_user.groups.add(group)
    api_user.save()


def _switch_main_email(participant: Participant, new_email: str) -> None:
    """
    This function switches the main email of a participant with one of it's
    secondary emails. The old secondary email object is used to store the
    previous main email.

    :param participant: A participant object
    :param new_email: An email string that corresponds to a secondary email
    :return: Nothing
    """
    # Get the secondary email that now houses the new main email
    secondary_emails = participant.secondaryemail_set.all()
    existing_new_email = next(
        iter([x for x in secondary_emails if x.email == new_email])
    )

    # Set the old main email as this object's email address
    existing_new_email.email = participant.email
    existing_new_email.save()

    # Set the new email (same as the original value of the secondary email
    # above) as the main email
    participant.email = new_email
    participant.save()
