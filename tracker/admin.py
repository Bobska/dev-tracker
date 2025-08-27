from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Project, Application, Task, Artifact, Decision, Integration


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'owner', 'completion_percentage_display', 'overdue_tasks_count_display', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'completion_percentage', 'overdue_tasks_count']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('name', 'description', 'status', 'owner')
        }),
        ('Dates', {
            'fields': ('start_date', 'target_date')
        }),
        ('Statistics', {
            'fields': ('completion_percentage', 'overdue_tasks_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def completion_percentage_display(self, obj):
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
    completion_percentage_display.short_description = 'Completion'

    def overdue_tasks_count_display(self, obj):
        count = obj.overdue_tasks_count
        if count > 0:
            return format_html('<span style="color: red;">⚠ {}</span>', count)
        return format_html('<span style="color: green;">✓ 0</span>')
    overdue_tasks_count_display.short_description = 'Overdue Tasks'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'complexity', 'estimated_weeks', 'tasks_completion_display']
    list_filter = ['status', 'complexity', 'project', 'created_at']
    search_fields = ['name', 'description', 'project__name']
    readonly_fields = ['created_at', 'updated_at', 'tasks_completion_percentage']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('project', 'name', 'description')
        }),
        ('Details', {
            'fields': ('complexity', 'status', 'estimated_weeks', 'features')
        }),
        ('Statistics', {
            'fields': ('tasks_completion_percentage',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def tasks_completion_display(self, obj):
        percentage = obj.tasks_completion_percentage
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
    tasks_completion_display.short_description = 'Task Completion'


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ['name', 'application', 'type', 'version', 'status', 'created_by', 'updated_at']
    list_filter = ['type', 'status', 'application', 'created_at']
    search_fields = ['name', 'description', 'application__name']
    readonly_fields = ['created_at', 'updated_at', 'file_size_mb']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('application', 'name', 'type', 'description')
        }),
        ('Content', {
            'fields': ('file_upload', 'content', 'version', 'status')
        }),
        ('Details', {
            'fields': ('created_by', 'file_size_mb'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def file_size_mb(self, obj):
        size = obj.file_size_mb
        if size > 0:
            return f"{size} MB"
        return "No file"
    file_size_mb.short_description = 'File Size'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'application', 'status', 'priority', 'assignee', 'due_date', 'is_overdue_display']
    list_filter = ['status', 'priority', 'assignee', 'application', 'created_at']
    search_fields = ['title', 'description', 'application__name']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue', 'hours_variance']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('application', 'title', 'description')
        }),
        ('Assignment', {
            'fields': ('priority', 'status', 'assignee', 'due_date')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours', 'hours_variance'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠ Overdue</span>')
        return format_html('<span style="color: green;">✓ On Time</span>')
    is_overdue_display.short_description = 'Status'

    def hours_variance(self, obj):
        variance = obj.hours_variance
        if variance is None:
            return "N/A"
        elif variance > 0:
            return format_html('<span style="color: red;">+{} hrs</span>', variance)
        elif variance < 0:
            return format_html('<span style="color: green;">{} hrs</span>', variance)
        else:
            return format_html('<span style="color: blue;">On Target</span>')
    hours_variance.short_description = 'Hour Variance'


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'impact', 'decided_date', 'decision_maker']
    list_filter = ['status', 'impact', 'project', 'decided_date']
    search_fields = ['title', 'description', 'decision_maker']
    readonly_fields = ['created_at', 'updated_at', 'days_since_creation', 'is_pending_too_long']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('project', 'title', 'description')
        }),
        ('Decision Details', {
            'fields': ('status', 'impact', 'decided_date', 'decision_maker')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'days_since_creation', 'is_pending_too_long'),
            'classes': ('collapse',)
        }),
    ]

    def days_since_creation(self, obj):
        days = obj.days_since_creation
        return f"{days} days"
    days_since_creation.short_description = 'Age'

    def is_pending_too_long(self, obj):
        if obj.is_pending_too_long:
            return format_html('<span style="color: red;">⚠ Too Long</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    is_pending_too_long.short_description = 'Pending Status'


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'integration_type', 'status', 'complexity', 'estimated_weeks', 'estimated_hours_display']
    list_filter = ['status', 'complexity', 'integration_type', 'from_app__project']
    search_fields = ['description', 'from_app__name', 'to_app__name']
    readonly_fields = ['created_at', 'updated_at', 'complexity_multiplier', 'estimated_hours']
    
    fieldsets = [
        ('Integration Details', {
            'fields': ('from_app', 'to_app', 'integration_type', 'description')
        }),
        ('Planning', {
            'fields': ('status', 'complexity', 'estimated_weeks')
        }),
        ('Calculations', {
            'fields': ('complexity_multiplier', 'estimated_hours'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def complexity_multiplier(self, obj):
        return f"{obj.complexity_multiplier}x"
    complexity_multiplier.short_description = 'Complexity Factor'

    def estimated_hours_display(self, obj):
        return f"{obj.estimated_hours} hours"
    estimated_hours_display.short_description = 'Total Hours'
