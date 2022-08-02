from django.conf import settings


class DatabaseRouter:
    """
    This DB router will route all DB stuff for the auditlog app into a
    separate database. It does check if the auditlog db is defined. If it's
    not, the default DB will be used.

    Note, when any of these methods return 'None', it means that this router
    does won't decide the action. The routing will then be handled by the
    next defined router. (If none are explicitly specified, it will be
    Django's default router, which will route everything to the 'default'
    database)
    """

    AUDITLOG_DB = 'auditlog'
    AUDITLOG_APP = 'auditlog'

    def __init__(self):
        self.audit_db_present = self.AUDITLOG_DB in settings.DATABASES

    def db_for_read(self, model, **hints):

        # If we don't have a separate DB defined, return that we don't care
        if not self.audit_db_present:
            return None

        # If this is a model from the AUDITLOG_APP, return the AUDITLOG_DB name
        if model._meta.app_label == self.AUDITLOG_APP:
            return self.AUDITLOG_DB

        # Otherwise, let Django's router handle it
        return None

    def db_for_write(self, model, **hints):

        # If we don't have a separate DB defined, return that we don't care
        if not self.audit_db_present:
            return None

        # If this is a model from the AUDITLOG_APP, return the AUDITLOG_DB name
        if model._meta.app_label == self.AUDITLOG_APP:
            return self.AUDITLOG_DB

        # Otherwise, let Django's router handle it
        return None

    def allow_relation(self, obj1, obj2, **hints):

        # If we don't have a separate DB defined, return that we don't care
        if not self.audit_db_present:
            return None

        # If both models are in the AUDITLOG_APP, we allow a relation between
        # them
        if obj1._meta.app_label == self.AUDITLOG_APP and \
                obj2._meta.app_label == self.AUDITLOG_APP:
            return True
        # If none of the models are in the AUDITLOG_APP, let Django figure
        # out a database
        elif self.AUDITLOG_APP not in [obj1._meta.app_label,
                                       obj2._meta.app_label]:
            return None

        # If one of two are in AUDITLOG_APP, block relations
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        # If we don't have a separate DB defined, return that we don't care
        if not self.audit_db_present:
            return None

        # If the model belongs to AUDITLOG_APP, only allow migrations on the
        # AUDITLOG_DB
        if app_label == self.AUDITLOG_APP:
            return db == self.AUDITLOG_DB
        # Do not migrate non-AUDITLOG_APP models on the AUDITLOG_DB
        elif db == self.AUDITLOG_DB:
            return False

        # In any other case, let Django's router handle it
        return None
