# Storage Product - Django Media Storage Application

A comprehensive Django web application for storing, organizing, and sharing photos and videos with user management, storage analytics, and album features.

## Features

- **User Authentication**: Sign up, login, and user profile management
- **Media Storage**: Upload, organize, and manage photos and videos
- **Album Management**: Create albums and organize media files
- **Sharing**: Share individual files or albums with expiration dates
- **Storage Analytics**: Track storage usage and view analytics
- **Storage Limits**: Configurable storage limits with upgrade options
- **Responsive Design**: Modern, mobile-friendly interface
- **Search**: Search through your media files
- **Notifications**: User notification system

## Tech Stack

- **Backend**: Django 5.1.7
- **Database**: PostgreSQL
- **Static Files**: WhiteNoise
- **Image Processing**: Pillow
- **Deployment**: Vercel

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Vercel account (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd storageproduct
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env with your database credentials
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Visit** `http://localhost:8000`

## Vercel Deployment

### 1. Prepare Your Repository

Ensure your code is pushed to a Git repository (GitHub, GitLab, etc.).

### 2. Set Up Database

Create a PostgreSQL database using:
- **Railway**: [railway.app](https://railway.app)
- **Supabase**: [supabase.com](https://supabase.com)
- **Neon**: [neon.tech](https://neon.tech)

### 3. Deploy to Vercel

1. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your Git repository

2. **Configure Environment Variables**
   In Vercel project settings, add:
   ```
   SECRET_KEY=your-secure-secret-key
   DEBUG=False
   DATABASE_URL=postgresql://username:password@host:port/database
   ALLOWED_HOSTS=your-app-name.vercel.app,localhost,127.0.0.1
   ```

3. **Deploy**
   - Vercel will automatically detect Django and build
   - The build process will install dependencies and collect static files

### 4. Post-Deployment

1. **Run migrations** (if not automatic)
2. **Create superuser** using Vercel CLI or dashboard
3. **Test your application**

## Environment Variables

### Required
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Optional
- `SECURE_SSL_REDIRECT`: Set to `True` for HTTPS redirect
- `SECURE_HSTS_SECONDS`: HSTS security header

## File Structure

```
storageproduct/
├── storageapp/          # Main Django app
│   ├── models.py       # Database models
│   ├── views.py        # View functions
│   ├── urls.py         # URL patterns
│   ├── forms.py        # Forms
│   └── templates/      # HTML templates
├── storageproduct/      # Django project settings
│   ├── settings.py     # Django settings
│   ├── urls.py         # Main URL configuration
│   └── wsgi.py         # WSGI configuration
├── static/             # Static files (CSS, JS, images)
├── media/              # User uploaded files
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel configuration
└── build.sh           # Build script
```

## Models

- **User**: Extended user model with profiles
- **Photo/Video**: Media file models with metadata
- **Album**: Collection of media files
- **SharedPhoto/SharedVideo/SharedAlbum**: Sharing functionality
- **UserProfile**: User storage limits and preferences
- **Notification**: User notification system
- **StorageHistory**: Storage usage tracking

## API Endpoints

- `/`: Home page
- `/dashboard/`: User dashboard
- `/photos/`: Photo management
- `/videos/`: Video management
- `/albums/`: Album management
- `/upload/`: File upload
- `/search/`: Media search
- `/profile/`: User profile
- `/analytics/`: Storage analytics

## Security Features

- CSRF protection
- XSS protection
- HSTS headers (production)
- Secure content type sniffing
- Frame options protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For deployment issues, check the [DEPLOYMENT.md](DEPLOYMENT.md) file for detailed troubleshooting steps. 