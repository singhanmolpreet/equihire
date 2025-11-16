from django.urls import path
from . import views

app_name = 'job_postings'  # Define the app namespace

urlpatterns = [
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('add/', views.add_job_posting, name='add_job_posting'),
    path('edit/<int:job_posting_id>/', views.edit_job_posting, name='edit_job_posting'),
    path('delete/<int:job_posting_id>/', views.delete_job_posting, name='delete_job_posting'),
    path('assign-expert/<int:job_posting_id>/', views.assign_expert_by_email, name='assign_expert_by_email'),
]

# job_postings/urls.py (Example)

