from django.forms.widgets import Widget


class ParticipantSexWidget(Widget):
    template_name = "widgets/participant_sex_widget.html"

    def value_from_datadict(self, data, files, name):
        value = data.get(name)

        if value == "None":
            return None

        if value == "OTHER":
            value = data.get(name + "_other")

        return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        if context["widget"]["value"] not in ["M", "F"]:
            context["widget"]["other_value"] = context["widget"]["value"]
            context["widget"]["value"] = "OTHER"

        return context
