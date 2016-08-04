from json import loads as json_loads

from rest_framework.exceptions import ParseError

from crams.DBConstants import FUNDING_BODY_NECTAR, FUNDING_BODY_VICNODE
from crams.lang_utils import reverse_dict, strip_lower
from crams.settings import NECTAR_APPROVER_ROLE, VICNODE_APPROVER_ROLE
from crams.settings import CRAMS_PROVISIONER_ROLE
from crams.models import CramsToken
from json import dumps as json_dumps


# Funding Body Role Map
ROLE_FB_MAP = {
    strip_lower(NECTAR_APPROVER_ROLE): FUNDING_BODY_NECTAR,
    strip_lower(VICNODE_APPROVER_ROLE): FUNDING_BODY_VICNODE
}
FB_ROLE_MAP_REVERSE = reverse_dict(ROLE_FB_MAP)


def get_configurable_roles():
    configurable_roles = list(ROLE_FB_MAP.keys())
    configurable_roles.append(strip_lower(CRAMS_PROVISIONER_ROLE))
    return configurable_roles


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


def setup_case_insensitive_roles(user, user_roles_list):
    crams_token, created = CramsToken.objects.get_or_create(user=user)
    user_roles_icase = [strip_lower(role) for role in user_roles_list]
    crams_token.ks_roles = json_dumps(user_roles_icase)
    crams_token.save()
    return crams_token
