from rest_framework import views
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.auth.authenticators import JwtAuthentication
from api.permissions import IsPermittedClient, IsLeader
from api.utils import add_comment
from experiments.models import Experiment
from participants.models import Participant


class AddCommentView(views.APIView):
    permission_classes = (IsPermittedClient, IsAuthenticated, IsLeader)
    authentication_classes = (JwtAuthentication,)

    def post(self, request):
        data = request.data
        success = False

        leader = request.user.leader

        experiment = Experiment.objects.get(
            pk=data.get('experiment')
        )

        if not leader == experiment.leader and leader not in \
                experiment.additional_leaders.all():
            raise PermissionDenied

        try:
            participant = Participant.objects.get(pk=data.get('participant'))

            add_comment(
                experiment,
                participant,
                leader,
                data.get('comment')
            )

            success = True
        except:
            pass

        return Response({
            'success': success
        })