from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Project URLs
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    
    # Application URLs
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/create/', views.ApplicationCreateView.as_view(), name='application_create'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('applications/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name='application_update'),
    path('applications/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application_delete'),
    
    # Task URLs
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    
    # Artifact URLs
    path('artifacts/', views.ArtifactListView.as_view(), name='artifact_list'),
    path('artifacts/create/', views.ArtifactCreateView.as_view(), name='artifact_create'),
    path('artifacts/<int:pk>/', views.ArtifactDetailView.as_view(), name='artifact_detail'),
    path('artifacts/<int:pk>/edit/', views.ArtifactUpdateView.as_view(), name='artifact_update'),
    path('artifacts/<int:pk>/delete/', views.ArtifactDeleteView.as_view(), name='artifact_delete'),
    path('artifacts/<int:pk>/download/', views.ArtifactDownloadView.as_view(), name='artifact_download'),
    
    # Decision URLs
    path('decisions/', views.DecisionListView.as_view(), name='decision_list'),
    path('decisions/create/', views.DecisionCreateView.as_view(), name='decision_create'),
    path('decisions/<int:pk>/', views.DecisionDetailView.as_view(), name='decision_detail'),
    path('decisions/<int:pk>/edit/', views.DecisionUpdateView.as_view(), name='decision_update'),
    path('decisions/<int:pk>/delete/', views.DecisionDeleteView.as_view(), name='decision_delete'),
    
    # Integration URLs
    path('integrations/', views.IntegrationListView.as_view(), name='integration_list'),
    path('integrations/create/', views.IntegrationCreateView.as_view(), name='integration_create'),
    path('integrations/<int:pk>/', views.IntegrationDetailView.as_view(), name='integration_detail'),
    path('integrations/<int:pk>/edit/', views.IntegrationUpdateView.as_view(), name='integration_update'),
    path('integrations/<int:pk>/delete/', views.IntegrationDeleteView.as_view(), name='integration_delete'),
]
