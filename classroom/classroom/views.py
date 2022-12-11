from rest_framework import generics, mixins, status
from rest_framework.response import Response

from classroom.models import Schedule, Classroom
from classroom.serializers import ScheduleSerializer, ClassroomWithoutScheduleSerializer, \
    ClassroomWithScheduleSerializer


# Create your views here.
class ClassroomListView(generics.GenericAPIView,
                        mixins.ListModelMixin):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomWithoutScheduleSerializer
    filterset_fields = {
        'faculty_id': ['exact'],
        'schedules__start': ['gte'],
        'schedules__end': ['lte']
    }

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('faculty_id', None):
            return Response({
                'status': '400',
                'message': 'A faculty_id is needed to filter the Classrooms',
            }, status=status.HTTP_400_BAD_REQUEST)
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
        classroom_id = serializer.data.get('classroom')
        start_datetime = serializer.data.get('start')
        end_datetime = serializer.data.get('end')
        #TODO help need to think
        if Schedule.objects.all().filter(classroom=classroom_id, start__lt=end_datetime,
                                         end__lte=end_datetime).count() != 0:
            return Response({
                'status': '400',
                'message': 'Classroom is already occupied in that schedule',
            }, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def post(self, request, *args, **kwargs):
        self.request.data['classroom'] = kwargs['pk']
        return self.create(request, *args, **kwargs)


class ClassroomScheduleListView(generics.GenericAPIView,
                                mixins.ListModelMixin):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomWithScheduleSerializer
    filterset_fields = {
        'schedules__course_edition_id': ['exact'],
        'schedules__start': ['gte'],
        'schedules__end': ['lte'],
        'schedules__type': ['exact'],
    }

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('schedules__course_edition_id', None):
            return Response({
                'status': '400',
                'message': 'A course_edition_id is needed to filter the Schedules',
            }, status=status.HTTP_400_BAD_REQUEST)
        return self.list(request, *args, **kwargs)
