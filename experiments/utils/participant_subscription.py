from main.utils import get_supreme_admin, send_template_email


def unsubscribe_participant(time_slot, appointment_pk: int,
                            sent_email: bool = True) -> None:

    appointment = time_slot.appointments.get(pk=appointment_pk)

    # Always delete first, the data in it will still be available for the
    # next bit
    appointment.delete()

    if sent_email:
        admin = get_supreme_admin()
        experiment = time_slot.experiment

        subject = 'UiL OTS uitschrijven experiment: {}'.format(experiment.name)
        context = {
            'participant': appointment.participant,
            'time_slot': time_slot,
            'experiment': experiment,
            'admin': admin.get_full_name(),
            'admin_email': admin.email,
            'other_time_link': '',
            'home_link': '',  # TODO: make these links
        }

        send_template_email(
            [appointment.participant.email],
            subject,
            'timeslots/mail/unsubscribed',
            context,
            admin.email
        )



