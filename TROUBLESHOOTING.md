# Vercel Deployment Troubleshooting

## Common Error: 500 Internal Server Error

If you're seeing a `500: INTERNAL_SERVER_ERROR` with `FUNCTION_INVOCATION_FAILED`, follow these steps:

### 1. Check Environment Variables

Make sure these are set in your Vercel dashboard:

```
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://username:password@host:port/database_name
ALLOWED_HOSTS=your-app-name.vercel.app,localhost,127.0.0.1
```

### 2. Verify Database Connection

Your `DATABASE_URL` should look like:
```
postgresql://postgres:password@metro.proxy.rlwy.net:51654/railway
```

### 3. Check Vercel Logs

1. Go to your Vercel dashboard
2. Click on your project
3. Go to "Functions" tab
4. Check the logs for specific error messages

### 4. Common Issues and Solutions

#### Issue: ModuleNotFoundError
**Solution**: Make sure all dependencies are in `requirements.txt`

#### Issue: Database Connection Failed
**Solution**: 
- Verify `DATABASE_URL` is correct
- Check if database allows external connections
- Ensure SSL is enabled for Railway

#### Issue: Static Files Not Found
**Solution**: 
- Static files are handled by WhiteNoise
- No additional configuration needed

#### Issue: Import Error
**Solution**: 
- Check if all imports are correct
- Verify file paths

### 5. Debug Mode

Temporarily set `DEBUG=True` to see detailed error messages:

```
DEBUG=True
```

**Remember to set it back to `False` after fixing the issue!**

### 6. Test Locally

Run this command to test your configuration:

```bash
python test_vercel.py
```

### 7. Manual Deployment Steps

1. **Push your changes**:
   ```bash
   git add .
   git commit -m "Fix Vercel deployment"
   git push
   ```

2. **Redeploy on Vercel**:
   - Go to Vercel dashboard
   - Click "Redeploy" on your project

3. **Check deployment logs**:
   - Monitor the build process
   - Look for any error messages

### 8. Alternative: Use Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### 9. Database Migration Issues

If migrations fail:

1. **Check database connection**
2. **Run migrations manually**:
   ```bash
   vercel --prod
   python manage.py migrate
   ```

### 10. Still Having Issues?

1. **Check Vercel documentation**: https://vercel.com/docs
2. **Review Django deployment checklist**: https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
3. **Contact Vercel support** if the issue persists

## Quick Fix Checklist

- [ ] Environment variables set correctly
- [ ] Database URL is valid and accessible
- [ ] All dependencies in requirements.txt
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS includes your Vercel domain
- [ ] Static files collected (automatic)
- [ ] Migrations run successfully
- [ ] No syntax errors in code
- [ ] Database allows external connections
- [ ] SSL enabled for database connection
