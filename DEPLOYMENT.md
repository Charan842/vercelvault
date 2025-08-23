# Vercel Deployment Guide

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub/GitLab Account**: Your code should be in a Git repository
3. **PostgreSQL Database**: You can use Railway, Supabase, or any PostgreSQL provider

## Environment Variables Setup

In your Vercel project settings, add these environment variables:

### Required Variables:
```
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://username:password@host:port/database_name
ALLOWED_HOSTS=your-app-name.vercel.app,localhost,127.0.0.1
```

### Optional Variables:
```
# For additional security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

## Database Setup

1. **Create a PostgreSQL database** (Railway, Supabase, etc.)
2. **Get the connection string** and add it as `DATABASE_URL`
3. **Run migrations** after deployment

## Deployment Steps

1. **Connect your repository** to Vercel
2. **Set environment variables** in Vercel dashboard
3. **Deploy** - Vercel will automatically detect Django and build
4. **Run migrations** using Vercel CLI or dashboard

## Post-Deployment

1. **Create a superuser**:
   ```bash
   vercel --prod
   python manage.py createsuperuser
   ```

2. **Collect static files** (automatic during build)

3. **Test your application**

## File Storage

For production, consider using:
- **AWS S3** for media files
- **Cloudinary** for image/video storage
- **Vercel Blob Storage** for file storage

## Troubleshooting

### Common Issues:

1. **Static files not loading**: Check `STATICFILES_STORAGE` setting
2. **Database connection**: Verify `DATABASE_URL` format
3. **Media files**: Use external storage for user uploads
4. **CORS issues**: Configure `ALLOWED_HOSTS` properly

### Debug Mode:
Set `DEBUG=True` temporarily to see error details, but remember to set it back to `False` for production.

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY`
- [ ] Proper `ALLOWED_HOSTS`
- [ ] HTTPS enabled
- [ ] Database credentials secured
- [ ] Static files served properly
- [ ] Media files on external storage
