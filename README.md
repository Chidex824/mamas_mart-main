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

This project is compatible with Vercel for a Django backend. Vercel detects the Django app from `manage.py` and serves it through the WSGI entrypoint in `mamas_mart/wsgi.py`.

Use these backend commands:

```
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Set these environment variables in your Vercel project settings:

```
SECRET_KEY=<a-new-long-random-secret>
DEBUG=False
ALLOWED_HOSTS=your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<database>
DB_NAME=<database-name>
DB_USER=<database-user>
DB_PASSWORD=<database-password>
DB_HOST=<database-host>
DB_PORT=5432
USE_HTTPS=True
```

This app is configured to use PostgreSQL by default. `pgAdmin 4` is only the database management UI; the actual database still needs a running PostgreSQL server or managed Postgres service.

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
- PostgreSQL (production-ready database)

## License

This project is licensed under the MIT License.
