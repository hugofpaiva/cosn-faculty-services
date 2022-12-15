from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from classroom import views

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),

    path('classroom/<int:pk>/', views.ClassroomUpdateView.as_view()),
    path('classroom/<int:pk>/book/', views.ScheduleCreateView.as_view()),
    path('classrooms/', views.ClassroomListView.as_view()),
    path('classrooms/schedules/', views.ClassroomScheduleListView.as_view()),

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
