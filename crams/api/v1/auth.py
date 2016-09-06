# coding=utf-8
"""
 auth.py
"""
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.authtoken import views
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view

from crams import settings
from crams.models import CramsToken, UserEvents
from crams.account.models import User


# noinspection PyUnusedLocal
@api_view(['GET', ])
def set_tokens(request):
    """
        set tokens
    :param request:
    :return:
    """
    for user in User.objects.all():
        Token.objects.get_or_create(user=user)

    return Response('Tokens Done')


@api_view(['GET', ])
def redirect_to_rc_shib(request):
    """
    redirect to rc shib
    :param request:
    :return:
    """
    try:
        auth_path = request.build_absolute_uri('/nectar_token_auth')
        ret_path = settings.CRAMS_RC_SHIB_URL_PART + auth_path

        try:
            ks_login_url = request.query_params.get('ks_login_url', None)
            # Temp Fix, until we figure out why #/ks_login is not returned
            ks_login_url = ks_login_url + settings.CLIENT_KS_LOGIN_PATH
        except Exception:
            ks_login_url = request.META.get('HTTP_REFERER') + \
                           settings.CLIENT_KS_LOGIN_PATH

        response = HttpResponseRedirect(ret_path)
        response.set_cookie(settings.CRAMS_CLIENT_COOKIE_KEY, ks_login_url)
        response.set_cookie('redirect', ret_path)
        response.set_cookie('authpath', auth_path)
        return response
    except Exception as e:
        return HttpResponse(str(e))


class CramsLoginAuthToken(views.ObtainAuthToken):
    """
    Class CramsLoginAuthToken
    """

    def post(self, request):
        """
        post method
        :param request:
        :return:
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            msg = 'User logged in with valid User/Password'
            UserEvents.objects.create(
                created_by=user,
                event_message=msg
            )

            crams_token, created = CramsToken.objects.get_or_create(user=user)
            response = Response({'token': crams_token.key})
            response['token'] = crams_token.key
            response['roles'] = crams_token.ks_roles
            return response

        return Response('Login fail')


obtain_auth_token = CramsLoginAuthToken.as_view()
