# MediaVault - Django Storage Application

A comprehensive Django web application for photo and video storage with advanced features including albums, sharing, and storage analytics.

## Features

- **Photo & Video Upload**: Support for multiple file uploads with size validation
- **Album Management**: Create and organize media into albums
- **Sharing System**: Share photos, videos, and albums with unique URLs
- **Storage Analytics**: Track storage usage with charts and history
- **User Management**: Registration, login, and profile management
- **Storage Limits**: Free tier (5GB) and premium tier (100GB) support
- **Responsive Design**: Modern UI that works on all devices

## Technology Stack

- **Backend**: Django 5.2.3
- **Database**: PostgreSQL (Railway)
- **Deployment**: Vercel
- **File Storage**: Local file system
- **Authentication**: Django's built-in auth system

## Local Development

### Prerequisites

- Python 3.9+
- PostgreSQL database
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Charan842/MediaVault.git
cd MediaVault
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file with your database credentials
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_django_secret_key
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Deployment

This project is configured for deployment on Vercel with the following setup:

- **Build Command**: `./build_files.sh`
- **Output Directory**: `staticfiles`
- **Python Runtime**: 3.9

### Environment Variables for Production

Set these in your Vercel dashboard:

- `DATABASE_URL`: Your PostgreSQL connection string
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` for production

## Project Structure

```
storageproduct/
├── storageapp/          # Main Django app
│   ├── models.py       # Database models
│   ├── views.py        # View functions
│   ├── forms.py        # Django forms
│   ├── admin.py        # Admin interface
│   └── templates/      # HTML templates
├── storageproduct/      # Project settings
│   ├── settings.py     # Django settings
│   ├── urls.py         # URL configuration
│   └── wsgi.py         # WSGI application
├── static/             # Static files (CSS, JS, images)
├── media/              # User uploaded files
├── requirements.txt    # Python dependencies
├── vercel.json        # Vercel configuration
└── build_files.sh     # Build script
```

## Database Models

- **UserProfile**: User storage limits and preferences
- **Photo/Video**: Media files with metadata
- **Album**: Collections of photos and videos
- **SharedPhoto/SharedVideo/SharedAlbum**: Sharing functionality
- **Notification**: User notifications
- **StorageUpgradeRequest**: Premium storage requests
- **StorageHistory**: Storage usage tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on GitHub or contact the development team. 