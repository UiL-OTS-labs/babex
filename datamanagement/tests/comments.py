from datetime import datetime, timedelta

from django.test import TestCase
from django.utils.timezone import get_current_timezone

from auditlog.models import LogEntry
from comments.models import Comment
from datamanagement.tests.common import _create_dummy_user, _create_experiment, \
    _create_participant, _create_thresholds
from datamanagement.utils.comments import delete_comments, get_comment_counts


class CommentDMTests(TestCase):
    databases = ['default', 'auditlog']

    def setUp(self) -> None:
        self.thresholds = _create_thresholds()
        self.experiment = _create_experiment()
        self.participant = _create_participant()

        self.comments = []
        for days_offset in range(5, 16):
            comment = Comment()
            comment.participant = self.participant
            comment.experiment = self.experiment
            comment.comment = "Offset used: -{}".format(days_offset)
            comment.system_comment = True
            comment.save()

            # Because comment.datetime has auto_add_now, we have to set the new
            # datetime after save, otherwise it will be ignored
            dt = datetime.now(tz=get_current_timezone()) - \
                               timedelta(days=days_offset)
            # Remove seconds etc, as they are irrelevant and mess with
            # comparisons
            dt = dt.replace(minute=0, second=0, microsecond=0)
            comment.datetime = dt
            comment.save()

            self.comments.append(comment)

    def test_correct_num_comments(self):
        """
        Sanity check for the test itself. Tests if the test DB has the
        same amount of comments as we have stored in the test.
        """
        self.assertEqual(len(self.comments), Comment.objects.count())

    def test_correct_datetimes(self):
        """
        Sanity check for the test itself. Tests if the datetime's of the
        comments are sequential
        """
        last_dt = self.comments[0].datetime

        for comment in self.comments[1:]:
            compensated_dt = last_dt - timedelta(days=1)
            self.assertEqual(compensated_dt, comment.datetime)
            last_dt = comment.datetime

    def test_honors_threshold(self):
        """
        Tests if we get the correct amount of outdated comments
        """
        comment_counts = get_comment_counts()

        self.assertEqual(len(comment_counts), 1)

        # Should have 6 comments that are old. (offset 10-15)
        self.assertEqual(comment_counts[0][1], 6)

    def test_delete_only_old_comments(self):
        """
        Tests if the delete_comments method only deleted comments that are
        deemed too old to keep
        :return:
        """
        delete_comments(self.experiment, _create_dummy_user())

        comment_counts = get_comment_counts()

        # We should have 0 experiments with outdated comments
        self.assertEqual(len(comment_counts), 0)

        # Should have 5 comments left that should've been untouched
        num_comments_left = Comment.objects.count()
        self.assertEqual(num_comments_left, 5)

        # Check if the auditlog logged anything
        self.assertEqual(LogEntry.objects.count(), 1)

