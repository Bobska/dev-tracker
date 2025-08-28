from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML, Field
from crispy_forms.bootstrap import FormActions
import json
from .models import Project, Application, Artifact, Task, Decision, Integration

User = get_user_model()


class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects."""
    
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'status', 'start_date', 
            'target_date', 'owner'
        ]
        widgets = {
            'start_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'target_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control'}
            ),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Project Information',
                Row(
                    Column('name', css_class='col-md-8'),
                    Column('owner', css_class='col-md-4'),
                ),
                'description',
                Row(
                    Column('status', css_class='col-md-4'),
                    Column('start_date', css_class='col-md-4'),
                    Column('target_date', css_class='col-md-4'),
                ),
            ),
            FormActions(
                Submit('submit', 'Save Project', css_class='btn btn-primary'),
                HTML('<a href="{% url "tracker:project_list" %}" class="btn btn-secondary ms-2">Cancel</a>'),
            )
        )

    def clean(self):
        """Custom validation to ensure target_date is after start_date."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        target_date = cleaned_data.get('target_date')

        if start_date and target_date:
            if target_date <= start_date:
                raise ValidationError(
                    "Target date must be after the start date."
                )
        
        return cleaned_data


class ApplicationForm(forms.ModelForm):
    """Form for creating and updating applications with dynamic features."""
    
    # Dynamic features field
    features_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'placeholder': 'Enter features separated by newlines...',
            'class': 'form-control'
        }),
        required=False,
        help_text="Enter each feature on a new line"
    )

    class Meta:
        model = Application
        fields = [
            'project', 'name', 'description', 'complexity', 
            'status', 'estimated_weeks'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'complexity': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'estimated_weeks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate features text field if editing
        if self.instance.pk and self.instance.features:
            self.fields['features_text'].initial = '\n'.join(self.instance.features)
        
        # Set up crispy forms helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Application Information',
                Row(
                    Column('project', css_class='col-md-6'),
                    Column('name', css_class='col-md-6'),
                ),
                'description',
                Row(
                    Column('complexity', css_class='col-md-4'),
                    Column('status', css_class='col-md-4'),
                    Column('estimated_weeks', css_class='col-md-4'),
                ),
                'features_text',
                HTML('<small class="text-muted">Suggested weeks based on complexity: Simple (2-4), Medium (4-8), High (8-16)</small>'),
            ),
            FormActions(
                Submit('submit', 'Save Application', css_class='btn btn-primary'),
                HTML('<a href="{% url "tracker:application_list" %}" class="btn btn-secondary ms-2">Cancel</a>'),
            )
        )

        # Add JavaScript for complexity-based suggestions
        self.fields['complexity'].widget.attrs.update({
            'onchange': 'updateEstimatedWeeks(this.value)'
        })

    def clean_features_text(self):
        """Convert features text to list format."""
        features_text = self.cleaned_data.get('features_text', '')
        if features_text:
            # Split by newlines and filter out empty lines
            features = [f.strip() for f in features_text.split('\n') if f.strip()]
            return features
        return []

    def save(self, commit=True):
        """Save the application with features from text field."""
        instance = super().save(commit=False)
        instance.features = self.cleaned_data.get('features_text', [])
        if commit:
            instance.save()
        return instance


