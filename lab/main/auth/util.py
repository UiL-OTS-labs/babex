from braces.views import UserPassesTestMixin
from rest_framework.permissions import IsAuthenticated


class ExperimentLeaderMixin(UserPassesTestMixin):
    """checks that the current user is a leader of the relevant experiment a view.
    Assumes the existence of a self.experiment property on the view.
    Suitable for use with regular Django class-based views.

    Note that this is different than RandomLeaderMixin.
    """

    def test_leader(self, user):
        # used by child views for finer grained control over leader access
        return True

    def test_func(self, user):
        return user.is_staff or self.experiment in user.experiments.all()


class RandomLeaderMixin(UserPassesTestMixin):
    """checks that the current user is a leader of ANY currently active experiment.
    Assumes the existence of a self.experiment property on the view.
    Suitable for use with regular Django class-based views"""

    def test_leader(self, user):
        # used by child view for finer grained control over leader access
        return True

    def test_func(self, user):
        # staff = lab managers, can access any experiment
        return (user.is_leader() or user.is_staff) and self.test_leader(user)


class IsExperimentLeader(IsAuthenticated):
    """checks that the current user is a leader of the relevant experiment a view.
    Assumes the existence of a self.experiment property on the view.
    Suitable for use with DRF class-based views"""

    pass


class IsRandomLeader(IsAuthenticated):
    """checks that the current user is a leader of the relevant experiment a view.
    Assumes the existence of a self.experiment property on the view.
    Suitable for use with DRF class-based views"""

    def has_permission(self, request, view):
        # staff = lab managers, can access any experiment
        return super().has_permission(request, view) and (self.request.user.is_staff or self.request.user.is_leader())
