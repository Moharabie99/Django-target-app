# dashboard/urls.py

from django.contrib import admin
from django.urls import path
from dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('upload/', views.upload, name='upload'),
    path('results/', views.results_view, name='results'),
    path('download/<str:filename>/', views.download_report, name='download_report'),
    path('home_page/', views.home_page, name='home_page'),
]



