export  DJANGO_SUPERUSER_PASSWORD=admin
python manage.py flush --noinput
python manage.py createsuperuser --noinput --username admin --email skip@skip.com
python manage.py loaddata rse_challenges_app/fixtures/challenges.json