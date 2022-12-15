from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

from faculty import views


def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),

    path('faculties/', views.FacultyListView.as_view()),
    path('faculty/<int:pk>/', views.FacultyDetailsView.as_view()),
    path('faculty/', views.FacultyCreateView.as_view()),

    path('articles/', views.ArticleListView.as_view()),
    path('article/<int:pk>/', views.ArticleDetailsView.as_view()),
    path('article/', views.ArticleCreateView.as_view()),

    path('sentry-debug/', trigger_error),

    path('certificate/', views.CertificateCreateView.as_view()),

    # OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Prometheus
    path('', include('django_prometheus.urls')),

    # Health Check
    path('ht/', include('health_check.urls')),
]
