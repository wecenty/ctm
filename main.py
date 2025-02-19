
import os
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctm.settings')
django.setup()

if __name__ == '__main__':
    execute_from_command_line(['manage.py', 'migrate'])
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:3000'])
