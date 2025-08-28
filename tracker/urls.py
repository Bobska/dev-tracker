"""
FamilyHub Development Tracker - Application URLs

URL patterns for the main tracker application.
Provides RESTful routing for all development tracking resources.
"""
from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    # Dashboard - Main entry point
    path('', views.dashboard_view, name='dashboard'),
    
    # Project Management URLs
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/<int:pk>/dashboard/', views.project_dashboard_view, name='project_dashboard'),
    
    # Application Management URLs
    path('apps/', views.ApplicationListView.as_view(), name='application_list'),
    path('apps/new/', views.ApplicationCreateView.as_view(), name='application_create'),
    path('apps/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('apps/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name='application_update'),
    path('apps/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application_delete'),
    
    # Task Management URLs
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/new/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('tasks/bulk/', views.bulk_task_operations_view, name='bulk_task_operations'),
    
    # Artifact Management URLs
    path('artifacts/', views.ArtifactListView.as_view(), name='artifact_list'),
    path('artifacts/new/', views.ArtifactCreateView.as_view(), name='artifact_create'),
    path('artifacts/<int:pk>/', views.ArtifactDetailView.as_view(), name='artifact_detail'),
    path('artifacts/<int:pk>/edit/', views.ArtifactUpdateView.as_view(), name='artifact_update'),
    path('artifacts/<int:pk>/delete/', views.ArtifactDeleteView.as_view(), name='artifact_delete'),
    path('artifacts/<int:pk>/download/', views.artifact_download_view, name='artifact_download'),
    
    # Decision Log URLs
    path('decisions/', views.DecisionListView.as_view(), name='decision_list'),
    path('decisions/new/', views.DecisionCreateView.as_view(), name='decision_create'),
    path('decisions/<int:pk>/', views.DecisionDetailView.as_view(), name='decision_detail'),
    path('decisions/<int:pk>/edit/', views.DecisionUpdateView.as_view(), name='decision_update'),
    path('decisions/<int:pk>/delete/', views.DecisionDeleteView.as_view(), name='decision_delete'),
    
    # Integration Planning URLs
    path('integrations/', views.IntegrationListView.as_view(), name='integration_list'),
    path('integrations/new/', views.IntegrationCreateView.as_view(), name='integration_create'),
    path('integrations/<int:pk>/', views.IntegrationDetailView.as_view(), name='integration_detail'),
    path('integrations/<int:pk>/edit/', views.IntegrationUpdateView.as_view(), name='integration_update'),
    path('integrations/<int:pk>/delete/', views.IntegrationDeleteView.as_view(), name='integration_delete'),
    
    # Requirements URLs
    path('requirements/', views.RequirementListView.as_view(), name='requirement_list'),
    path('requirements/new/', views.RequirementCreateView.as_view(), name='requirement_create'),
    path('requirements/<int:pk>/', views.RequirementDetailView.as_view(), name='requirement_detail'),
    path('requirements/<int:pk>/edit/', views.RequirementUpdateView.as_view(), name='requirement_update'),
    path('requirements/<int:pk>/delete/', views.RequirementDeleteView.as_view(), name='requirement_delete'),
    
    # Search and Utility
    path('search/', views.search_view, name='search'),
]