class ArtifactForm(forms.ModelForm):
    """Form for creating and updating artifacts with file upload and version management."""
    
    increment_version = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Check to automatically increment version number"
    )

    class Meta:
        model = Artifact
        fields = [
            'name', 'content', 'application', 'type', 'status', 
            'file_upload', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Artifact name (required)'
            }),
            'content': forms.Textarea(attrs={
                'rows': 8, 
                'class': 'form-control',
                'placeholder': 'Enter artifact content here... (required)'
            }),
            'application': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Select application (optional)'
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'file_upload': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.py,.js,.html,.css,.md'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Additional description about this artifact... (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.attrs = {'enctype': 'multipart/form-data'}
        
        # Make application field optional
        self.fields['application'].required = False
        
        self.helper.layout = Layout(
            Fieldset(
                'Artifact Information',
                HTML('<div class="alert alert-info"><i class="bi bi-info-circle me-2"></i><strong>Required:</strong> Name and Content</div>'),
                'name',
                'content',
                HTML('<hr class="my-3">'),
                HTML('<h6 class="text-muted">Optional Fields</h6>'),
                Row(
                    Column('application', css_class='col-md-6'),
                    Column('type', css_class='col-md-6'),
                ),
                Row(
                    Column('status', css_class='col-md-6'),
                    Column(Field('increment_version', css_class='form-check-input'), css_class='col-md-6'),
                ),
                'file_upload',
                HTML('<small class="text-muted">Supported formats: PDF, DOC, DOCX, TXT, PY, JS, HTML, CSS, MD (Max 10MB)</small>'),
                'description',
            ),
            FormActions(
                Submit('submit', 'Save Artifact', css_class='btn btn-primary'),
                HTML('<a href="{% url "tracker:artifact_list" %}" class="btn btn-secondary ms-2">Cancel</a>'),
            )
        )

    def clean_file_upload(self):
        """Validate file upload."""
        file = self.cleaned_data.get('file_upload')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 10MB.")
            
            # Check file extension
            allowed_extensions = [
                'pdf', 'doc', 'docx', 'txt', 'py', 'js', 
                'html', 'css', 'md', 'json', 'xml'
            ]
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError(
                    f"File type '{file_extension}' not allowed. "
                    f"Allowed types: {', '.join(allowed_extensions)}"
                )
        return file

    def save(self, commit=True):
        """Save artifact with version increment logic."""
        instance = super().save(commit=False)
        
        # Handle version increment
        if self.cleaned_data.get('increment_version') and instance.pk:
            # Parse current version and increment
            current_version = instance.version
            try:
                major, minor = map(int, current_version.split('.'))
                minor += 1
                instance.version = f"{major}.{minor}"
            except (ValueError, AttributeError):
                # If version format is invalid, set to 1.1
                instance.version = "1.1"
        elif not instance.version:
            # Set initial version for new artifacts
            instance.version = "1.0"
        
        if commit:
            instance.save()
        return instance


class TaskForm(forms.ModelForm):
    """Form for creating and updating tasks with time tracking."""

    class Meta:
        model = Task
        fields = [
            'application', 'title', 'description', 'assignee', 
            'status', 'priority', 'due_date', 
            'estimated_hours', 'actual_hours'
        ]
        widgets = {
            'application': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1, 
                'step': 1,
                'placeholder': 'Hours'
            }),
            'actual_hours': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'step': 1,
                'placeholder': 'Hours'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Task Information',
                Row(
                    Column('application', css_class='col-md-6'),
                    Column('title', css_class='col-md-6'),
                ),
                'description',
                Row(
                    Column('assignee', css_class='col-md-6'),
                    Column('status', css_class='col-md-6'),
                ),
                Row(
                    Column('priority', css_class='col-md-4'),
                    Column('due_date', css_class='col-md-4'),
                    Column(Field('estimated_hours'), css_class='col-md-4'),
                ),
                'actual_hours',
                HTML('<small class="text-muted">Assignee options: Claude (AI assistance), GitHub Copilot (Code generation), Human (Manual tasks), Team (Collaborative work)</small>'),
            ),
            FormActions(
                Submit('submit', 'Save Task', css_class='btn btn-primary'),
                HTML('<a href="{% url "tracker:task_list" %}" class="btn btn-secondary ms-2">Cancel</a>'),
            )
        )

        # Make assignee_user conditional based on assignee_type
        # Remove conditional logic since we're using a simple choice field now

    def clean(self):
        """Custom validation for task form."""
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        estimated_hours = cleaned_data.get('estimated_hours')
        actual_hours = cleaned_data.get('actual_hours')

        # Validate due date is not in the past (for new tasks)
        if due_date and not self.instance.pk:
            if due_date < timezone.now().date():
                raise ValidationError({
                    'due_date': 'Due date cannot be in the past.'
                })

        # Validate actual hours doesn't exceed estimated by too much
        if estimated_hours and actual_hours:
            if actual_hours > estimated_hours * 2:
                self.add_error('actual_hours', 
                    'Actual hours significantly exceed estimate. Consider updating the estimate.')

        return cleaned_data


class SearchForm(forms.Form):
    """Global search form across all models."""
    
    SEARCH_TYPE_CHOICES = [
        ('all', 'All Items'),
        ('projects', 'Projects'),
        ('applications', 'Applications'),
        ('artifacts', 'Artifacts'),
        ('tasks', 'Tasks'),
        ('decisions', 'Decisions'),
        ('integrations', 'Integrations'),
    ]

    query = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search projects, apps, tasks...',
            'autocomplete': 'off'
        })
    )
    
    search_type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        initial='all',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        empty_label="All Projects",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='col-md-6'),
                Column('search_type', css_class='col-md-3'),
                Column('project', css_class='col-md-3'),
            ),
            FormActions(
                Submit('submit', 'Search', css_class='btn btn-primary'),
                HTML('<a href="{% url "tracker:search" %}" class="btn btn-outline-secondary ms-2">Clear</a>'),
            )
        )


