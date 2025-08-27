from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Project, Application, Task, Artifact, Decision, Integration


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_by', 'team_members_count', 'completion_percentage', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['team_members']
    readonly_fields = ['created_at', 'updated_at', 'completion_percentage']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('name', 'description', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('URLs', {
            'fields': ('repository_url', 'documentation_url')
        }),
        ('Team', {
            'fields': ('created_by', 'team_members')
        }),
        ('Statistics', {
            'fields': ('completion_percentage',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def team_members_count(self, obj):
        return obj.team_members.count()
    team_members_count.short_description = 'Team Size'

    def completion_percentage(self, obj):
        percentage = obj.completion_percentage
        if percentage >= 90:
            color = 'green'
        elif percentage >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, percentage
        )
    completion_percentage.short_description = 'Completion'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'technology_stack', 'version', 'assigned_to', 'created_at']
    list_filter = ['status', 'technology_stack', 'project', 'created_at']
    search_fields = ['name', 'description', 'project__name']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('project', 'name', 'description', 'status')
        }),
        ('Technical Details', {
            'fields': ('technology_stack', 'version')
        }),
        ('URLs', {
            'fields': ('repository_url', 'demo_url')
        }),
        ('Assignment', {
            'fields': ('assigned_to',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'application', 'status', 'priority', 'assignee_type', 'assigned_to', 'due_date', 'is_overdue']
    list_filter = ['status', 'priority', 'assignee_type', 'project', 'application', 'created_at']
    search_fields = ['title', 'description', 'project__name', 'application__name']
    date_hierarchy = 'due_date'
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('title', 'description', 'project', 'application')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Assignment', {
            'fields': ('assignee_type', 'assigned_to')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours', 'due_date', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']

    def is_overdue(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">Yes</span>')
        return 'No'
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ['name', 'application', 'artifact_type', 'version', 'file_size_display', 'created_by', 'created_at']
    list_filter = ['artifact_type', 'application__project', 'application', 'created_at']
    search_fields = ['name', 'description', 'application__name', 'application__project__name']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('name', 'description', 'application', 'artifact_type', 'version')
        }),
        ('Content', {
            'fields': ('file', 'content', 'url')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']

    def file_size_display(self, obj):
        if obj.file:
            return f"{obj.file_size_mb} MB"
        return "No file"
    file_size_display.short_description = 'File Size'


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'application', 'status', 'decision_maker', 'created_at']
    list_filter = ['status', 'project', 'application', 'created_at']
    search_fields = ['title', 'description', 'project__name', 'application__name']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('title', 'description', 'project', 'application', 'status')
        }),
        ('Decision Details', {
            'fields': ('rationale', 'consequences', 'alternatives')
        }),
        ('Metadata', {
            'fields': ('decision_maker', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_application', 'target_application', 'status', 'complexity', 'assigned_to', 'created_at']
    list_filter = ['status', 'complexity', 'source_application__project', 'created_at']
    search_fields = ['name', 'description', 'source_application__name', 'target_application__name']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('name', 'description', 'source_application', 'target_application')
        }),
        ('Status & Complexity', {
            'fields': ('status', 'complexity')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Details', {
            'fields': ('dependencies', 'notes', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']
