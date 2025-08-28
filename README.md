# FamilyHub Development Tracker

A comprehensive Django web application serving as the central command center for tracking FamilyHub project development - a unified platform combining multiple Django applications including Timesheet Tracker, Daycare Invoice Tracker, AutoCraftCV, and more.

![Django](https://img.shields.io/badge/Django-5.2.5-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Project Overview

FamilyHub Development Tracker provides a centralized platform for managing the development lifecycle of multiple Django applications. It tracks projects, applications, artifacts, tasks, decisions, and integration plans with a modern, responsive interface.

### Key Features

- **Project Management**: Track multiple projects with status monitoring and timeline visualization
- **Application Tracking**: Monitor individual Django apps with version control and repository integration
- **Artifact Management**: Store and version requirements documents, code files, and architecture plans
- **Task Assignment**: Assign development tasks to different team members (Claude, GitHub Copilot, Human developers)
- **Decision Logging**: Document architectural and technical decisions with rationale
- **Integration Planning**: Track app-to-app integrations with dependency mapping
- **File Uploads**: Support for multiple file formats with size and type validation
- **Data Export**: Export project data to JSON, CSV, and Excel formats
- **Responsive Design**: Bootstrap 5 interface optimized for all devices

## 🛠️ Technology Stack

- **Backend**: Django 5.2.5
- **Frontend**: Bootstrap 5, JavaScript, Chart.js (ready)
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Forms**: django-crispy-forms with Bootstrap 5 styling
- **Authentication**: Django's built-in User model with custom extensions
- **File Storage**: Local filesystem (development), cloud storage ready

## 📋 Requirements

- Python 3.10 or higher
- Django 5.2.5+
- SQLite (development) or PostgreSQL (production)
- Modern web browser with JavaScript enabled

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/dev_tracker.git
cd dev_tracker
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@familyhub.local
```

### 5. Database Setup

```bash
# Create database tables
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Load sample data (optional)
python manage.py populate_sample_data
```

### 6. Create Required Directories

```bash
mkdir logs media exports static
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 📁 Project Structure

```
dev_tracker/
├── dev_tracker/                # Project configuration
│   ├── __init__.py
│   ├── settings.py             # Django settings with environment config
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py                 # WSGI configuration
├── tracker/                    # Main application
│   ├── migrations/             # Database migrations
│   ├── management/             # Custom management commands
│   │   └── commands/
│   │       ├── populate_sample_data.py    # Sample data generation
│   │       └── export_project_data.py     # Data export utility
│   ├── templates/              # HTML templates
│   │   └── tracker/            # App-specific templates
│   ├── static/                 # Static files (CSS, JS, images)
│   ├── models.py               # Database models
│   ├── views.py                # View functions and classes
│   ├── forms.py                # Django forms
│   ├── urls.py                 # App URL patterns
│   ├── api_urls.py             # API endpoint URLs
│   ├── api_views.py            # API view functions
│   └── admin.py                # Admin configuration
├── accounts/                   # User management
├── templates/                  # Global templates
│   ├── base.html               # Base template with Bootstrap 5
│   └── registration/           # Authentication templates
├── static/                     # Global static files
├── media/                      # User-uploaded files
├── logs/                       # Application logs
├── exports/                    # Data export files
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
└── README.md                   # This file
```

## 💾 Database Models

### Core Models

1. **Project**: Main container for development projects
   - Fields: name, description, status, owner, start_date, target_date, features
   - Relationships: One-to-many with Applications, Tasks, Decisions

2. **Application**: Individual Django applications
   - Fields: name, description, status, version, repository_url, tech_stack, features
   - Relationships: Belongs to Project, has many Tasks and Artifacts

3. **Artifact**: Documents, code files, and deliverables
   - Fields: title, description, artifact_type, version, file_path, file_size
   - Relationships: Belongs to Application
   - Supported Types: Requirements, Code, Documentation, Architecture, Testing

4. **Task**: Development tasks and assignments
   - Fields: title, description, status, priority, due_date, assigned_to
   - Relationships: Belongs to Project and/or Application
   - Statuses: Not Started, In Progress, Review, Completed, Blocked

5. **Decision**: Technical and architectural decisions
   - Fields: title, description, decision_type, status, impact, rationale
   - Relationships: Belongs to Project
   - Types: Architecture, Technology, Process, Design

6. **Integration**: App-to-app integration tracking
   - Fields: from_application, to_application, integration_type, status, complexity
   - Relationships: Many-to-many between Applications

## 🎨 User Interface

### Dashboard Features
- Project overview with completion statistics
- Recent artifacts and task updates  
- Overdue tasks highlighting
- Quick action buttons for common operations
- Visual progress indicators

### Key Pages
- **Dashboard**: Central overview with statistics and recent activity
- **Projects**: List and detail views with CRUD operations
- **Applications**: Application management with version tracking
- **Tasks**: Kanban-style task board with assignment tracking
- **Artifacts**: File upload and version management
- **Decisions**: Decision logging with impact assessment
- **Integrations**: Dependency mapping and timeline visualization

## 🔧 Management Commands

### Populate Sample Data
Generate realistic test data for development:

```bash
python manage.py populate_sample_data
```

This creates:
- FamilyHub main project
- 7 sample applications (Timesheet, Daycare Tracker, AutoCraftCV, etc.)
- Development tasks assigned to different team members
- Sample artifacts and documentation
- Architecture decisions and integration plans

### Export Project Data
Export data for backup or reporting:

```bash
# Export all data to JSON
python manage.py export_project_data --format json

# Export specific project to CSV
python manage.py export_project_data --format csv --project 1

# Export to Excel with custom path
python manage.py export_project_data --format excel --output /path/to/export.xlsx

# Export specific data types
python manage.py export_project_data --include projects applications tasks
```

## 🔒 Security Features

- CSRF protection on all forms
- User authentication required for all views
- File upload validation (type and size)
- SQL injection prevention through Django ORM
- XSS prevention in templates
- Secure session management
- Production-ready security headers

## 🔌 API Endpoints

The application includes RESTful API endpoints for AJAX functionality:

```
GET  /api/stats/             # Dashboard statistics
GET  /api/search/            # Global search
GET  /api/tasks/             # Task data for charts
GET  /api/projects/          # Project summaries
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test tracker

# Run with coverage
coverage run manage.py test
coverage report
```

### Test Data
Use the management command to generate consistent test data:

```bash
python manage.py populate_sample_data
```

## 📊 Sample Data

The application includes comprehensive sample data representing the FamilyHub project:

### Applications Included
1. **Timesheet Tracker** - Employee time tracking (Ready for Development)
2. **Daycare Invoice Tracker** - Invoice management (Production Ready)
3. **AutoCraftCV** - Automated CV generation (Production Ready)
4. **Employment History** - Job history tracking (Planning Phase)
5. **Upcoming Payments** - Payment scheduling (Planning Phase)
6. **Credit Card Management** - Financial tracking (Planning Phase)
7. **Household Budget** - Budget management (Planning Phase)

### Sample Tasks
- Requirements gathering and analysis
- Database design and modeling
- UI/UX development with Bootstrap 5
- API development and testing
- Integration planning and implementation
- Documentation and deployment

## 🚀 Deployment

### Production Checklist

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

2. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   python manage.py createcachetable  # For database caching
   ```

3. **Web Server Configuration**
   - Configure nginx or Apache for static file serving
   - Set up SSL certificates
   - Configure database connection pooling

4. **Security Settings**
   - All production security settings are automatically enabled when `DEBUG=False`
   - SSL redirect, HSTS headers, secure cookies

## 📈 Performance Optimization

- Database query optimization with select_related() and prefetch_related()
- Template caching for repeated elements
- Static file compression and minification ready
- Database indexing on frequently queried fields
- Pagination for large datasets

## 🔍 Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --clear
   ```

2. **Database Migration Issues**
   ```bash
   python manage.py makemigrations
   python manage.py migrate --fake-initial
   ```

3. **File Upload Problems**
   - Check `MEDIA_ROOT` permissions
   - Verify file size limits in settings
   - Ensure upload directory exists

4. **Email Configuration**
   - Test with console backend first
   - Verify SMTP settings
   - Check firewall restrictions

## 📝 Development Guidelines

### Code Standards
- Follow PEP 8 styling conventions
- Use meaningful variable and function names
- Include docstrings for complex functions
- Handle errors gracefully with try/except blocks
- Use Django's messages framework for user feedback

### Commit Message Format
```
feat: add new feature
fix: resolve bug issue
docs: update documentation
style: formatting changes
refactor: code refactoring
test: add or update tests
chore: maintenance tasks
```

### Testing Requirements
- Write unit tests for all models
- Test view functionality and permissions
- Validate form inputs and error handling
- Test file upload and download features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django framework for robust web development
- Bootstrap 5 for responsive UI components
- Chart.js for data visualization capabilities
- django-crispy-forms for enhanced form styling
- GitHub Copilot for development assistance

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review Django documentation for framework-specific issues

---

**Project Status**: Ready for Development and Production Deployment  
**Last Updated**: December 2024  
**Version**: 1.0.0
