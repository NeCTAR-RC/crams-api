from rest_framework import viewsets, decorators
from rest_framework.views import Response

from crams.models import ProjectIDSystem, ProjectID
from crams.permissions import IsCramsAuthenticated


class ExistsViewset(viewsets.ViewSet):
    serializer_class = None
    permission_classes = [IsCramsAuthenticated]
    queryset = ProjectID.objects.none()

    @decorators.list_route(
        url_path='project_id/(?P<system_pk>\d+)/(?P<project_id>\S+)')
    def projectid_exists_for_system(self, request, system_pk, project_id):
        ret_dict = {
            'exists': False,
            'message': None
        }
        try:
            system = ProjectIDSystem.objects.get(pk=system_pk)
            if project_id is not None:
                project_id = project_id.lower()
                qs = ProjectID.objects.filter(
                    system=system, identifier__iexact=project_id)
                ret_dict['exists'] = qs.exists()
        except ProjectIDSystem.DoesNotExist:
            ret_dict['message'] = \
                'System DB id {}: does not exists'.format(system_pk)

        return Response(ret_dict)
