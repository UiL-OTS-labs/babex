from django.core.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework import mixins as rest_mixins, views, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.auth.authenticators import JwtAuthentication
from api.permissions import IsLeader, IsPermittedClient
from api.serializers import ExperimentSerializer
from api.utils import register_participant
from experiments.models import Experiment
from experiments.utils.exclusion import check_participant_eligible
from experiments.utils.timeslot_create import add_timeslot


class ExperimentsView(rest_mixins.RetrieveModelMixin,  # This default
                      # implementation suits our needs
                      viewsets.GenericViewSet):
    serializer_class = ExperimentSerializer
    permission_classes = (IsPermittedClient,)
    authentication_classes = (JwtAuthentication,)

    def get_queryset(self):
        qs = Experiment.objects.all()

        qs = qs.select_related('leader', 'location')
        qs = qs.prefetch_related(
            'additional_leaders',
            'excluded_experiments',
        )

        self.queryset = qs

        return qs

    def list(self, request, *args, **kwargs):
        """Custom implementation of the list call.

        This method differs from the standard viewset list method in that it
        will also filter the experiments if an authenticated user makes the
        call.

        It also uses a more limited QuerySet, as it filters out closed and
        non-public experiments.
        """
        qs = self.get_queryset().filter(
            public=True,
            open=True,
        )
        open_experiments = list(qs)

        # If the request has been issued on behalf of a participant, filter
        # the open experiments to exclude experiments that participant cannot
        # take part in
        filter_personally = request.user.is_authenticated and hasattr(
            request.user, 'participant'
        )

        filtered = []
        for experiment in open_experiments:
            if not experiment.has_free_timeslots():
                continue

            if filter_personally and not check_participant_eligible(
                    experiment,
                    request.user.participant):
                continue

            filtered.append(experiment)

        serializer = self.serializer_class(filtered, many=True)

        return Response(serializer.data)


class LeaderExperimentsView(rest_mixins.RetrieveModelMixin,
                            rest_mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    serializer_class = ExperimentSerializer
    permission_classes = (IsPermittedClient, IsAuthenticated)
    authentication_classes = (JwtAuthentication,)

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, 'leader'):
            raise PermissionDenied

        leader = user.leader

        qs = Experiment.objects.filter(Q(leader=leader) | Q(
            additional_leaders=leader))

        qs = qs.select_related('leader', 'location')
        qs = qs.prefetch_related('additional_leaders', 'excluded_experiments')

        self.queryset = qs

        return qs


class SwitchExperimentOpenView(views.APIView):
    permission_classes = (IsPermittedClient, IsAuthenticated, IsLeader)
    authentication_classes = (JwtAuthentication,)

    def post(self, request, experiment):
        if not hasattr(request.user, 'leader'):
            raise PermissionDenied

        leader = request.user.leader

        experiment_object = Experiment.objects.get(pk=experiment)

        if not leader == experiment_object.leader and leader not in \
                experiment_object.additional_leaders.all():
            raise PermissionDenied

        experiment_object.open = not experiment_object.open
        experiment_object.save()

        return Response({
            'success': True,
            'open':    experiment_object.open
        })


class RegisterView(views.APIView):
    permission_classes = (IsPermittedClient,)
    authentication_classes = (JwtAuthentication,)

    def post(self, request, experiment):
        data = request.data
        experiment = Experiment.objects.get(pk=experiment)

        success, recoverable, messages = register_participant(data, experiment)

        return Response({
            'success':     success,
            'recoverable': recoverable,
            'messages':    messages
        })
