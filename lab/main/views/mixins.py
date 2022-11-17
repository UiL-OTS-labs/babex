from django.contrib import messages


class RedirectSuccessMessageMixin:
    success_message = ''

    def get(self, *args, **kwargs):
        response = super(RedirectSuccessMessageMixin, self).get(*args, **kwargs)

        messages.success(self.request, self.success_message)

        return response

    def get_success_message(self):
        return self.success_message
