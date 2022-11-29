from django.core.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework import mixins as rest_mixins, views, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.auth.authenticators import JwtAuthentication
from api.permissions import IsLeader, IsPermittedClient
from api.serializers import ExperimentSerializer
from api.serializers.experiment_serializers import LeaderExperimentSerializer
from api.utils import register_participant
from auditlog.enums import Event, UserType
import auditlog.utils.log as auditlog
from experiments.models import Appointment, Experiment
from experiments.utils import delete_timeslot, unsubscribe_participant
from experiments.utils.exclusion import check_participant_eligible
from experiments.utils.remind_participant import remind_participant
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
            if not experiment.has_free_places():
                continue

            if filter_personally and not check_participant_eligible(
                    experiment,
                    request.user.participant):
                continue

            filtered.append(experiment)

        serializer = self.serializer_class(filtered, many=True)

        return Response(serializer.data)


class LeaderExperimentsView(viewsets.GenericViewSet):
    serializer_class = LeaderExperimentSerializer
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

        qs = qs.distinct()

        self.queryset = qs

        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        message = "Leader accessed '{}' data (pk: {}), which includes " \
                  "participant data.".format(
            instance.name,
            instance.pk,
        )

        event = Event.VIEW_SENSITIVE_DATA
        if 'download' in self.request.query_params:
            event = Event.DOWNLOAD_DATA

        auditlog.log(
            event,
            message,
            self.request.user,
            UserType.LEADER,
        )

        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        message = "Leader accessed overview data, which includes " \
                  "participant data in the payload. However, this should not " \
                  "be visible to leader."

        event = Event.VIEW_DATA
        if 'download' in self.request.query_params:
            event = Event.DOWNLOAD_DATA

        auditlog.log(
            event,
            message,
            self.request.user,
            UserType.LEADER,
            {
                'pk_list': [x.pk for x in queryset]
            }
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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


class RemindParticipantsView(views.APIView):
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

        pks = request.data.getlist('appointments')

        try:
            for pk in pks:
                appointment = Appointment.objects.get(pk=pk)
                remind_participant(appointment)
        except Exception as e:  # NoQA
            pass

        return Response(True)


class AddTimeSlotView(views.APIView):
    permission_classes = (IsPermittedClient, IsAuthenticated, IsLeader)
    authentication_classes = (JwtAuthentication,)

    def post(self, request, experiment):
        data = request.data
        success = False

        leader = request.user.leader

        experiment_object = Experiment.objects.get(pk=experiment)

        if not leader == experiment_object.leader and leader not in \
                experiment_object.additional_leaders.all():
            raise PermissionDenied

        try:
            add_timeslot(
                experiment_object,
                data['datetime'],
                data['max_places'],
            )
        except:
            pass
        else:
            success = True

        return Response({
            'success': success
        })


class DeleteTimeSlots(views.APIView):
    permission_classes = (IsPermittedClient, IsAuthenticated, IsLeader)
    authentication_classes = (JwtAuthentication, )

    def post(self, request, experiment):
        data = request.data
        success = False

        leader = request.user.leader

        experiment_object = Experiment.objects.get(pk=experiment)

        if not leader == experiment_object.leader and leader not in \
                experiment_object.additional_leaders.all():
            raise PermissionDenied

        try:
            for item in data.get('to_delete'):
                timeslot, n = item.split('_')
                timeslot, n = int(timeslot), int(n)

                delete_timeslot(experiment_object,
                                timeslot,
                                n,
                                request.user)
        except:
            pass
        else:
            success = True

        return Response({
            'success': success
        })


class DeleteAppointment(views.APIView):
    permission_classes = (IsPermittedClient, IsAuthenticated, IsLeader)
    authentication_classes = (JwtAuthentication, )

    def post(self, request, experiment):
        data = request.data
        success = False

        leader = request.user.leader

        experiment_object = Experiment.objects.get(pk=experiment)

        if not leader == experiment_object.leader and leader not in \
                experiment_object.additional_leaders.all():
            raise PermissionDenied

        try:
            # NOTE: this function also logs the action into the auditlog
            # (This deviates from the usual way, in which it's done by the view)
            unsubscribe_participant(
                data.get('to_delete'),
                deleting_user=request.user
            )
        except:
            pass
        else:
            success = True

        return Response({
            'success': success
        })


class RegisterView(views.APIView):
    permission_classes = (IsPermittedClient,)
    authentication_classes = (JwtAuthentication,)

    def post(self, request, experiment):
        data = request.data
        experiment = Experiment.objects.get(pk=experiment)

        # If full == False, we're dealing with a logged in user and we should
        # retrieve the email from the account (as it's not provided by the
        # client app)
        if 'full' in data and not data['full']:
            data['email'] = request.user.participant.email

        success, recoverable, messages = register_participant(data, experiment)

        return Response({
            'success':     success,
            'recoverable': recoverable,
            'messages':    messages
        })
