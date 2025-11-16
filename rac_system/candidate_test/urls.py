from django.urls import path
from . import views

urlpatterns = [
    # Company Views
    path('test/create/', views.create_test, name='create_test'),
    path('test/success/<int:test_id>/', views.test_success, name='test_success'),

    # Candidate Views
    path('test/<int:test_id>/take/', views.take_test, name='take_test'),
    path('test/results/<int:attempt_id>/', views.test_results, name='test_results'),
]