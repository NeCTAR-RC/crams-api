from json import loads as json_loads

from rest_framework.exceptions import ParseError

from crams.DBConstants import FUNDING_BODY_NECTAR, FUNDING_BODY_VICNODE
from crams.lang_utils import reverse_dict
from crams.settings import NECTAR_APPROVER_ROLE, VICNODE_APPROVER_ROLE


# Funding Body Role Map
ROLE_FB_MAP = {
    NECTAR_APPROVER_ROLE: FUNDING_BODY_NECTAR,
    VICNODE_APPROVER_ROLE: FUNDING_BODY_VICNODE
}
FB_ROLE_MAP_REVERSE = reverse_dict(ROLE_FB_MAP)


def get_authorised_funding_bodies(user):
    """

    :param user:
    :return:
    """

    if not hasattr(user, 'auth_token'):
        raise ParseError('Current user has no token, hence roles not set')

    json_roles = user.auth_token.cramstoken.ks_roles
    if json_roles:
        roles = set(json_loads(json_roles))
        return [ROLE_FB_MAP.get(r) for r in roles]

    return []
