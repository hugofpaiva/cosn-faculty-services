from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiParameter
from rest_framework import generics, mixins, status
from rest_framework.response import Response

from classroom.models import Schedule, Classroom
from classroom.serializers import ScheduleSerializer, ClassroomWithoutScheduleSerializer, \
    ClassroomWithScheduleSerializer, ErrorSerializer


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

    @extend_schema(
        parameters=[
            OpenApiParameter(name="faculty_id", required=True, type=int),
        ],
    )
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('faculty_id', None):
            return Response({
                'details': 'A faculty_id is needed to filter the Classrooms',
            }, status=status.HTTP_400_BAD_REQUEST)
        return self.list(request, *args, **kwargs)


class ClassroomUpdateView(generics.GenericAPIView,
                          mixins.UpdateModelMixin):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomWithoutScheduleSerializer

    @extend_schema(
        request=ClassroomWithoutScheduleSerializer,
        examples=[OpenApiExample(
            name="Change overall availability of a classroom",
            description="Change overall availability of a classroom to not available",
            request_only=True,
            status_codes=[200],
            value={
                "is_available": False,
            }
        ),
            OpenApiExample(
                name="Changed overall availability of a classroom",
                description="Changed overall availability of a classroom to not available",
                response_only=True,
                status_codes=[200],
                value={
                    "id": 1,
                    "name": "B250",
                    "is_available": False,
                    "seats": 25
                }
            )

        ],
        responses={200: ClassroomWithoutScheduleSerializer})
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ScheduleCreateView(generics.GenericAPIView,
                         mixins.CreateModelMixin):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            classroom = Classroom.objects.get(pk=kwargs['pk'])
            if not classroom.is_available:
                return Response({
                    'details': 'Classroom is closed for maintenance',
                }, status=status.HTTP_400_BAD_REQUEST)

            start_datetime = serializer.validated_data.get('start')
            end_datetime = serializer.validated_data.get('end')

            if end_datetime <= start_datetime:
                return Response({
                    'details': 'End date must be higher than start date',
                }, status=status.HTTP_400_BAD_REQUEST)

            if Schedule.objects.all().filter(classroom=classroom, start__gte=start_datetime,
                                             end__lte=start_datetime).count() != 0 or \
                    Schedule.objects.all().filter(classroom=classroom, start__lte=start_datetime,
                                                  end__gte=start_datetime).count() != 0 or \
                    Schedule.objects.all().filter(classroom=classroom, start__lte=end_datetime,
                                                  end__gte=end_datetime).count() != 0:
                return Response({
                    'details': 'Classroom is already occupied in that schedule',
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.validated_data['classroom'] = classroom
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Classroom.DoesNotExist:
            return Response({
                'details': 'Classroom not found',
            }, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=ScheduleSerializer,
        examples=[
            OpenApiExample(
                name="Create Class Schedule",
                description="Create Class Schedule",
                request_only=True,
                status_codes=[201],
                value={
                    "course_edition_id": 1,
                    "start": "2022-12-11T16:02:25.301Z",
                    "end": "2022-12-11T16:02:25.301Z",
                    "type": "CL",
                },

            ),
            OpenApiExample(
                name="Create Exam Schedule",
                description="Create Exam Schedule",
                request_only=True,
                status_codes=[201],
                value={
                    "course_edition_id": 1,
                    "start": "2022-12-11T16:02:25.301Z",
                    "end": "2022-12-11T16:02:25.301Z",
                    "type": "EX",
                },

            ),
            OpenApiExample(
                name="Created Class Successfully",
                description="Created Class Successfully",
                response_only=True,
                status_codes=[201],
                value={
                    "id": 1,
                    "course_edition_id": 1,
                    "start": "2022-12-11T16:02:25.301Z",
                    "end": "2022-12-11T16:02:25.301Z",
                    "type": "CL",
                    "classroom": 1
                },

            ),
            OpenApiExample(
                name="Created Exam Successfully",
                description="Created Exam Successfully",
                response_only=True,
                status_codes=[201],
                value={
                    "id": 1,
                    "course_edition_id": 1,
                    "start": "2022-12-11T16:02:25.301Z",
                    "end": "2022-12-11T16:02:25.301Z",
                    "type": "EX",
                    "classroom": 1
                },

            ),
            OpenApiExample(
                name="Classroom Not Found",
                status_codes=[404],
                response_only=True,
                description="Classroom Not Found",
                value={'details': 'Classroom not found'},

            ),
            OpenApiExample(
                name="Classroom is closed for maintenance",
                status_codes=[400],
                response_only=True,
                description="Classroom is closed for maintenance",
                value={'details': 'Classroom is closed for maintenance'},

            ),
            OpenApiExample(
                name="Classroom is already occupied in that schedule",
                status_codes=[400],
                response_only=True,
                description="Classroom is already occupied in that schedule",
                value={'details': 'Classroom is already occupied in that schedule'},

            ),
            OpenApiExample(
                name="End date must be higher than start date",
                status_codes=[400],
                response_only=True,
                description="End date must be higher than start date",
                value={'details': 'End date must be higher than start date'},

            )
        ],
        responses={201: ScheduleSerializer,
                   404: ErrorSerializer, 400: ErrorSerializer})
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = queryset.distinct()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="schedules__course_edition_id", required=True, type=int),
        ],
    )
    def get(self, request, *args, **kwargs):
        if not request.query_params.get('schedules__course_edition_id', None):
            return Response({
                'details': 'A course_edition_id is needed to filter the Schedules',
            }, status=status.HTTP_400_BAD_REQUEST)
        return self.list(request, *args, **kwargs)
