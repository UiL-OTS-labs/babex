# NOTE: do not import anything here, it breaks the fragile import chain
# (To be more precise, auditlog.models imports  auditlog.utils.get_choices,
# but auditlog.utils.log imports auditlog.models. This is fine, until this file
# contains imports from the util modules.)
