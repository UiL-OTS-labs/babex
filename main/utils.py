from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
from django.conf import settings
from django.template.loader import render_to_string
from typing import Tuple, List


def send_template_email(recipient_list: list, subject: str, template: str,
                        template_context: dict, from_email: str = None) -> None:
    """
    Light wrapper for Django's send_mail function. The main addition: this
    function handles the template rendering for you. Just specify the template
    name (without extensions).

    Note: both a HTML and a plain text version of the template should exist!

    For example:
    app/test.html
    app/test.txt

    Function call: send_template_email(template='app/test', *args, **kwargs)

    :param recipient_list: A list of recipients
    :param subject: Email subject
    :param template: Template name, without extension
    :param template_context: Any context variables for the templates
    :param from_email: FROM header. If absent, settings.FROM_EMAIL will be used
    """
    plain_body = render_to_string('{}.txt'.format(template), template_context)
    html_body = render_to_string('{}.html'.format(template), template_context)

    from_email = from_email or settings.FROM_EMAIL

    send_mail(
        subject,
        plain_body,
        from_email,
        recipient_list,
        html_message=html_body
    )


def send_personalised_mass_mail(datatuple: Tuple[str, dict, List[str]],
                                template: str,
                                template_context: dict,
                                from_email: str = None) -> None:
    """
    Given a datatuple of (subject, personal_context, recipient_list),
    send each message to each recipient list.

    personal_context and template_context will be merged together to create
    a personalised email.

    :param datatuple: A tuple of tuples: (subject, personal_context, recipient_list)
    :param template: Template name, without extension
    :param template_context: Any context variables for the templates
    :param from_email: FROM header. If absent, settings.FROM_EMAIL will be used
    """
    messages = []
    from_email = from_email or settings.FROM_EMAIL
    connection = get_connection()

    for subject, personal_context, recipient_list in datatuple:
        context = personal_context.copy()
        context.update(template_context)

        plain_body = render_to_string('{}.txt'.format(template),
                                      context)
        html_body = render_to_string('{}.html'.format(template),
                                     context)

        message = EmailMultiAlternatives(subject, plain_body, from_email,
                                         recipient_list, connection=connection)

        message.attach_alternative(html_body, 'text/html')

        messages.append(message)

    connection.send_messages(messages)
