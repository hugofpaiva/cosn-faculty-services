from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from tuition import views


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('admin/', admin.site.urls),

    path('tuition-fees/', views.TuitionFeeListView.as_view()),
    path('tuition-fee/<int:pk>/', views.TuitionFeeDetailsView.as_view()),
    path('tuition-fee/<int:pk>/pay', views.TuitionFeePayView.as_view()),
    path('tuition-fee/<int:pk>/receipt', views.TuitionFeePayView.as_view()),
    path('tuition-fee/', views.TuitionFeeCreateView.as_view()),

    path('sentry-debug/', trigger_error),

    # OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Prometheus
    path('', include('django_prometheus.urls')),

    # Health Check
    path('ht/', include('health_check.urls')),
]
