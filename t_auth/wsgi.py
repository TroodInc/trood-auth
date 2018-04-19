import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 't_auth.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')

from configurations.wsgi import get_wsgi_application

application = get_wsgi_application()
