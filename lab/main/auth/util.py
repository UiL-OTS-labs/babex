from braces.views import StaffuserRequiredMixin, UserPassesTestMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated


class LabManagerMixin(StaffuserRequiredMixin):
    raise_exception = True


class LabSupportMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self, user):
        return user.is_authenticated and (user.is_support or user.is_staff)


class ExperimentLeaderMixin(UserPassesTestMixin):
    """Checks that the current user is a leader of the relevant experiment.
    Assumes the existence of a self.experiment property on the view.
    Suitable for use with regular Django class-based views.

    Note that this is different than RandomLeaderMixin.
    """

    raise_exception = True

    def test_leader(self, user):
        # used by child views for finer grained control over leader access
        return True

    def test_func(self, user):
        if not user.is_authenticated:
            return False
        # staff = lab managers, can access any experiment
        return user.is_staff or self.experiment in user.experiments.all()


class RandomLeaderMixin(UserPassesTestMixin):
    """Checks that the current user is a leader of ANY currently active experiment.
    Assumes the existence of a self.experiment property on the view.
    Suitable for use with regular Django class-based views"""

    raise_exception = True

    def test_leader(self, user):
        # used by child view for finer grained control over leader access
        return True

    def test_func(self, user):
        if not user.is_authenticated:
            return False
        # staff = lab managers, can access any experiment
        return (user.is_leader or user.is_staff) and self.test_leader(user)


class IsLabManager(IsAdminUser):
    pass


class IsExperimentLeader(IsAuthenticated):
    """Checks that the current user is a leader of the relevant experiment.
    Assumes the existence of a self.experiment property on the view.
    Suitable for use with DRF class-based views"""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            request.user.is_staff or view.experiment in request.user.experiments.all()
        )


class IsRandomLeader(IsAuthenticated):
    """checks that the current user is a leader of ANY currently active experiment.
    Assumes the existence of a self.experiment property on the view.
    Suitable for use with DRF class-based views"""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and (request.user.is_staff or request.user.is_leader)