class BulkTaskForm(forms.Form):
    """Form for bulk operations on tasks."""
    
    BULK_ACTIONS = [
        ('', 'Select Action'),
        ('complete', 'Mark as Completed'),
        ('in_progress', 'Mark as In Progress'),
        ('pending', 'Mark as Pending'),
        ('change_assignee', 'Change Assignee'),
        ('update_due_date', 'Update Due Date'),
    ]

    action = forms.ChoiceField(
        choices=BULK_ACTIONS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Optional fields for specific actions
    new_assignee = forms.ChoiceField(
        choices=Task.ASSIGNEE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    new_due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    selected_tasks = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('action', css_class='col-md-4'),
                Column('new_assignee', css_class='col-md-4'),
                Column('new_due_date', css_class='col-md-4'),
            ),
            'selected_tasks',
            FormActions(
                Submit('submit', 'Apply Action', css_class='btn btn-warning'),
            )
        )

    def clean(self):
        """Validate bulk action requirements."""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        
        if action == 'change_assignee':
            if not cleaned_data.get('new_assignee'):
                raise ValidationError({
                    'new_assignee': 'New assignee is required for this action.'
                })
        
        elif action == 'update_due_date':
            if not cleaned_data.get('new_due_date'):
                raise ValidationError({
                    'new_due_date': 'New due date is required for this action.'
                })
        
        # Validate selected tasks
        selected_tasks = cleaned_data.get('selected_tasks', '')
        if not selected_tasks:
            raise ValidationError('No tasks selected for bulk operation.')
        
        try:
            task_ids = [int(id) for id in selected_tasks.split(',') if id.strip()]
            if not task_ids:
                raise ValidationError('No valid task IDs found.')
            cleaned_data['task_ids'] = task_ids
        except ValueError:
            raise ValidationError('Invalid task IDs format.')
        
        return cleaned_data


class DecisionForm(forms.ModelForm):
    """Form for creating and updating decisions."""

    class Meta:
        model = Decision
        fields = [
            'project', 'title', 'description', 'status', 
            'impact', 'decision_maker', 'decided_date'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'impact': forms.Select(attrs={'class': 'form-select'}),
            'decision_maker': forms.TextInput(attrs={'class': 'form-control'}),
            'decided_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Decision Information',
                Row(
                    Column('project', css_class='col-md-6'),
                    Column('title', css_class='col-md-6'),
                ),
                'description',
                Row(
                    Column('status', css_class='col-md-4'),
                    Column('impact', css_class='col-md-4'),
                    Column('decided_date', css_class='col-md-4'),
                ),
                'decision_maker',
            ),
            FormActions(
                Submit('submit', 'Save Decision', css_class='btn btn-primary'),
                HTML('<a href="{% url "tracker:decision_list" %}" class="btn btn-secondary ms-2">Cancel</a>'),
            )
        )


class IntegrationForm(forms.ModelForm):
    """Form for creating and updating integrations."""

    class Meta:
        model = Integration
        fields = [
            'from_app', 'to_app', 'integration_type', 'status', 
            'complexity', 'description', 'estimated_weeks'
        ]
        widgets = {
            'from_app': forms.Select(attrs={'class': 'form-select'}),
            'to_app': forms.Select(attrs={'class': 'form-select'}),
            'integration_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'complexity': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'estimated_weeks': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1, 
                'step': 1
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Integration Information',
                Row(
                    Column('from_app', css_class='col-md-6'),
                    Column('to_app', css_class='col-md-6'),
                ),
                'description',
                Row(
                    Column('integration_type', css_class='col-md-4'),
                    Column('status', css_class='col-md-4'),
                    Column('complexity', css_class='col-md-4'),
                ),
                'estimated_weeks',
            ),
            FormActions(
                Submit('submit', 'Save Integration', css_class='btn btn-primary'),
                HTML('<a href="{% url "tracker:integration_list" %}" class="btn btn-secondary ms-2">Cancel</a>'),
            )
        )

    def clean(self):
        """Validate integration form."""
        cleaned_data = super().clean()
        from_app = cleaned_data.get('from_app')
        to_app = cleaned_data.get('to_app')

        if from_app and to_app and from_app == to_app:
            raise ValidationError({
                'to_app': 'Source and target applications cannot be the same.'
            })

        # Check if applications are from the same project
        if from_app and to_app and from_app.project != to_app.project:
            raise ValidationError("Can only integrate applications within the same project.")

        return cleaned_data
