from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Project URLs
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/dashboard/', views.project_dashboard_view, name='project_dashboard'),
    
    # Application URLs
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/create/', views.ApplicationCreateView.as_view(), name='application_create'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('applications/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name='application_update'),
    
    # Task URLs
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/bulk/', views.bulk_task_operations_view, name='bulk_task_operations'),
    
    # Artifact URLs
    path('artifacts/', views.ArtifactListView.as_view(), name='artifact_list'),
    path('artifacts/create/', views.ArtifactCreateView.as_view(), name='artifact_create'),
    path('artifacts/<int:pk>/', views.ArtifactDetailView.as_view(), name='artifact_detail'),
    path('artifacts/<int:pk>/edit/', views.ArtifactUpdateView.as_view(), name='artifact_update'),
    path('artifacts/<int:pk>/download/', views.artifact_download_view, name='artifact_download'),
    
    # Decision URLs
    path('decisions/', views.DecisionListView.as_view(), name='decision_list'),
    path('decisions/create/', views.DecisionCreateView.as_view(), name='decision_create'),
    path('decisions/<int:pk>/edit/', views.DecisionUpdateView.as_view(), name='decision_update'),
    
    # Integration URLs
    path('integrations/', views.IntegrationListView.as_view(), name='integration_list'),
    path('integrations/create/', views.IntegrationCreateView.as_view(), name='integration_create'),
    path('integrations/<int:pk>/', views.IntegrationDetailView.as_view(), name='integration_detail'),
    path('integrations/<int:pk>/edit/', views.IntegrationUpdateView.as_view(), name='integration_update'),
    
    # Search and API URLs
    path('search/', views.search_view, name='search'),
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
