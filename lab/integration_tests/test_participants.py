def test_participant_add_comment(sb, live_server, as_leader, sample_experiment, sample_participant):
    sample_experiment.leaders.add(as_leader)
    sb.open(live_server.url + "/participants")
    sb.click(f"a:contains('{sample_participant.name}')")
    sb.click("a:contains('new comment')")
    sb.click("textarea")
    sb.type("textarea", "hello this is a comment")
    sb.click("button:contains(Send)")

    sb.assert_text_not_visible("button:contains(Send)")
    sb.assert_text_visible("hello this is a comment")
    sb.assert_text(as_leader.name, "#participant-comments")