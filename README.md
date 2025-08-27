# FamilyHub Development Tracker

A comprehensive Django web application for tracking software development progress, designed to serve as the central command center for managing the FamilyHub project and its multiple applications.

## 🚀 Features

### Core Functionality
- **Project Management**: Track multiple projects with status, timelines, and team management
- **Application Tracking**: Manage individual applications within projects (Timesheet, Daycare Tracker, etc.)
- **Task Management**: Create, assign, and track development tasks with priority levels
- **Artifact Management**: Store and version project artifacts (requirements, code, documentation)
- **Decision Logging**: Record architectural and technical decisions with rationale
- **Integration Planning**: Track app-to-app integration requirements and progress

### User Management
- **Custom User Model**: Extended user profiles with roles and GitHub integration
- **Authentication**: Complete login/logout/registration system
- **Role-based Access**: Different user roles (Developer, Manager, Tester, Designer, Analyst)

### UI/UX
- **Bootstrap 5**: Modern, responsive design with custom styling
- **Dashboard**: Comprehensive overview with statistics and quick actions
- **Interactive Forms**: User-friendly forms with validation and dynamic features
- **File Upload**: Support for document and artifact uploads

## 🛠 Technology Stack

- **Backend**: Django 5.2.5, Python 3.10+
- **Database**: SQLite (development), easily configurable for PostgreSQL/MySQL
- **Frontend**: Bootstrap 5, Custom CSS/JavaScript
- **Forms**: django-crispy-forms with Bootstrap 5 styling
- **File Handling**: Pillow for image processing
- **Configuration**: python-decouple for environment variables

## 📋 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Virtual environment (recommended)

### Installation Steps

1. **Clone or extract the project:**
   ```bash
   cd "FamilyHub/Individual Apps/dev_tracker"
   ```

2. **Activate virtual environment:**
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   ```bash
   # Copy .env.example to .env and configure
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```

5. **Database Setup:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application:**
   - Main Application: http://127.0.0.1:8000/
   - Admin Interface: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
dev_tracker/
├── accounts/                 # User management app
│   ├── models.py            # Custom User model
│   ├── forms.py             # Registration/profile forms
│   ├── views.py             # Authentication views
│   └── urls.py              # Account URLs
├── tracker/                 # Main tracking app
│   ├── models.py            # Core models (Project, Task, etc.)
│   ├── views.py             # CRUD views
│   ├── admin.py             # Admin configuration
│   └── urls.py              # Tracker URLs
├── templates/               # HTML templates
│   ├── base.html            # Base template with Bootstrap
│   ├── accounts/            # Authentication templates
│   └── tracker/             # App-specific templates
├── static/                  # Static files
│   ├── css/custom.css       # Custom styling
│   ├── js/custom.js         # Custom JavaScript
│   └── images/              # Images and icons
├── media/                   # User uploaded files
├── dev_tracker/             # Django project settings
│   ├── settings.py          # Main settings file
│   ├── urls.py              # URL configuration
│   └── wsgi.py              # WSGI configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── manage.py               # Django management script
```

## 🎯 Usage Guide

### Getting Started

1. **Login/Register**: Create an account or use the admin user
2. **Create Project**: Start by creating your first project (e.g., "FamilyHub")
3. **Add Applications**: Create applications within your project
4. **Create Tasks**: Break down work into manageable tasks
5. **Upload Artifacts**: Store requirements, documentation, and code files

### Dashboard Features

- **Statistics Cards**: Overview of projects, applications, and tasks
- **Quick Actions**: Rapidly create new items
- **Recent Activity**: Stay updated with latest changes
- **Progress Tracking**: Visual progress indicators

### Admin Interface

Access the Django admin at `/admin/` for:
- User management
- Bulk operations
- Advanced filtering and search
- Direct database management

## 🔧 Configuration

### Environment Variables (.env)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Database Configuration

Default: SQLite for development
Production: Configure PostgreSQL/MySQL in settings.py

### Static Files

- Development: Served automatically by Django
- Production: Run `python manage.py collectstatic`

## 📊 Data Models

### Core Models

- **Project**: Main container for applications and tasks
- **Application**: Individual apps within a project
- **Task**: Development tasks with assignment and tracking
- **Artifact**: Files and documents with versioning
- **Decision**: Technical decision logging
- **Integration**: App-to-app integration planning

### User Model

Extended Django User with additional fields:
- Profile picture
- Bio and GitHub username
- Role assignment
- Creation/update timestamps

## 🎨 Customization

### Styling
- Modify `static/css/custom.css` for styling changes
- Update `static/js/custom.js` for JavaScript functionality
- Customize Bootstrap variables if needed

### Templates
- Base template: `templates/base.html`
- App templates: `templates/tracker/` and `templates/accounts/`
- Crispy forms for consistent styling

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG=False` in production
2. Configure proper `SECRET_KEY`
3. Set up production database (PostgreSQL recommended)
4. Configure static file serving
5. Set up media file handling
6. Configure email backend for password reset
7. Set proper `ALLOWED_HOSTS`

## 📝 Future Enhancements

- **API Integration**: REST API for mobile/external access
- **Real-time Updates**: WebSocket integration for live updates
- **Advanced Analytics**: Charts and reporting dashboard
- **GitHub Integration**: Direct repository integration
- **Time Tracking**: Built-in time tracking for tasks
- **Notification System**: Email/in-app notifications
- **Export Features**: PDF/Excel export capabilities

## 🤝 Contributing

This project is part of the FamilyHub initiative. Follow the development standards outlined in the project documentation.

## 📄 License

Part of the FamilyHub project suite.

---

**Built with ❤️ using Django 5.2.5 & Bootstrap 5**
