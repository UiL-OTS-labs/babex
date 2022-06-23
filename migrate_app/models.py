from django.db import models


class Admin(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'admin'


class CiSessions(models.Model):
    session_id = models.CharField(primary_key=True, max_length=40)
    ip_address = models.CharField(max_length=16)
    user_agent = models.CharField(max_length=50)
    last_activity = models.PositiveIntegerField()
    user_data = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ci_sessions'


class Comments(models.Model):
    participant_id = models.IntegerField()
    leader_id = models.IntegerField()
    experiment_id = models.IntegerField()
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'comments'


class Criteria(models.Model):
    name_form = models.CharField(max_length=255)
    name_natural = models.CharField(max_length=255)
    values = models.CharField(max_length=255)
    value_correct = models.CharField(max_length=255)
    message_failed = models.TextField()

    class Meta:
        managed = False
        db_table = 'criteria'


class EmailTokens(models.Model):
    participants_id = models.IntegerField()
    experiment_id = models.IntegerField()
    token = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'email_tokens'


class Experiments(models.Model):
    name = models.CharField(max_length=255)
    duration = models.CharField(max_length=100)
    compensation = models.CharField(max_length=50)
    task_description = models.TextField()
    additional_instructions = models.TextField()
    location = models.TextField()
    places = models.IntegerField()
    open = models.IntegerField()
    visible = models.IntegerField()
    other_leaders = models.TextField()

    class Meta:
        managed = False
        db_table = 'experiments'


class ExperimentsCriteria(models.Model):
    experiment_id = models.IntegerField()
    criteria_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'experiments_criteria'
        unique_together = (('experiment_id', 'criteria_id'),)


class ExperimentsDefaultCriteria(models.Model):
    experiment_id = models.IntegerField(primary_key=True)
    type_age = models.CharField(max_length=30)
    age = models.CharField(max_length=255)
    language = models.CharField(max_length=100)
    multiple_lang = models.CharField(max_length=50)
    dyslectic = models.CharField(max_length=30)
    handedness = models.CharField(max_length=30)
    sex = models.CharField(max_length=50)
    social_role = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'experiments_default_criteria'


class ExperimentsExcluded(models.Model):
    experiment_id = models.IntegerField()
    experiment_ex_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'experiments_excluded'
        unique_together = (('experiment_id', 'experiment_ex_id'),)


class ExperimentsLeaders(models.Model):
    experiment_id = models.IntegerField()
    leader_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'experiments_leaders'
        unique_together = (('experiment_id', 'leader_id'),)


class ExperimentsTimeslots(models.Model):
    experiment_id = models.IntegerField()
    timeslot_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'experiments_timeslots'
        unique_together = (('experiment_id', 'timeslot_id'),)


class Leaders(models.Model):
    name = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=45)
    language = models.CharField(max_length=100)
    photo = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leaders'


class Participants(models.Model):
    email = models.CharField(unique=True, max_length=100)
    email_secondary = models.TextField()
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=100)
    dyslectic = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    multiple_lang = models.CharField(max_length=10)
    phonenumber = models.CharField(max_length=20)
    handedness = models.CharField(max_length=10)
    sex = models.CharField(max_length=10)
    social_role = models.CharField(max_length=255)
    email_subscription = models.CharField(max_length=10)
    capable = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'participants'


class ParticipantsCriteriaValue(models.Model):
    participant_id = models.IntegerField()
    criteria_id = models.IntegerField()
    value = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'participants_criteria_value'


class ParticipantsTimeslots(models.Model):
    participant_id = models.IntegerField()
    timeslot_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'participants_timeslots'
        unique_together = (('participant_id', 'timeslot_id'),)


class Timeslots(models.Model):
    tdate = models.DateField()
    ttime = models.TimeField()
    place = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'timeslots'
