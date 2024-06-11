import tempfile

from experiments.models import Experiment


def test_create_experiment(sb, as_admin, sample_leader):
    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")

    sb.click('a:contains("Create experiment")')
    sb.type('input[name="name"]', "Experiment name")
    sb.type('input[name="duration"]', "10 minutes")
    sb.type('input[name="session_duration"]', "25 minutes")
    sb.type('input[name="recruitment_target"]', "30")

    sb.type('textarea[name="task_description"]', "task description")
    sb.type('textarea[name="additional_instructions"]', "additional instructions")
    sb.type('input[name="responsible_researcher"]', "dr. Lin Guist")

    sb.select_option_by_text('select[name="leaders"]', sample_leader.name)

    # upload an email attachment
    test_file_content = b"this is a test file"
    with tempfile.NamedTemporaryFile() as file:
        file.write(test_file_content)
        file.flush()

        sb.choose_file('input[name="attachments"]', file.name)

        sb.click('button:contains("Next")')
        sb.assert_text_visible("Successfully created")
        sb.click('button:contains("Save")')

        sb.assert_text_visible("Experiment name")

    experiment = Experiment.objects.last()
    assert experiment.name == "Experiment name"

    assert experiment.attachments.count() == 1
    assert experiment.attachments.first().file.read() == test_file_content


def test_edit_experiment_add_attachment(sb, live_server, as_admin, sample_experiment):
    sb.open(live_server.url + f"/experiments/{sample_experiment.pk}/update/")

    # upload an email attachment
    test_file_content = b"this is a test file"
    with tempfile.NamedTemporaryFile() as file:
        file.write(test_file_content)
        file.flush()

        sb.choose_file('input[name="attachments"]', file.name)

        sb.click('button:contains("Save")')

        sb.assert_text_visible("updated")

    assert sample_experiment.attachments.count() == 1
    assert sample_experiment.attachments.first().file.read() == test_file_content
