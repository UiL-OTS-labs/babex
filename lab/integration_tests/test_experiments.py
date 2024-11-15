import tempfile

from playwright.sync_api import expect

from experiments.models import Experiment


def test_create_experiment(page, as_admin, sample_leader, sample_location):
    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()

    page.get_by_role("link", name="Create experiment").click()
    page.get_by_role("textbox", name="Name").fill("Experiment name")
    page.get_by_role("spinbutton", name="Task duration").fill("10")
    page.get_by_role("spinbutton", name="Session duration").fill("25")
    page.get_by_role("spinbutton", name="Recruitment target").fill("30")

    page.locator('select[name="location"]').select_option(sample_location.name)
    page.get_by_role("textbox", name="Task description").fill("task description")
    page.get_by_role("textbox", name="Responsible researcher").fill("dr. Lin Guist")

    page.locator('select[name="leaders"]').select_option(sample_leader.name)

    # upload an email attachment
    test_file_content = b"this is a test file"
    with tempfile.NamedTemporaryFile() as file:
        file.write(test_file_content)
        file.flush()

        page.on("filechooser", lambda file_chooser: file_chooser.set_files(file.name))
        page.click('input[name="attachments"]')

        page.get_by_role("button", name="Next").click()
        expect(page.get_by_text("Successfully created")).to_be_visible()
        page.get_by_role("button", name="Save").click()

        expect(page.get_by_text("Experiment name")).to_be_visible()

    experiment = Experiment.objects.last()
    assert experiment.name == "Experiment name"

    assert experiment.attachments.count() == 1
    assert experiment.attachments.first().file.read() == test_file_content


def test_edit_experiment_add_attachment(page, live_server, as_admin, sample_experiment):
    page.goto(live_server.url + f"/experiments/{sample_experiment.pk}/update/")

    # upload an email attachment
    test_file_content = b"this is a test file"
    with tempfile.NamedTemporaryFile() as file:
        file.write(test_file_content)
        file.flush()

        page.on("filechooser", lambda file_chooser: file_chooser.set_files(file.name))
        page.click('input[name="attachments"]')

        page.get_by_role("button", name="Save").click()

        expect(page.get_by_text("updated")).to_be_visible()

    assert sample_experiment.attachments.count() == 1
    assert sample_experiment.attachments.first().file.read() == test_file_content
