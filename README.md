# Mamas Mart

This is the Mamas Mart project, a Django-based web application for managing products, accounts, and dashboard analytics.

## Features

- User authentication and management
- Product listing and management
- Dashboard with sales and revenue charts
- Responsive UI with Bootstrap and ApexCharts

## Setup

1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```
   python manage.py migrate
   ```
5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```
   python manage.py runserver
   ```

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
