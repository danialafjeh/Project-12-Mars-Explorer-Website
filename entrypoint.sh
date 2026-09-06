#!/bin/sh

python manage.py migrate

if [ "$(python manage.py shell -c "from main.models import Mars; print(Mars.objects.exists())" | tail -n 1)" = "True" ]; then
    echo "Sample data already exists. Skipping loaddata."
else
    echo "Loading sample data..."
    python manage.py loaddata main/mars_data.json
fi

python manage.py runserver 0.0.0.0:8000
