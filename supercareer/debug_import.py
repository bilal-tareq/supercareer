
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supercareer.settings')
django.setup()

try:
    from accounts.views import RegisterView
    print("Import successful")
except Exception as e:
    import traceback
    traceback.print_exc()
