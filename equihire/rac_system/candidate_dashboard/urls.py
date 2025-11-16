from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Import auth_views

app_name = 'candidate_dashboard'

urlpatterns = [
    path('jobs/', views.job_listings, name='job_listings'),
    path('candidate_dashboard/', views.dashboard, name='dashboard'),
    path('jobs/<int:job_posting_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_posting_id>/apply/', views.apply_for_job, name='apply_for_job'),
    path('jobs/<int:job_posting_id>/confirmation/', views.application_confirmation, name='application_confirmation'),
]

