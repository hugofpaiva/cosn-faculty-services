from django.shortcuts import render
from rest_framework import generics, mixins, status
from django.http import Http404
from rest_framework.response import Response

from faculty.models import Faculty, Article
from faculty.serializers import FacultySerializer, ArticleSerializer


# Create your views here.
class FacultyListView(generics.GenericAPIView,
                      mixins.ListModelMixin):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FacultyDetailsView(generics.GenericAPIView, mixins.DestroyModelMixin,
                         mixins.RetrieveModelMixin,
                         ):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            faculty = Faculty.objects.get(pk=kwargs['pk'])

            if not faculty.is_active:
                return Response({
                    'status': '400',
                    'message': 'Faculty already archived.',
                }, status=status.HTTP_400_BAD_REQUEST)
            #TODO send to message broker
            faculty.is_active = False
            faculty.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Faculty.DoesNotExist:
            raise Http404


class FacultyCreateView(generics.GenericAPIView,
                        mixins.CreateModelMixin):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ArticleListView(generics.GenericAPIView,
                      mixins.ListModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ArticleDetailsView(generics.GenericAPIView, mixins.DestroyModelMixin,
                         mixins.RetrieveModelMixin,
                         ):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ArticleCreateView(generics.GenericAPIView,
                        mixins.CreateModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
