# Mamas Mart

Mamas Mart is a Django application for managing products, inventory, sales, accounts, and dashboard analytics.

## Features

- User authentication and management
- Product listing and management
- Dashboard with sales and revenue charts
- Responsive UI with Bootstrap and ApexCharts

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and set the local database values.
4. Apply migrations and collect static files:
   ```
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
6. Start the development server:
   ```
   python manage.py runserver
   ```

## Production deployment

This is a server-rendered Django application. Deploy the Django backend to a Python host such as Render, Railway, or Fly.io. Netlify cannot run this Django application directly as a normal static site; it can host a separate frontend or proxy to the deployed backend.

Use these backend commands:

```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
gunicorn mamas_mart.wsgi:application
```

Set these environment variables in the hosting provider:

```
SECRET_KEY=<a-new-long-random-secret>
DEBUG=False
ALLOWED_HOSTS=your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
DB_NAME=<managed-postgres-database>
DB_USER=<managed-postgres-user>
DB_PASSWORD=<managed-postgres-password>
DB_HOST=<managed-postgres-host>
DB_PORT=5432
USE_HTTPS=True
```

Uploaded files in `media/` require persistent object storage such as Amazon S3 or Cloudinary. Do not commit `.env`, database credentials, generated static files, or uploaded media.

## Usage

- Access the admin panel at `/admin/`
- Use the dashboard to view sales and revenue analytics
- Manage products and user accounts through the web interface

## Technologies Used

- Python 3.x
- Django
- Bootstrap 5
- ApexCharts
- SQLite (default database)

## License

This project is licensed under the MIT License.
