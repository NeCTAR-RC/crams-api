# coding=utf-8
"""
    DB Constants
"""

JSON_APPROVER_STR = 'approver'

# SystemIds
SYSTEM_NECTAR_UUID = 'NeCTAR_UUID'
SYSTEM_NECTAR = 'NeCTAR'

# funding Body
FUNDING_BODY_NECTAR = 'NeCTAR'
FUNDING_BODY_VICNODE = 'VicNode'

# Contact Role
APPLICANT = 'Applicant'

# Request Status Codes
REQUEST_STATUS_NEW = 'N'
REQUEST_STATUS_SUBMITTED = 'E'
REQUEST_STATUS_UPDATE_OR_EXTEND = 'X'
REQUEST_STATUS_APPROVED = 'A'
REQUEST_STATUS_DECLINED = 'R'
REQUEST_STATUS_PROVISIONED = 'P'
REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED = 'J'
REQUEST_STATUS_LEGACY_SUB = 'L'
REQUEST_STATUS_LEGACY_APPROVED = 'M'
REQUEST_STATUS_LEGACY_DECLINED = 'O'

LEGACY_STATES = [REQUEST_STATUS_LEGACY_DECLINED,
                 REQUEST_STATUS_LEGACY_APPROVED, REQUEST_STATUS_LEGACY_SUB]
NON_ADMIN_STATES = [REQUEST_STATUS_NEW, REQUEST_STATUS_SUBMITTED,
                    REQUEST_STATUS_UPDATE_OR_EXTEND, REQUEST_STATUS_LEGACY_SUB]
APPROVAL_STATES = [REQUEST_STATUS_APPROVED, REQUEST_STATUS_LEGACY_APPROVED]
NEW_REQUEST_STATUS = [REQUEST_STATUS_NEW, REQUEST_STATUS_SUBMITTED]
DECLINED_STATES = [
    REQUEST_STATUS_DECLINED,
    REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED,
    REQUEST_STATUS_LEGACY_DECLINED]
ADMIN_STATES = APPROVAL_STATES + DECLINED_STATES + [REQUEST_STATUS_PROVISIONED]