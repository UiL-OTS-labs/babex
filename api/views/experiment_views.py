from rest_framework import viewsets, permissions, views, mixins as rest_mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.permissions import IsPermittedClient
from api.serializers import ExperimentSerializer
from experiments.models import Experiment
from api.auth.authenticators import JwtAuthentication

from experiments.utils.exclusion import check_participant_eligible


class OpenExperimentsView(rest_mixins.RetrieveModelMixin,  # This default
                          # implementation suits our needs
                          viewsets.GenericViewSet):

    serializer_class = ExperimentSerializer
    permission_classes = (IsPermittedClient,)
    authentication_classes = (JwtAuthentication,)

    def get_queryset(self):
        qs = Experiment.objects.filter(open=True, public=True)

        qs = qs.select_related('leader', 'location')
        qs = qs.prefetch_related('additional_leaders', 'excluded_experiments')

        self.queryset = qs

        return qs

    def list(self, request, *args, **kwargs):
        """Custom implementation of the list call.

        This method differs from the standard viewset list method in that it
        will also filter the experiments if an authenticated user makes the
        call.
        """
        open_experiments = list(self.get_queryset())

        # If the request has been issued on behalf of a participant, filter
        # the open experiments to exclude experiments that participant cannot
        # take part in
        if request.user.is_authenticated and hasattr(request.user,
                                                     'participant'):
            filtered = []
            for experiment in open_experiments:
                if check_participant_eligible(experiment,
                                              request.user.participant):
                    filtered.append(experiment)

            open_experiments = filtered

        serializer = self.serializer_class(open_experiments, many=True)

        return Response(serializer.data)
