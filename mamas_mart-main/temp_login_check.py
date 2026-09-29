import os 
os.environ['DJANGO_SETTINGS_MODULE']='mamas_mart.settings' 
import django 
django.setup() 
from django.test import Client 
c = Client(HTTP_HOST='127.0.0.1:8000') 
r = c.get('/login/?next=/') 
print(r.status_code) 
print(getattr(r, 'template_name', None)) 
