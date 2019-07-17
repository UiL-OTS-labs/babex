from .account_views import ChangePasswordView, CreateParticipantAccountView, \
    ForgotPasswordView, ResetPasswordView, ValidateTokenView
from .admin_views import AdminView
from .comment_views import AddCommentView
from .experiment_views import AddTimeSlotView, DeleteTimeSlots, ExperimentsView, \
    LeaderExperimentsView, RegisterView, SwitchExperimentOpenView
from .leader_views import LeaderView
from .participant_views import AppointmentsView, GetAppointmentTokenView, \
    GetRequiredFields, SubscribeToEmaillistView
