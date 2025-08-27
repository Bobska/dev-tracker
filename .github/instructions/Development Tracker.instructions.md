---
applyTo: '**'
---
# FamilyHub Development Tracker: GitHub Copilot Instructions

## Project Overview
Create a Django web application to serve as the central command center for tracking FamilyHub project development - a unified platform combining multiple Django apps (Timesheet, Daycare Tracker, AutoCraftCV, etc.).

## Django Development Standards

### Django Framework Requirements:
- **Django Version**: 5.2.5+
- **Python Version**: 3.10+  
- **Database**: SQLite for development
- **UI Framework**: Bootstrap 5 with responsive design
- **Forms**: django-crispy-forms for consistent styling
- **Authentication**: Django's built-in User model

### Code Quality Standards:
- Follow PEP 8 styling conventions
- Use meaningful variable and function names
- Include docstrings for complex functions
- Handle errors gracefully with try/except blocks
- Use Django's messages framework for user feedback
- Implement proper pagination for list views

## Model Design Requirements

### Core Models Structure:
1. **Project**: Main container (FamilyHub project)
2. **Application**: Individual apps (Timesheet, Daycare, AutoCraftCV)
3. **Artifact**: Requirements, code, documentation with versioning
4. **Task**: Development tasks with assignment tracking
5. **Decision**: Architecture and technical decision logging
6. **Integration**: App-to-app integration planning

### Model Implementation Standards:
- Include `__str__` methods that return meaningful representations
- Add `created_at` and `updated_at` timestamps on all models
- Use proper ForeignKey relationships with `related_name` attributes
- Implement JSONField for flexible data storage (features, metadata)
- Add model validation with custom clean methods
- Use choices for status fields with clear options

## Database Relationships:
```
Project (1) → (Many) Application
Application (1) → (Many) Artifact
Application (1) → (Many) Task
Project (1) → (Many) Decision
Application (Many) → (Many) Integration
```

## View Implementation Requirements

### View Types:
- **Dashboard Views**: Statistical summaries and recent activity
- **CRUD Views**: Create, Read, Update, Delete for all models
- **List Views**: Filterable and searchable with pagination
- **Detail Views**: Comprehensive information with related objects

### View Standards:
- Use class-based views for CRUD operations
- Function-based views for dashboard and complex logic
- Implement proper URL patterns with meaningful names
- Add search functionality across relevant models
- Create AJAX endpoints for dynamic updates
- Include proper error handling and user feedback

## Template & UI Requirements

### Bootstrap 5 Implementation:
- Use template inheritance with comprehensive base.html
- Implement consistent navigation with project/app context
- Create responsive design for mobile compatibility
- Use Bootstrap components (cards, badges, progress bars)
- Include status color-coding throughout interface

### UI Elements:
- **Status Badges**: Color-coded for different states
- **Progress Bars**: Visual completion tracking
- **Icons**: Bootstrap Icons for visual clarity
- **Forms**: Crispy forms with validation feedback
- **Tables**: Responsive with sorting and filtering
- **Dashboard Cards**: Key metrics and statistics

## Form Implementation Standards

### Form Requirements:
- Use django-crispy-forms for consistent styling
- Implement proper form validation with custom clean methods
- Add JavaScript for dynamic interactions (add/remove features)
- Handle file uploads with size and type validation
- Use Django messages for form submission feedback
- Include CSRF protection on all forms

### Form Types:
- **Model Forms**: For all CRUD operations
- **Search Forms**: Global search across models
- **Filter Forms**: Advanced filtering options
- **Upload Forms**: File handling for artifacts

## Admin Interface Requirements

### Admin Configuration:
- Comprehensive admin interfaces for all models
- List displays with relevant fields and relationships
- List filters for status, dates, and categories
- Search fields across text content
- Inline editing for related models
- Custom actions for bulk operations
- Color-coded status displays

## File Handling Requirements

### Artifact File Management:
- Support multiple file types (PDF, DOC, TXT, etc.)
- File size validation (max 10MB)
- Organized file storage structure
- Version control for uploaded files
- File download functionality
- Preview capabilities where possible

## Sample Data Requirements

### Create Realistic Test Data:
- **FamilyHub Main Project** with proper dates and status
- **Three Applications**: Timesheet (ready), Daycare Tracker (production), AutoCraftCV (production)
- **Sample Artifacts**: Requirements docs, code files, architecture plans
- **Development Tasks**: Assigned to Claude, GitHub Copilot, human developers
- **Integration Plans**: Between applications with dependencies
- **Decision Records**: Technical and architectural choices

## Specific Feature Requirements

### Dashboard Features:
- Project overview with completion statistics
- Recent artifacts and task updates
- Overdue tasks highlighting
- Progress charts (Chart.js integration ready)
- Quick action buttons for common tasks

### Task Management:
- Kanban-style task board by status
- Assignment to different team members (Claude, Copilot, Human)
- Priority levels with visual indicators
- Due date tracking with overdue alerts
- Time estimation vs actual tracking

### Artifact Versioning:
- Version number tracking (1.0, 1.1, etc.)
- Content comparison between versions
- File replacement with version history
- Version-specific download links

### Integration Tracking:
- Visual dependency mapping
- Integration status monitoring
- Timeline visualization for integration roadmap
- Complexity assessment and time estimates

## Testing Requirements

### Test Each Implementation:
- Model creation and relationships
- Form validation and submission
- View rendering and context data
- File upload and download functionality
- AJAX endpoints and dynamic updates
- Admin interface operations
- Search and filtering functionality

### Browser Testing:
- Responsive design on mobile/tablet/desktop
- Form interactions and validation display
- File upload progress and success states
- Status updates and visual feedback

## Performance Considerations

### Optimization Requirements:
- Use select_related() and prefetch_related() for database queries
- Implement proper pagination for large datasets
- Optimize file uploads with progress indicators
- Cache frequently accessed data where appropriate
- Use Django's built-in optimization features

## Security Standards

### Django Security:
- CSRF protection on all forms
- Proper file upload validation
- User authentication for all views
- SQL injection prevention through ORM
- XSS prevention in templates
- Secure file handling and storage

---

**Project Goal**: Create a comprehensive, user-friendly development tracking system that serves as the central command center for managing the FamilyHub project development, integration planning, and progress monitoring.