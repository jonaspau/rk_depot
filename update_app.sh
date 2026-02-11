cd /home/mail_/projects/rk_depot

echo "Henter nyeste kode fra GitHub..."
git pull origin main

echo "Stopper gammel server..."
sudo pkill gunicorn

echo "Starter serveren på nytt..."
sudo /home/mail_/projects/rk_depot/venv/bin/gunicorn --bind 0.0.0.0:80 --chdir /home/mail_/projects/rk_depot --workers 3 run:app -D

echo "Ferdig! Sjekk http://136.113.15.120"
