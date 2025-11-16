from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('upload/', views.upload_and_match, name='upload_and_match'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),  
]
