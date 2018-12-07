from main.utils import send_template_email, get_supreme_admin


def unsubscribe_participant(time_slot, participant_pk: int,
                            sent_email: bool = True) -> None:

    participant = time_slot.participants.get(pk=participant_pk)

    time_slot.participants.remove(participant)
    time_slot.save()

    if sent_email:
        admin = get_supreme_admin()
        experiment = time_slot.experiment

        subject = 'UiL OTS uitschrijven experiment: {}'.format(experiment.name)
        context = {
            'participant': participant,
            'time_slot': time_slot,
            'experiment': experiment,
            'admin': admin.get_full_name(),
            'admin_email': admin.email,
            'other_time_link': '',
            'home_link': '',  # TODO: make these links
        }

        send_template_email(
            [participant.email],
            subject,
            'timeslots/mail/unsubscribed',
            context,
            admin.email
        )


