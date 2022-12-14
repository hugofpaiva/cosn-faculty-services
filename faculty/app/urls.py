"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

from faculty import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('faculties/', views.FacultyListView.as_view()),
    path('faculty/<int:pk>/', views.FacultyDetailsView.as_view()),
    path('faculty/', views.FacultyCreateView.as_view()),

    path('articles/', views.ArticleListView.as_view()),
    path('article/<int:pk>/', views.ArticleDetailsView.as_view()),
    path('article/', views.ArticleCreateView.as_view()),

    path('certificate/', views.CertificateCreateView.as_view()),

    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
