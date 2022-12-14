from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import generics, mixins, status
from django.http import Http404
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from faculty.models import Faculty, Article
from faculty.serializers import FacultySerializer, ArticleSerializer, ErrorSerializer
from datetime import datetime

from confluent_kafka import Producer

kafka_conf = {
    'bootstrap.servers': 'dynamicity2022.fe.up.pt',
    'session.timeout.ms': 6000,
}
TOPIC_CREATE_FACULTY = 'faculty.created'
TOPIC_ARCHIVE_FACULTY = 'faculty.archived'

kafka_producer = Producer(**kafka_conf)


def kafka_delivery_callback(err, msg):
    if err:
        print('%% Message failed delivery: %s\n' % err)
    else:
        print('%% Message delivered to %s [%d]\n' %
              (msg.topic(), msg.partition()))


def kafka_send_event(topic: str, event: str):
    try:
        kafka_producer.produce(topic, event, callback=kafka_delivery_callback)
    except BufferError as e:
        print(
            '%% Local producer queue is full (%d messages awaiting delivery): try again\n'
            % len(kafka_producer))


# Create your views here.
class FacultyListView(generics.GenericAPIView, mixins.ListModelMixin):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FacultyDetailsView(
        generics.GenericAPIView,
        mixins.DestroyModelMixin,
        mixins.RetrieveModelMixin,
):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(request=None,
                   examples=[
                       OpenApiExample(
                           name="Archived Successfully",
                           description="Archived with success",
                           status_codes=[204],
                       ),
                       OpenApiExample(
                           name="Not Found",
                           status_codes=[404],
                           description="Faculty not found",
                           value={'details': 'Not found'},
                       ),
                       OpenApiExample(
                           name="Already archived",
                           status_codes=[400],
                           description="Faculty already archived",
                           value={'details': 'Faculty already archived.'},
                       )
                   ],
                   responses={
                       204: None,
                       404: ErrorSerializer,
                       400: ErrorSerializer
                   })
    def delete(self, request, *args, **kwargs):
        try:
            faculty = Faculty.objects.get(pk=kwargs['pk'])

            if not faculty.is_active:
                return Response({
                    'details': 'Faculty already archived.',
                },
                                status=status.HTTP_400_BAD_REQUEST)
            faculty.is_active = False
            faculty.save()

            kafka_send_event(TOPIC_ARCHIVE_FACULTY,
                             f'{faculty.pk}, "{datetime.now()}"')
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Faculty.DoesNotExist:
            raise Http404


class FacultyCreateView(generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        faculty = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers), faculty

    def post(self, request, *args, **kwargs):
        response, faculty = self.create(request, *args, **kwargs)

        kafka_send_event(TOPIC_CREATE_FACULTY,
                         f'{faculty.id}, "{datetime.now()}"')
        return response


class ArticleListView(generics.GenericAPIView, mixins.ListModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filterset_fields = {
        'faculty': ['exact'],
        'created_at': ['gte', 'lte'],
    }
    search_fields = ['author', 'title']
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ArticleDetailsView(
        generics.GenericAPIView,
        mixins.DestroyModelMixin,
        mixins.RetrieveModelMixin,
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ArticleCreateView(generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
