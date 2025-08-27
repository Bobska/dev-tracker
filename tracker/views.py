from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Q
from .models import Project, Application, Task, Artifact, Decision, Integration


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard view showing project statistics and recent activity.
    """
    template_name = 'tracker/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's projects
        user_projects = Project.objects.filter(
            Q(created_by=self.request.user) | Q(team_members=self.request.user)
        ).distinct()
        
        # Dashboard statistics
        context.update({
            'total_projects': user_projects.count(),
            'active_projects': user_projects.filter(status='active').count(),
            'total_applications': Application.objects.filter(project__in=user_projects).count(),
            'total_tasks': Task.objects.filter(project__in=user_projects).count(),
            'pending_tasks': Task.objects.filter(
                project__in=user_projects,
                status__in=['todo', 'in_progress']
            ).count(),
            'completed_tasks': Task.objects.filter(
                project__in=user_projects,
                status='completed'
            ).count(),
            
            # Recent items
            'recent_projects': user_projects[:5],
            'recent_tasks': Task.objects.filter(project__in=user_projects)[:10],
            'recent_artifacts': Artifact.objects.filter(application__project__in=user_projects)[:5],
        })
        
        return context


# Project Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'tracker/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(created_by=user) | Q(team_members=user)
        ).distinct()


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'tracker/project_detail.html'
    context_object_name = 'project'


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'tracker/project_form.html'
    fields = ['name', 'description', 'status', 'start_date', 'end_date', 'repository_url', 'documentation_url', 'team_members']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Project "{form.instance.name}" created successfully.')
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'tracker/project_form.html'
    fields = ['name', 'description', 'status', 'start_date', 'end_date', 'repository_url', 'documentation_url', 'team_members']

    def form_valid(self, form):
        messages.success(self.request, f'Project "{form.instance.name}" updated successfully.')
        return super().form_valid(form)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'tracker/project_confirm_delete.html'
    success_url = reverse_lazy('tracker:project_list')

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        messages.success(request, f'Project "{project.name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Application Views
class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'tracker/application_list.html'
    context_object_name = 'applications'
    paginate_by = 15


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'tracker/application_detail.html'
    context_object_name = 'application'


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    template_name = 'tracker/application_form.html'
    fields = ['project', 'name', 'description', 'status', 'technology_stack', 'version', 'repository_url', 'demo_url', 'assigned_to']

    def form_valid(self, form):
        messages.success(self.request, f'Application "{form.instance.name}" created successfully.')
        return super().form_valid(form)


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    template_name = 'tracker/application_form.html'
    fields = ['project', 'name', 'description', 'status', 'technology_stack', 'version', 'repository_url', 'demo_url', 'assigned_to']

    def form_valid(self, form):
        messages.success(self.request, f'Application "{form.instance.name}" updated successfully.')
        return super().form_valid(form)


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'tracker/application_confirm_delete.html'
    success_url = reverse_lazy('tracker:application_list')


# Task Views
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tracker/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tracker/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tracker/task_form.html'
    fields = ['title', 'description', 'project', 'application', 'status', 'priority', 'assignee_type', 'assigned_to', 'estimated_hours', 'due_date']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Task "{form.instance.title}" created successfully.')
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'tracker/task_form.html'
    fields = ['title', 'description', 'project', 'application', 'status', 'priority', 'assignee_type', 'assigned_to', 'estimated_hours', 'actual_hours', 'due_date', 'completed_at']

    def form_valid(self, form):
        messages.success(self.request, f'Task "{form.instance.title}" updated successfully.')
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tracker/task_confirm_delete.html'
    success_url = reverse_lazy('tracker:task_list')


# Artifact Views
class ArtifactListView(LoginRequiredMixin, ListView):
    model = Artifact
    template_name = 'tracker/artifact_list.html'
    context_object_name = 'artifacts'
    paginate_by = 15


class ArtifactDetailView(LoginRequiredMixin, DetailView):
    model = Artifact
    template_name = 'tracker/artifact_detail.html'
    context_object_name = 'artifact'


class ArtifactCreateView(LoginRequiredMixin, CreateView):
    model = Artifact
    template_name = 'tracker/artifact_form.html'
    fields = ['name', 'description', 'application', 'artifact_type', 'version', 'file', 'content', 'url']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Artifact "{form.instance.name}" created successfully.')
        return super().form_valid(form)


class ArtifactUpdateView(LoginRequiredMixin, UpdateView):
    model = Artifact
    template_name = 'tracker/artifact_form.html'
    fields = ['name', 'description', 'application', 'artifact_type', 'version', 'file', 'content', 'url']

    def form_valid(self, form):
        messages.success(self.request, f'Artifact "{form.instance.name}" updated successfully.')
        return super().form_valid(form)


class ArtifactDeleteView(LoginRequiredMixin, DeleteView):
    model = Artifact
    template_name = 'tracker/artifact_confirm_delete.html'
    success_url = reverse_lazy('tracker:artifact_list')


class ArtifactDownloadView(LoginRequiredMixin, DetailView):
    model = Artifact

    def get(self, request, *args, **kwargs):
        artifact = self.get_object()
        if artifact.file:
            response = HttpResponse(artifact.file.read())
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{artifact.file.name}"'
            return response
        else:
            messages.error(request, 'No file available for download.')
            return redirect('tracker:artifact_detail', pk=artifact.pk)


# Decision Views
class DecisionListView(LoginRequiredMixin, ListView):
    model = Decision
    template_name = 'tracker/decision_list.html'
    context_object_name = 'decisions'
    paginate_by = 15


class DecisionDetailView(LoginRequiredMixin, DetailView):
    model = Decision
    template_name = 'tracker/decision_detail.html'
    context_object_name = 'decision'


class DecisionCreateView(LoginRequiredMixin, CreateView):
    model = Decision
    template_name = 'tracker/decision_form.html'
    fields = ['title', 'description', 'project', 'application', 'status', 'rationale', 'consequences', 'alternatives']

    def form_valid(self, form):
        form.instance.decision_maker = self.request.user
        messages.success(self.request, f'Decision "{form.instance.title}" created successfully.')
        return super().form_valid(form)


class DecisionUpdateView(LoginRequiredMixin, UpdateView):
    model = Decision
    template_name = 'tracker/decision_form.html'
    fields = ['title', 'description', 'project', 'application', 'status', 'rationale', 'consequences', 'alternatives']

    def form_valid(self, form):
        messages.success(self.request, f'Decision "{form.instance.title}" updated successfully.')
        return super().form_valid(form)


class DecisionDeleteView(LoginRequiredMixin, DeleteView):
    model = Decision
    template_name = 'tracker/decision_confirm_delete.html'
    success_url = reverse_lazy('tracker:decision_list')


# Integration Views
class IntegrationListView(LoginRequiredMixin, ListView):
    model = Integration
    template_name = 'tracker/integration_list.html'
    context_object_name = 'integrations'
    paginate_by = 15


class IntegrationDetailView(LoginRequiredMixin, DetailView):
    model = Integration
    template_name = 'tracker/integration_detail.html'
    context_object_name = 'integration'


class IntegrationCreateView(LoginRequiredMixin, CreateView):
    model = Integration
    template_name = 'tracker/integration_form.html'
    fields = ['name', 'description', 'source_application', 'target_application', 'status', 'complexity', 'estimated_hours', 'dependencies', 'notes', 'assigned_to']

    def form_valid(self, form):
        messages.success(self.request, f'Integration "{form.instance.name}" created successfully.')
        return super().form_valid(form)


class IntegrationUpdateView(LoginRequiredMixin, UpdateView):
    model = Integration
    template_name = 'tracker/integration_form.html'
    fields = ['name', 'description', 'source_application', 'target_application', 'status', 'complexity', 'estimated_hours', 'actual_hours', 'dependencies', 'notes', 'assigned_to']

    def form_valid(self, form):
        messages.success(self.request, f'Integration "{form.instance.name}" updated successfully.')
        return super().form_valid(form)


class IntegrationDeleteView(LoginRequiredMixin, DeleteView):
    model = Integration
    template_name = 'tracker/integration_confirm_delete.html'
    success_url = reverse_lazy('tracker:integration_list')
