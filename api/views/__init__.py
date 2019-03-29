from .account_views import ChangePasswordView, ForgotPasswordView, \
    ResetPasswordView, ValidateTokenView
from .admin_views import AdminView
from .comment_views import AddCommentView
from .experiment_views import AddTimeSlotView, DeleteTimeSlots, ExperimentsView, \
    LeaderExperimentsView, RegisterView, SwitchExperimentOpenView
from .leader_views import ChangeLeaderView, LeaderView
from .participant_views import AppointmentsView, GetAppointmentTokenView, \
    GetRequiredFields, SubscribeToEmaillistView
