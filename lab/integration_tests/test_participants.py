from playwright.sync_api import expect


def test_participant_add_comment(page, live_server, as_leader, sample_experiment, sample_participant):
    sample_experiment.leaders.add(as_leader)
    page.goto(live_server.url + "/participants")
    page.locator("a").get_by_text(sample_participant.name).click()
    page.locator("a").get_by_text("new comment").click()
    page.fill("textarea", "hello this is a comment")
    page.get_by_role("button", name="Send").click()

    expect(page.get_by_role("button", name="Send")).not_to_be_visible()
    expect(page.get_by_text("hello this is a comment")).to_be_visible()
    expect(page.locator("#participant-comments")).to_contain_text(as_leader.name)
