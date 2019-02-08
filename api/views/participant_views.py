from rest_framework import views
from rest_framework.response import Response

from api.permissions import IsPermittedClient
from participants.models import Participant


class SubscribeToEmaillistView(views.APIView):
    permission_classes = (IsPermittedClient,)

    def post(self, request):
        post_data = request.POST
        success = False

        email = post_data.get('email')

        qs = Participant.objects.prefetch_related('secondaryemail_set').all()

        filtered = [x for x in qs if x.email == email
                    or email
                    in [y.email for y in x.secondaryemail_set.all()]]

        alreadyKnown = len(filtered) != 0

        if not alreadyKnown:
            participant = Participant()

            participant.email = email
            participant.language = post_data.get('language')
            participant.multilingual = post_data.get('multilingual')
            participant.dyslexic = post_data.get('dyslexic')

            participant.save()
            success = True

        return Response({
            'success': success
        })
