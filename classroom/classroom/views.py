from rest_framework import generics, mixins, status
from rest_framework.response import Response

from classroom.models import Schedule, Classroom
from classroom.serializers import ScheduleSerializer, ClassroomWithoutScheduleSerializer


# Create your views here.
class ClassroomListView(generics.GenericAPIView,
                        mixins.ListModelMixin):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomWithoutScheduleSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('faculty_id'):
            return Response({
                'status': '400',
                'message': 'A student_id is needed to filter the TuitionFees',
            }, status=status.HTTP_400_BAD_REQUEST)
        #TODO filter by date to check if classroom is available then

        return self.list(request, *args, **kwargs)


class ClassroomUpdateView(generics.GenericAPIView,
                          mixins.UpdateModelMixin):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomWithoutScheduleSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ScheduleCreateView(generics.GenericAPIView,
                         mixins.CreateModelMixin):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def post(self, request, *args, **kwargs):
        # TODO check if dates are available
        return self.create(request, *args, **kwargs)
