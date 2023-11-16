def test_create_experiment(sb, as_admin, sample_leader):
    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")

    sb.click('a:contains("Create experiment")')
    sb.type('input[name="name"]', "Experiment name")
    sb.type('input[name="duration"]', "10 minutes")
    sb.type('input[name="compensation"]', "15 eu")
    sb.type('input[name="recruitment_target"]', "30")

    sb.type('textarea[name="task_description"]', "task description")
    sb.type('textarea[name="additional_instructions"]', "additional instructions")

    sb.select_option_by_text('select[name="leaders"]', sample_leader.username)

    sb.click('button:contains("Next")')
    sb.assert_text_visible("Successfully created")
    sb.click('button:contains("Save")')
    sb.assert_text_visible("Experiment name")
